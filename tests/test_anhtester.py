"""Regression test: the audit must reproduce the findings from the manual trace of
anhtester/AutomationFrameworkCucumberTestNG.

Set QA_TOOL_FIXTURE to a clone of that repository (any recent commit) to run it.
"""
import os
import unittest
from pathlib import Path

from qa_tool.audit import audit

FIXTURE = os.environ.get("QA_TOOL_FIXTURE")


@unittest.skipUnless(FIXTURE, "set QA_TOOL_FIXTURE to a clone of anhtester/AutomationFrameworkCucumberTestNG")
class ManualTraceFindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings = audit(Path(FIXTURE)).findings

    def find(self, code, needle):
        hits = [f for f in self.findings if f.code == code and needle in f.title]
        self.assertTrue(hits, f"missing {code} for {needle!r}; got {[(f.code, f.title) for f in self.findings]}")
        return hits[0]

    def test_1_invalid_signin_then_checks_wrong_thing_real_check_hidden_in_when(self):
        f = self.find("INTENT_MISMATCH", "The user can not redirect to Dashboard page")
        self.assertEqual(f.severity, "medium")
        self.assertIn("email-error", " ".join(f.detail))
        self.assertIn("verifySignInFail", " ".join(f.detail))

    def test_2_url_from_examples_is_ignored(self):
        f = self.find("DISABLED_STEP", "User navigate to url")
        self.assertIn("`url`", " ".join(f.detail))

    def test_3_click_login_button_is_empty(self):
        self.find("EMPTY_STEP", "click Login button")

    def test_4_navigate_to_dashboard_only_checks(self):
        self.find("CHECK_ONLY_ACTION_STEP", "User navigate to dashboard")

    def test_5_unused_page_objects(self):
        orphans = {f.title.split("`")[1] for f in self.findings if f.code == "ORPHAN_PAGE_OBJECT"}
        self.assertEqual(orphans, {"ClientPageCRM", "ProjectPageCRM"})

    def test_6_latent_soft_assert_risk(self):
        f = self.find("SOFT_ASSERT_RISK", "Soft assertions")
        self.assertEqual(f.severity, "low")   # latent: only the unused ClientPageCRM uses it
        self.assertIn("after the scenario's status is read", " ".join(f.detail))

    def test_7_reused_failure_message(self):
        self.find("REUSED_FAILURE_MESSAGE", "The Dashboard page not display.")

    def test_no_false_alarms(self):
        # The WebUI.verify* helpers fail properly (AssertionError escapes catch (Exception)),
        # and every step has exactly one definition.
        codes = {f.code for f in self.findings}
        self.assertNotIn("HOLLOW_THEN", codes)
        self.assertNotIn("UNDEFINED_STEP", codes)
        self.assertNotIn("AMBIGUOUS_STEP", codes)


if __name__ == "__main__":
    unittest.main()
