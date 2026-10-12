import unittest
from resume_optimizer import match_resume_to_job, make_docx, make_pdf

class TestResumeOptimizer(unittest.TestCase):
    def test_keyword_match(self):
        result = match_resume_to_job(
            "Python developer with SQL and FastAPI experience.",
            "Required: Python, SQL, FastAPI, Docker", "Python Developer"
        )
        self.assertGreater(result["score"], 0)
        self.assertIn("python", result["matched_keywords"])

    def test_exports(self):
        self.assertTrue(make_docx("SUMMARY\nPython developer"))
        self.assertTrue(make_pdf("SUMMARY\nPython developer"))

if __name__ == "__main__":
    unittest.main()
