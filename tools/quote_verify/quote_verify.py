#!/usr/bin/env python3
"""Offline-first quote presence checker for candidate source citations."""
from __future__ import annotations

import argparse
import difflib
import html
from html.parser import HTMLParser
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit, urlunsplit
import ssl
from urllib.request import Request, urlopen

VERSION = "0.1.0"
ELLIPSIS_RE = re.compile(r"(?:\.{3,}|…+)")
FOOTNOTE_RE = re.compile(r"\[\s*\d+\s*\]")
WORD_RE = re.compile(r"\w+", re.UNICODE)
BLOCK_TAGS = {"address", "article", "blockquote", "br", "dd", "div", "dl", "dt", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "li", "ol", "p", "pre", "section", "table", "td", "th", "tr", "ul"}
SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}


class VisibleText(HTMLParser):
    """Extract readable text while ignoring executable and non-visible elements."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.canonical_urls: list[str] = []
        self.meta: dict[str, str] = {}
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in SKIP_TAGS:
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            if attrs.get("href"):
                self.canonical_urls.append(attrs["href"])
        if tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            if key and attrs.get("content"):
                self.meta[key.lower()] = attrs["content"]
        if not self._skip and tag in BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in SKIP_TAGS and self._skip:
            self._skip -= 1
        if not self._skip and tag in BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        if not self._skip:
            self.parts.append(data)


def parse_html(raw: bytes) -> dict:
    text = raw.decode("utf-8", errors="replace")
    parser = VisibleText()
    parser.feed(text)
    body = re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()
    canonical = parser.canonical_urls[0] if parser.canonical_urls else None
    page_url = canonical or parser.meta.get("og:url") or parser.meta.get("twitter:url")
    return {"text": body, "title": " ".join(parser.title_parts).strip(), "url": page_url}


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    p = urlsplit(url.strip())
    scheme = p.scheme.lower()
    host = (p.hostname or "").lower()
    port = p.port
    netloc = host if not port or (scheme == "https" and port == 443) or (scheme == "http" and port == 80) else f"{host}:{port}"
    path = unquote(p.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((scheme, netloc, path, p.query, ""))


def normalize_text(value: str) -> str:
    """S3-compatible conservative normalization for case, marks, punctuation and [n]."""
    value = FOOTNOTE_RE.sub(" ", value)
    value = unicodedata.normalize("NFKD", value.casefold())
    chars = []
    base = ""
    for ch in value:
        if unicodedata.combining(ch):
            # Remove Latin diacritics, but preserve marks used to distinguish kana.
            if base and unicodedata.name(base, "").startswith("LATIN "):
                continue
            chars.append(ch)
        else:
            chars.append(ch)
            if ch.isalpha():
                base = ch
            elif not ch.isspace():
                base = ""
    value = unicodedata.normalize("NFKC", "".join(chars))
    # Punctuation and symbols become separators, so words never concatenate.
    value = "".join(ch if ch.isalnum() or unicodedata.combining(ch) else " " for ch in value)
    return " ".join(value.split())


def split_fragments(quote: str) -> list[str]:
    return [part.strip() for part in ELLIPSIS_RE.split(quote) if part.strip()]


def _tokens(value: str) -> list[str]:
    return WORD_RE.findall(value)


def _near_match(query: str, body: str) -> tuple[bool, float, str | None, bool]:
    """Find a narrow similar token window, rejecting any changed Arabic-digit token."""
    q = _tokens(query)
    words = _tokens(body)
    if len(q) < 12 or len(words) < len(q) - 8:
        return False, 0.0, None, False
    max_change = min(8, max(1, int(len(q) * 0.08)))
    anchors = {}
    for i in range(max(0, len(words) - 3)):
        anchors.setdefault(tuple(words[i:i + 4]), []).append(i)
    candidate_starts = set()
    for qi in range(len(q) - 3):
        for wi in anchors.get(tuple(q[qi:qi + 4]), ()):
            candidate_starts.add(max(0, wi - qi))
    best = (0.0, None)
    numeric_difference = False
    for start in candidate_starts:
        for delta in range(-max_change, max_change + 1):
            left = max(0, start)
            size = max(1, len(q) + delta)
            window = words[left:left + size]
            if not window:
                continue
            matcher = difflib.SequenceMatcher(None, q, window, autojunk=False)
            ratio = matcher.ratio()
            edits = 0
            numeric_edit = False
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    continue
                edits += max(i2 - i1, j2 - j1)
                changed = q[i1:i2] + window[j1:j2]
                if any(re.search(r"[0-9]", token) for token in changed):
                    numeric_edit = True
            numeric_difference = numeric_difference or (ratio >= 0.92 and edits <= max_change and numeric_edit)
            if ratio > best[0]:
                best = (ratio, " ".join(window))
            if ratio >= 0.92 and edits <= max_change and not numeric_edit:
                return True, ratio, " ".join(window), False
    return False, best[0], best[1], numeric_difference


def load_pages(pages_dir: Path | None) -> tuple[dict[str, dict], list[dict]]:
    by_url: dict[str, dict] = {}
    inventory = []
    if not pages_dir:
        return by_url, inventory
    for file in sorted([*pages_dir.glob("*.html"), *pages_dir.glob("*.htm")]):
        page = parse_html(file.read_bytes())
        normalized = normalize_url(page.get("url"))
        item = {"file": str(file), "title": page["title"], "url": page.get("url"), "normalized_url": normalized, "text": page["text"]}
        inventory.append({k: v for k, v in item.items() if k != "text"})
        if normalized:
            by_url.setdefault(normalized, item)
    return by_url, inventory


def read_input(path: Path) -> tuple[list[dict], str]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list) and (not data or isinstance(data[0], list)):
        records = []
        for index, row in enumerate(data, 1):
            if len(row) != 4:
                raise ValueError(f"legacy pair #{index} must have [agent, person, url, quotes]")
            agent, person, url, quotes = row
            records.append({"id": f"legacy-{index:03d}", "agent": agent, "person": person, "url": url,
                            "quotes": quotes, "verification_claim": "checked"})
        return records, "legacy-pairs"
    if isinstance(data, dict):
        records = data.get("records")
    else:
        records = data
    if not isinstance(records, list):
        raise ValueError("input must be a JSON array or an object with a records array")
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            raise ValueError(f"record #{index} must be an object")
        for key in ("id", "agent", "person", "url", "quotes"):
            if key not in record:
                raise ValueError(f"record #{index} is missing required field {key!r}")
        if not isinstance(record["quotes"], list) or not all(isinstance(q, str) for q in record["quotes"]):
            raise ValueError(f"record #{index} quotes must be an array of strings")
    return records, "candidate-json"


INVALID_PERCENT_RE = re.compile(r"%(?![0-9a-fA-F]{2})")


def invalid_url_reason(url: str) -> str | None:
    if INVALID_PERCENT_RE.search(url):
        return "URL が不正: malformed percent escape"
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return "URL が不正: expected an absolute HTTP(S) URL"
        parsed.port
    except ValueError:
        return "URL が不正: malformed URL"
    return None


def fetch_page(url: str, timeout: float, ca_file: str | Path | None = None) -> tuple[dict | None, str | None]:
    try:
        request = Request(url, headers={"User-Agent": f"QuoteVerify/{VERSION} (standard single request; no access-control bypass)"})
        context = ssl.create_default_context(cafile=str(ca_file) if ca_file else None)
        with urlopen(request, timeout=timeout, context=context) as response:
            if response.status != 200:
                return None, f"HTTP {response.status}; page was not verified"
            body = response.read(8_000_001)
            if len(body) > 8_000_000:
                return None, "response exceeded 8 MB safety limit"
            page = parse_html(body)
            page["final_url"] = response.geturl()
            return page, None
    except HTTPError as exc:
        return None, f"HTTP {exc.code}; access restrictions are not bypassed"
    except (URLError, TimeoutError, OSError) as exc:
        return None, f"fetch failed: {type(exc).__name__}: {exc}"


def challenge_reason(page: dict) -> str | None:
    sample = (page.get("title", "") + " " + page.get("text", "")[:3000]).casefold()
    indicators = ("verify you are human", "checking your browser", "are you a robot", "automated access", "security check", "bot detection", "captcha", "enable javascript and cookies to continue")
    hit = next((marker for marker in indicators if marker in sample), None)
    return f"page appears to be an access challenge ({hit}); no bypass attempted" if hit else None


def quote_state(record: dict, page: dict | None, unavailable_reason: str | None, fetch_requested: bool) -> dict:
    claim = record.get("verification_claim", "checked")
    quotes = record.get("quotes", [])
    if claim in ("not_checked", "unverified", "未確認"):
        state = "未確認申告"
        return {"state": state, "reason": "submitter declared the citation unverified", "fragments": []}
    if not quotes:
        return {"state": "未照合", "reason": "record has no quote fragments", "fragments": []}
    if page is not None:
        challenge = challenge_reason(page)
        if challenge:
            return {"state": "確認不能", "reason": challenge, "fragments": []}
    if page is None:
        state = "確認不能" if unavailable_reason else "未照合"
        return {"state": state, "reason": unavailable_reason or "no saved page matched this URL; network fetching was not requested", "fragments": []}

    fragment_results = []
    for quote in quotes:
        pieces = split_fragments(quote)
        piece_results = []
        for piece in pieces:
            normalized = normalize_text(piece)
            if not normalized:
                continue
            if normalized in normalize_text(page["text"]):
                piece_results.append({"quote_fragment": piece, "normalized_summary": normalized[:180], "match": "exact", "matched_text": normalized[:180]})
            else:
                near, ratio, matched, numeric_mismatch = _near_match(normalized, normalize_text(page["text"]))
                fragment_result = {"quote_fragment": piece, "normalized_summary": normalized[:180],
                                   "match": "near" if near else "absent", "similarity": round(ratio, 3) if near else None,
                                   "matched_text": (matched or "")[:180] if near else None}
                if not near and numeric_mismatch:
                    fragment_result["reason"] = "数字が一致しない"
                piece_results.append(fragment_result)
        fragment_results.extend(piece_results)

    matches = [x["match"] for x in fragment_results]
    if not matches:
        state, reason = "未照合", "no non-empty fragments to check"
    elif "absent" in matches:
        state, reason = "URL 不一致", "one or more fragments were not found in the page at the supplied URL; origin mismatch is not asserted unless separately established"
        if any(x.get("reason") == "数字が一致しない" for x in fragment_results):
            reason += "; 数字が一致しない in one or more fragments"
    elif "near" in matches:
        state, reason = "ほぼ一致", "all fragments were found exactly or by the documented narrow token similarity rule"
    else:
        state, reason = "本文一致", "all quote fragments were found after documented normalization"
    return {"state": state, "reason": reason, "fragments": fragment_results}


def find_saved_page(record: dict, pages: dict[str, dict]) -> tuple[dict | None, str | None]:
    """Match canonical URLs exactly; allow a labeled same-Wikipedia slug redirect alias only when unique."""
    url = record.get("url", "")
    exact = pages.get(normalize_url(url))
    if exact is not None:
        return exact, "canonical-url"
    requested = urlsplit(url)
    if (requested.hostname or "").lower() not in {"en.wikipedia.org", "wikipedia.org"}:
        return None, None
    slug = unquote(requested.path.rsplit("/", 1)[-1])
    slug_key = normalize_text(slug)
    person_key = normalize_text(record.get("person", ""))
    aliases = []
    for page in pages.values():
        canonical = urlsplit(page.get("url") or "")
        canonical_slug = unquote(canonical.path.rsplit("/", 1)[-1])
        title_key = normalize_text(page.get("title", ""))
        if ((canonical.hostname or "").lower() in {"en.wikipedia.org", "wikipedia.org"}
                and normalize_text(canonical_slug) == slug_key
                and person_key and person_key in title_key):
            aliases.append(page)
    if len(aliases) == 1:
        return aliases[0], "inferred-same-wikipedia-slug-and-title"
    return None, None


def same_page_redirect(requested_url: str, final_url: str, record: dict, page: dict) -> bool:
    """Accept URL spelling changes that still identify the requested page."""
    requested_parts, final_parts = urlsplit(requested_url), urlsplit(final_url)
    if requested_parts.scheme.lower() not in {"http", "https"} or final_parts.scheme.lower() not in {"http", "https"}:
        return False
    requested_https = normalize_url(urlunsplit(("https", *requested_parts[1:])))
    final_https = normalize_url(urlunsplit(("https", *final_parts[1:])))
    if requested_https == final_https:
        return True
    requested, final = requested_parts, final_parts
    wiki_hosts = {"en.wikipedia.org", "www.en.wikipedia.org", "en.m.wikipedia.org"}
    if (requested.hostname or "").lower() in wiki_hosts and (final.hostname or "").lower() in wiki_hosts:
        requested_slug = unquote(requested.path.rsplit("/", 1)[-1])
        final_slug = unquote(final.path.rsplit("/", 1)[-1])
        person_key = normalize_text(record.get("person", ""))
        title_key = normalize_text(page.get("title", ""))
        return bool(person_key and person_key in title_key and normalize_text(requested_slug) == normalize_text(final_slug))
    return False


def run(records: list[dict], pages: dict[str, dict], *, fetch_missing=False, timeout=12.0, ca_file: str | Path | None = None) -> list[dict]:
    results = []
    for record in records:
        url = record.get("url", "")
        bad_url = invalid_url_reason(url)
        claim = record.get("verification_claim", "checked")
        if bad_url:
            if claim in ("not_checked", "unverified", "未確認"):
                result = quote_state(record, None, None, fetch_missing)
                result["reason"] += f"; {bad_url}"
            else:
                result = {"state": "未照合", "reason": bad_url, "fragments": []}
            results.append({"id": record.get("id"), "agent": record.get("agent"), "person": record.get("person"),
                            "url": url, "page_match": None, **result})
            continue
        page, page_match = find_saved_page(record, pages)
        reason = None
        if page is None and fetch_missing and url:
            page, reason = fetch_page(url, timeout, ca_file)
            if page is not None:
                final_url = page.get("final_url", url)
                if not same_page_redirect(url, final_url, record, page):
                    reason = f"redirected to a different page; final URL: {final_url}"
                    page = None
                else:
                    page_match = "fetched-url"
        result = quote_state(record, page, reason, fetch_missing)
        results.append({"id": record.get("id"), "agent": record.get("agent"), "person": record.get("person"),
                        "url": url, "page_match": page_match, **result})
    return results


def markdown_report(results: list[dict], inventory: list[dict], input_format: str) -> str:
    lines = ["# Quote verification report", "", f"- Tool version: `{VERSION}`", f"- Input format: `{input_format}`", "- Network fetching: disabled unless explicitly requested", "",
             "## Results", "", "| ID | Agent | Candidate | URL | State | Reason |", "|---|---|---|---|---|---|"]
    for r in results:
        safe = lambda value: str(value or "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {safe(r['id'])} | {safe(r['agent'])} | {safe(r['person'])} | {safe(r['url'])} | {safe(r['state'])} | {safe(r['reason'])} |")
    lines.extend(["", "## Fragment details", ""])
    for r in results:
        lines.append(f"### {r['id']} — {r['person']} ({r['state']})")
        if not r["fragments"]:
            lines.append(f"- {r['reason']}")
        for f in r["fragments"]:
            lines.append(f"- `{f['match']}` quote: {f['quote_fragment']}")
            if f.get("reason"):
                lines.append(f"  - note: {f['reason']}")
            lines.append(f"  - normalized: `{f['normalized_summary']}`")
            if f.get("matched_text"):
                lines.append(f"  - matched text: `{f['matched_text']}`")
        lines.append("")
    lines.extend(["## Saved page inventory", "", "| File | Canonical URL | Title |", "|---|---|---|"])
    for p in inventory:
        lines.append(f"| `{p['file']}` | {p.get('url') or ''} | {(p.get('title') or '').replace('|', '\\|')} |")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="candidate JSON object, or legacy pairs.json")
    parser.add_argument("--pages-dir", type=Path, help="directory of saved .html/.htm pages")
    parser.add_argument("--json-out", type=Path, help="write machine-readable report")
    parser.add_argument("--markdown-out", type=Path, help="write human-readable report")
    parser.add_argument("--fetch-missing", action="store_true", help="make one ordinary HTTP request for URLs without a matching saved page; never bypass access controls")
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument("--ca-file", type=Path, help="CA bundle file for HTTPS certificate verification (verification remains enabled)")
    args = parser.parse_args(argv)
    try:
        records, input_format = read_input(args.input)
        pages, inventory = load_pages(args.pages_dir)
        results = run(records, pages, fetch_missing=args.fetch_missing, timeout=args.timeout, ca_file=args.ca_file)
        payload = {"tool_version": VERSION, "input_format": input_format, "fetch_missing": args.fetch_missing,
                   "saved_pages": inventory, "results": results}
        json_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        md_text = markdown_report(results, inventory, input_format)
        if args.json_out:
            args.json_out.write_text(json_text, encoding="utf-8")
        if args.markdown_out:
            args.markdown_out.write_text(md_text, encoding="utf-8")
        if not args.json_out and not args.markdown_out:
            sys.stdout.buffer.write(json_text.encode("utf-8"))
        counts = {}
        for item in results:
            counts[item["state"]] = counts.get(item["state"], 0) + 1
        print("Summary:", json.dumps(counts, ensure_ascii=True, sort_keys=True), file=sys.stderr)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"quote_verify: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())





