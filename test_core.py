import unittest
from core import (
    parse,
    match_schemes,
    doc_checklist,
    SCHEMES,
    full_report,
    prefill,
)


class TestHaqdaarCore(unittest.TestCase):

    def setUp(self):
        self.student = parse(
            "I am a 20 years student from Uttar Pradesh, OBC, "
            "family income 1.2 lakh, female",
            {},
        )

    def test_student_profile_parsing(self):
        self.assertEqual(self.student["state"], "Uttar Pradesh")
        self.assertEqual(self.student["income"], 120000)
        self.assertEqual(self.student["age"], 20)
        self.assertEqual(self.student["category"], "OBC")
        self.assertEqual(self.student["gender"], "female")

    def test_student_scheme_matching(self):
        ids = [s["id"] for s in match_schemes(self.student)]
        self.assertIn("nsp-post-matric-obc", ids)
        self.assertIn("up-scholarship", ids)
        self.assertNotIn("pm-kisan", ids)

    def test_document_checklist(self):
        scheme = next(
            s for s in SCHEMES
            if s["id"] == "nsp-post-matric-obc"
        )
        result = doc_checklist(scheme, ["Aadhaar", "bank passbook"])
        self.assertIn("Income certificate", result["missing"])

    def test_farmer_scheme_matching(self):
        farmer = parse(
            "farmer, Bihar, 40 years, SC, income 80000",
            {},
        )
        ids = [s["id"] for s in match_schemes(farmer)]
        self.assertIn("pm-kisan", ids)

    def test_prefilled_form_uses_correct_age(self):
        schemes = match_schemes(self.student)
        self.assertTrue(schemes)
        form = prefill(schemes[0], self.student)
        self.assertEqual(form["Age"], 20)

    def test_report_contains_scheme_results(self):
        report = full_report(self.student, ["Aadhaar"])
        self.assertIn("Found ", report)
        self.assertIn("Apply:", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
