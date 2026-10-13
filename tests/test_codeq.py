import unittest

from jcoin_codeq import compile_codeq, verify_codeq


class CodeQTests(unittest.TestCase):
    def setUp(self):
        self.intent = {
            "id": "split-001",
            "amount": 101,
            "expires_at": 2000,
            "memo": "test split",
            "lanes": [
                {"id": "merchant", "to": "JC" + "1" * 40, "weight_bps": 9000},
                {"id": "roundup", "to": "JC" + "2" * 40, "weight_bps": 700},
                {"id": "community", "to": "JC" + "3" * 40, "weight_bps": 300},
            ],
        }

    def test_allocation_is_deterministic_and_conserves_amount(self):
        result = compile_codeq(self.intent, now=1000)
        reordered = dict(self.intent, lanes=list(reversed(self.intent["lanes"])))
        self.assertEqual(result, compile_codeq(reordered, now=1000))
        self.assertEqual(sum(item["amount"] for item in result["allocations"]), 101)
        self.assertEqual(result["conservation"], {"input": 101, "allocated": 101})
        self.assertTrue(verify_codeq(result, now=1000))

    def test_edited_allocation_fails_verification(self):
        result = compile_codeq(self.intent, now=1000)
        result["allocations"][0]["amount"] += 1
        self.assertFalse(verify_codeq(result, now=1000))

    def test_expired_or_duplicate_destination_intents_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "expired"):
            compile_codeq(dict(self.intent, expires_at=1000), now=1000)
        duplicate = dict(self.intent, lanes=[*self.intent["lanes"][:2],
                                             dict(self.intent["lanes"][2], to=self.intent["lanes"][0]["to"])])
        with self.assertRaisesRegex(ValueError, "unique recipient"):
            compile_codeq(duplicate, now=1000)


if __name__ == "__main__":
    unittest.main()
