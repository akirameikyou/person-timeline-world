# Quote Verify 001

Offline-first citation quote checker for the candidate-source workflow. It checks whether submitted quote fragments occur in the body extracted from a saved HTML page. It does **not** decide whether a quote supports its attached claim or whether a historical claim is true.

## Run against saved pages (offline)

From the repository root:

```powershell
python tools/quote_verify/quote_verify.py `
  C:\GitHub\person-timeline-world-work\experiment_candidate_extraction_001\verification\pairs.json `
  --pages-dir C:\GitHub\person-timeline-world-work\experiment_candidate_extraction_001\verification `
  --json-out quote-verification.json `
  --markdown-out quote-verification.md
```

The `pairs.json` legacy array format is accepted for the regression run. For new work, use the JSON object format shown below. No network requests are made by default. `--fetch-missing` explicitly permits one ordinary HTTP request per missing URL; access controls are not bypassed. HTTP 401/403, login/paywall blocks, fetch errors, and bot challenge pages must be treated as **確認不能** after a fetch attempt. If no saved file exists and fetching is disabled, the result is **未照合**.

Saved files are matched to a submitted URL using their `<link rel="canonical">`, `og:url`, or `twitter:url`. A page for another URL is not silently treated as the requested source, even if it contains similar text. One exception is labeled in the report: a unique English Wikipedia page whose slug is equivalent after punctuation normalization and whose title contains the candidate name is treated as an inferred same-site redirect alias; inspect `page_match` before treating that association as established.

## New input format

One citation/source URL per record; a person can have multiple records if they cite multiple pages. Keep the submitter's check claim distinct from this tool's result. See `candidate.schema.json` for validation.

```json
{
  "schema_version": "1.0",
  "records": [
    {
      "id": "R2-001-S1",
      "agent": "ExampleModel",
      "person": "Example person",
      "url": "https://example.org/biography",
      "source_title": "Page title",
      "publisher": "Publisher",
      "source_type": "museum page",
      "verification_claim": "checked",
      "quotes": ["A short direct quote... another separated fragment"],
      "claims": ["The specific claim this quote is offered to support."],
      "uncertainty": "Any stated caveat"
    }
  ]
}
```

Set `verification_claim` to `not_checked` when the submitter did not open the page and check the quote. For unknown or omitted legacy claims, the tool assumes `checked` so that old `pairs.json` is actually inspected; new submissions should set it explicitly.

## States

Results are per submitted record (one URL) and fragments are also reported individually.

- **本文一致**: every nonempty fragment occurs after the normalization below.
- **ほぼ一致**: no fragment is absent; at least one is accepted by the narrow token-similarity rule below. This is a mechanical review flag, not semantic approval.
- **URL 不一致**: a page for the supplied URL was read, but one or more fragments were not found. This does not by itself prove which alternate URL was intended. If a separate saved page is found to contain it, report that as additional evidence rather than silently swapping sources.
- **確認不能**: a fetch was attempted but the page could not be inspected (for example HTTP 403, network denial, or a challenge page).
- **未確認申告**: the submitter explicitly declared the URL/quote unverified. The tool does not promote that self-report to a match.
- **未照合**: no check ran (for example no matching saved page and fetching was not requested), or there was no usable quote.

Where several fragments exist, any absent fragment makes the record `URL 不一致`; otherwise a near fragment makes it `ほぼ一致`; otherwise all exact fragments make it `本文一致`. The result includes the reason and fragment-level observations.

## Normalization and “near” boundary

Exact matching applies these mechanical changes to both quote and extracted page text:

1. Unicode NFKD, lowercase/casefold, and remove combining diacritic marks.
2. Remove footnote tokens exactly matching `[n]` (digits, optional spaces).
3. Replace punctuation/symbols with spaces, then collapse whitespace.
4. If the quote contains `...` (3+ periods) or `…`, split at those markers and check each nonempty fragment independently. The tool does not assume omitted text between fragments.

The near rule is deliberately narrow and deterministic: only quotes with at least 12 word tokens are eligible; a matching window must have token similarity of at least 0.92 and no more than 8% changed tokens (minimum 1, maximum 8), with a four-token exact anchor. Any changed, inserted, or removed token containing an ASCII Arabic digit (`[0-9]`, including years) disqualifies a near match; that fragment is `absent` with the reason `数字が一致しない`. A number that matches exactly may still be part of a `本文一致` result. Other one-word substitutions can still be classified as `ほぼ一致`, even when the replacement changes meaning (for example, `kingdoms` → `zebra`). **Human review is mandatory for every `ほぼ一致` result**; similarity does not establish meaning or source support. Near results expose the similarity and matched token window. These thresholds are initial implementation choices, not an adopted research standard.

The HTML reader omits script/style/template/svg/noscript contents and extracts visible text from standard HTML. A small set of common human-verification and CAPTCHA indicators returns `確認不能` rather than a quote-missing result. It may not reproduce a browser's rendered text for dynamic pages. A missing quote in an incomplete extraction should be manually checked before interpreting it as a source mismatch.

## Offline regression

The repository does not include third-party saved pages. If the external verification directory exists, the regression test reads it in place and never copies or modifies it. Otherwise the fixture regression is skipped.

```powershell
python -m unittest discover -s tools/quote_verify/tests -v
```

The expected comparison follows `QUOTE_VERIFICATION_001.md`; the test separately reports pairs with no saved page, which cannot reproduce the prior browser-based judgment offline. A match to a prior judgment establishes reproducibility only, not correctness of the prior judgment.



