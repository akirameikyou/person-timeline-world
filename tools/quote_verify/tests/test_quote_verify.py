import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quote_verify import fetch_page, find_saved_page, load_pages, markdown_report, normalize_url, normalize_text, parse_html, quote_state, read_input, run, same_page_redirect, split_fragments

REPO = Path(__file__).resolve().parents[3]
EXTERNAL = Path(r"C:\GitHub\person-timeline-world-work\experiment_candidate_extraction_001\verification")


class QuoteVerifyUnitTests(unittest.TestCase):
    def test_mediawiki_revision_ids_are_extracted_or_null(self):
        page = parse_html(b'''<html><script>mw.config.set({"wgRevisionId": 12345, "wgCurRevisionId": 67890, "wgPageName":"Example"});</script><body>text</body></html>''')
        self.assertEqual(page["page_revision"], 12345)
        self.assertEqual(page["current_revision"], 67890)
        plain = parse_html(b"<html><body>plain page</body></html>")
        self.assertIsNone(plain["page_revision"])
        self.assertIsNone(plain["current_revision"])

    def test_saved_pages_keep_mediawiki_revision_ids(self):
        with tempfile.TemporaryDirectory() as td:
            saved = Path(td) / "wiki.html"
            saved.write_text('''<html><head><link rel="canonical" href="https://en.wikipedia.org/wiki/Example"></head><script>mw.config.set({"wgRevisionId": 100, "wgCurRevisionId": 200});</script><body>text</body></html>''', encoding="utf-8")
            pages, inventory = load_pages(Path(td))
        page = pages[normalize_url("https://en.wikipedia.org/wiki/Example")]
        self.assertEqual((page["page_revision"], page["current_revision"]), (100, 200))
        self.assertEqual((inventory[0]["page_revision"], inventory[0]["current_revision"]), (100, 200))

    def test_oldid_checks_current_version_separately_and_preserves_primary_state(self):
        url = "https://en.wikipedia.org/w/index.php?title=Example_Person&oldid=123"
        quote = "This quotation appears only in the current revision of this article."
        record = {"id": "old", "agent": "test", "person": "Example Person", "url": url,
                  "quotes": [quote], "verification_claim": "checked"}
        old_page = {"text": "An earlier version without the quoted material.", "title": "Example Person - Wikipedia",
                    "url": url, "final_url": url, "page_revision": 123, "current_revision": 456}
        current_url = "https://en.wikipedia.org/w/index.php?title=Example_Person"
        current_page = {"text": quote, "title": "Example Person - Wikipedia", "url": current_url,
                        "final_url": current_url, "page_revision": 456, "current_revision": 456}
        with patch("quote_verify.fetch_page", side_effect=[(old_page, None), (current_page, None)]) as mocked:
            result = run([record], {}, fetch_missing=True)[0]
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(result["state"], "URL 不一致")
        self.assertIn("引用は指定の版になく、現在の版にある（版の申告と食い違い）", result["reason"])
        self.assertEqual(result["current_version_check"]["state"], "本文一致")
        self.assertEqual(result["page_revision"], 123)
        self.assertEqual(result["current_revision"], 456)
        self.assertIsNotNone(result["fetched_at"])

    def test_url_without_oldid_does_not_fetch_current_version(self):
        url = "https://en.wikipedia.org/w/index.php?title=Example_Person"
        record = {"id": "current", "agent": "test", "person": "Example Person", "url": url,
                  "quotes": ["the sentence"], "verification_claim": "checked"}
        page = {"text": "the sentence", "title": "Example Person - Wikipedia", "final_url": url}
        with patch("quote_verify.fetch_page", return_value=(page, None)) as mocked:
            result = run([record], {}, fetch_missing=True)[0]
        mocked.assert_called_once_with(url, 12.0, None)
        self.assertIsNone(result["current_version_check"])

    def test_accessed_at_is_reported_as_claim_and_does_not_affect_match(self):
        url = "https://example.org/page"
        record = {"id": "time", "agent": "test", "person": "p", "url": url,
                  "accessed_at": "2026-10-23T02:00:00+09:00", "quotes": ["the quoted sentence"],
                  "verification_claim": "checked"}
        page = {"text": "the quoted sentence", "title": "", "url": url}
        result = run([record], {normalize_url(url): page})[0]
        self.assertEqual(result["state"], "本文一致")
        self.assertEqual(result["accessed_at"], record["accessed_at"])
        self.assertIsNone(result["fetched_at"])
        report = markdown_report([result], [], "candidate-json")
        self.assertIn("申告の閲覧日時", report)
        self.assertIn(record["accessed_at"], report)

    def test_normalization_diacritics_punctuation_footnotes(self):
        self.assertEqual(normalize_text("Muḥammad [12] — Naṣīr-al-Dīn!"), "muhammad nasir al din")

    def test_normalization_preserves_japanese_voicing_marks(self):
        self.assertEqual(normalize_text("書道で"), "書道で")
        self.assertNotEqual(normalize_text("書道で"), normalize_text("書道て"))
        self.assertEqual(normalize_text("ば は ぱ"), "ば は ぱ")

    def test_ellipsis_splits_without_joining(self):
        self.assertEqual(split_fragments("alpha... beta … gamma"), ["alpha", "beta", "gamma"])

    def test_html_extraction_ignores_script(self):
        page = parse_html(b"<html><head><title>T</title></head><body>A <b>visible</b><script>hidden</script></body></html>")
        self.assertIn("A visible", page["text"])
        self.assertNotIn("hidden", page["text"])

    def test_numeric_year_change_is_not_near(self):
        pairs_file = EXTERNAL / "pairs.json"
        if pairs_file.is_file():
            records, _ = read_input(pairs_file)
            pages, _ = load_pages(EXTERNAL)
            source = next(r for r in records if r["agent"] == "M" and r["person"] == "Nzinga")
            page, basis = find_saved_page(source, pages)
            self.assertIsNotNone(page, "Nzinga saved page should be used when the fixture is available")
            self.assertEqual(basis, "canonical-url")
            original_quote = source["quotes"][0]
        else:
            original_quote = "The queen ruled these kingdoms from 1624 until 1663 across the region."
            page = parse_html(f"<html><body><p>{original_quote}</p></body></html>".encode("utf-8"))
        self.assertIn("1624", original_quote)
        changed_quote = original_quote.replace("1624", "1642", 1)
        record = {"id": "year-change", "agent": "test", "person": "Nzinga", "url": "https://example.org/source",
                  "quotes": [changed_quote], "verification_claim": "checked"}
        result = quote_state(record, page, None, False)
        self.assertEqual(result["state"], "URL 不一致")
        self.assertEqual(result["fragments"][0]["match"], "absent")
        self.assertEqual(result["fragments"][0]["reason"], "数字が一致しない")
        self.assertIn("数字が一致しない", result["reason"])

    def test_non_numeric_word_replacement_still_near(self):
        quote = "these kingdoms remained closely linked through many years of changing rule and trade across central regions"
        page = {"text": quote.replace("kingdoms", "zebra"), "title": "", "url": "https://example.org/a"}
        record = {"id": "word-change", "agent": "test", "person": "example", "url": page["url"],
                  "quotes": [quote], "verification_claim": "checked"}
        self.assertEqual(quote_state(record, page, None, False)["state"], "ほぼ一致")

    def test_numeric_quote_that_matches_exactly_is_body_match(self):
        quote = "the ruler governed the northern kingdom from 1624 until the final peace agreement"
        page = {"text": quote, "title": "", "url": "https://example.org/a"}
        record = {"id": "number-exact", "agent": "test", "person": "example", "url": page["url"],
                  "quotes": [quote], "verification_claim": "checked"}
        self.assertEqual(quote_state(record, page, None, False)["state"], "本文一致")
    def test_near_match_and_missing_fragment(self):
        quote = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen"
        page = {"text": "one two three four five six seven eight nine ten eleven twelve thirteen fifteen sixteen", "title": "", "url": "https://example.org/a"}
        record = {"id": "1", "agent": "a", "person": "p", "url": page["url"], "quotes": [quote], "verification_claim": "checked"}
        self.assertEqual(quote_state(record, page, None, False)["state"], "ほぼ一致")
        missing = dict(record, quotes=["a completely unrelated phrase missing from the target page"])
        self.assertEqual(quote_state(missing, page, None, False)["state"], "URL 不一致")

    def test_access_challenge_is_not_treated_as_missing_quote(self):
        page = {"text": "Please verify you are human before continuing", "title": "Security check", "url": "https://example.org/a"}
        record = {"id": "1", "agent": "a", "person": "p", "url": page["url"], "quotes": ["quote not present"], "verification_claim": "checked"}
        self.assertEqual(quote_state(record, page, None, False)["state"], "確認不能")
    def test_states_and_unverified_claim(self):
        page = {"text": "The exact cited sentence is present in this page.", "title": "", "url": "https://example.org/a"}
        exact = {"id": "1", "agent": "a", "person": "p", "url": page["url"], "quotes": ["THE exact cited sentence is present in this page [2]."], "verification_claim": "checked"}
        self.assertEqual(quote_state(exact, page, None, False)["state"], "本文一致")
        unchecked = dict(exact, verification_claim="not_checked")
        self.assertEqual(quote_state(unchecked, page, None, False)["state"], "未確認申告")
        self.assertEqual(quote_state(exact, None, None, False)["state"], "未照合")
        self.assertEqual(quote_state(exact, None, "HTTP 403", True)["state"], "確認不能")

    def test_different_redirect_target_is_unavailable_and_reports_final_url(self):
        requested = "https://museum.example/archives/leaflet/412/index.html"
        record = {"id": "redirect", "agent": "test", "person": "p", "url": requested,
                  "quotes": ["quote from the requested page"], "verification_claim": "checked"}
        fetched = {"title": "Maintenance notice", "text": "unrelated maintenance content",
                   "final_url": "https://museum.example/"}
        with patch("quote_verify.fetch_page", return_value=(fetched, None)):
            result = run([record], {}, fetch_missing=True)[0]
        self.assertEqual(result["state"], "確認不能")
        self.assertIn("https://museum.example/", result["reason"])
        self.assertEqual(result["page_match"], None)

    def test_same_page_redirect_variants_are_accepted(self):
        record = {"person": "Example Person"}
        page = {"title": "Example Person - Wikipedia"}
        self.assertTrue(same_page_redirect("http://example.org/page", "https://example.org/page/", record, page))
        self.assertTrue(same_page_redirect("https://en.wikipedia.org/wiki/Example-Person", "https://en.wikipedia.org/wiki/Example_Person", record, page))
        self.assertFalse(same_page_redirect("https://example.org/page", "https://example.org/", record, page))

    def test_ca_file_is_used_for_verified_https_fetch(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, size): return b"<html><body>quote</body></html>"
            def geturl(self): return "https://example.org/page"

        with patch("quote_verify.urlopen", return_value=Response()) as mocked, \
                patch("quote_verify.ssl.create_default_context", return_value=ssl.create_default_context()) as context_factory:
            page, reason = fetch_page("https://example.org/page", 3, r"C:\certs\ca-bundle.crt")
        self.assertIsNone(reason)
        self.assertEqual(page["final_url"], "https://example.org/page")
        context_factory.assert_called_once_with(cafile=r"C:\certs\ca-bundle.crt")
        self.assertEqual(mocked.call_args.kwargs["context"].verify_mode, ssl.CERT_REQUIRED)

    def test_invalid_percent_escape_skips_fetch_and_keeps_unverified_claim(self):
        bad_url = "https://ja.wikipedia.org/wiki/%E5%AE%AE%E5%B7%D%E9%95%B7%E6%98%A5"
        checked = {"id": "bad-url", "agent": "Gemini", "person": "宮川長春", "url": bad_url,
                   "quotes": ["quote"], "verification_claim": "checked"}
        unchecked = dict(checked, id="unchecked", verification_claim="not_checked")
        with patch("quote_verify.fetch_page") as mocked:
            checked_result, unchecked_result = run([checked, unchecked], {}, fetch_missing=True)
        mocked.assert_not_called()
        self.assertEqual(checked_result["state"], "未照合")
        self.assertIn("URL が不正", checked_result["reason"])
        self.assertEqual(unchecked_result["state"], "未確認申告")
        self.assertIn("URL が不正", unchecked_result["reason"])

    def test_legacy_pairs_are_read(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "pairs.json"
            p.write_text(json.dumps([["G", "Person", "https://example.org", ["quote"]]]), encoding="utf-8")
            records, fmt = read_input(p)
        self.assertEqual(fmt, "legacy-pairs")
        self.assertEqual(records[0]["person"], "Person")


@unittest.skipUnless(EXTERNAL.is_dir(), "external experiment fixture is not available")
class SavedFixtureRegression(unittest.TestCase):
    def test_saved_page_mapping_and_reported_results(self):
        pairs = EXTERNAL / "pairs.json"
        report = EXTERNAL / "QUOTE_VERIFICATION_001.md"
        self.assertTrue(pairs.is_file())
        self.assertTrue(report.is_file())
        records, _ = read_input(pairs)
        pages, inventory = load_pages(EXTERNAL)
        results = run(records, pages)
        mapped = [r for r in results if r["page_match"] is not None]
        unmapped = [r for r in results if r not in mapped]
        self.assertEqual(len(inventory), 9)
        self.assertEqual(len(mapped), 9)
        self.assertEqual(len(unmapped), 9)
        # S3 reports Yelü Chucai as a match; its Britannica page is one of the saved pages.
        yelu = next(r for r in results if r["agent"] == "G" and r["person"] == "耶律楚材")
        self.assertEqual(yelu["state"], "本文一致")
        # Eight matched Meta URLs have saved pages; their old report says all eight matched.
        saved_meta = [r for r in mapped if r["agent"] == "M"]
        self.assertEqual(len(saved_meta), 8)
        self.assertTrue(all(r["state"] == "本文一致" for r in saved_meta),
                        [(r["person"], r["state"], r["reason"]) for r in saved_meta])
        # M Rabban's page was browser-checked per S3 but is absent from the saved HTML set.
        rabban = next(r for r in results if r["agent"] == "M" and r["person"] == "Rabban Bar Sauma")
        self.assertEqual(rabban["state"], "未照合")
        self.assertNotIn("Rabban", [p["title"] for p in inventory])


if __name__ == "__main__":
    unittest.main()






