import json
from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quote_verify import find_saved_page, load_pages, normalize_text, parse_html, quote_state, read_input, run, split_fragments

REPO = Path(__file__).resolve().parents[3]
EXTERNAL = Path(r"C:\GitHub\person-timeline-world-work\experiment_candidate_extraction_001\verification")


class QuoteVerifyUnitTests(unittest.TestCase):
    def test_normalization_diacritics_punctuation_footnotes(self):
        self.assertEqual(normalize_text("Muḥammad [12] — Naṣīr-al-Dīn!"), "muhammad nasir al din")

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






