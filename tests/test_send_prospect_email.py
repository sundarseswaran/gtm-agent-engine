import unittest
from types import SimpleNamespace

from gtm_agent.data_service import get_prospect_record
from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTest(unittest.TestCase):
    runtime = SimpleNamespace(config={"metadata": {"user_id": "rep_amills"}})

    def test_missing_or_unknown_prospect_id_does_not_send(self):
        for prospect_id in ("", "LEAD-40404"):
            result = send_prospect_email.func(
                prospect_id,
                "Follow-up",
                "Hello",
                self.runtime,
            )

            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["prospect_id"], prospect_id)
            self.assertNotIn("message_id", result)

    def test_disqualified_prospects_are_blocked_without_confirmation(self):
        for prospect_id in ("LEAD-50001", "LEAD-50002", "LEAD-50003", "LEAD-50004", "LEAD-50005"):
            result = send_prospect_email.func(
                prospect_id,
                "Follow-up",
                "Hello",
                self.runtime,
            )

            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["prospect_id"], prospect_id)
            self.assertEqual(result["to"], get_prospect_record(prospect_id)["email"])
            self.assertNotIn("message_id", result)

    def test_non_disqualified_prospect_is_sent_using_authoritative_contact(self):
        result = send_prospect_email.func(
            "LEAD-12853",
            "Follow-up",
            "Hello",
            self.runtime,
            from_rep={"email": "rep@example.com", "name": "Rep"},
        )

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["to"], get_prospect_record("LEAD-12853")["email"])
        self.assertEqual(result["to_name"], get_prospect_record("LEAD-12853")["name"])

    def test_disqualified_prospect_can_be_sent_after_confirmation(self):
        result = send_prospect_email.func(
            "LEAD-50001",
            "Follow-up",
            "Hello",
            self.runtime,
            confirmed_by_rep=True,
        )

        self.assertEqual(result["status"], "sent")


if __name__ == "__main__":
    unittest.main()
