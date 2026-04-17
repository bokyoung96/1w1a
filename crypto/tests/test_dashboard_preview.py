from __future__ import annotations

import unittest

from crypto.dashboard import CryptoDashboardPreviewService


class CryptoDashboardPreviewTests(unittest.TestCase):
    def test_preview_builds_a_complete_crypto_dashboard_payload(self) -> None:
        payload = CryptoDashboardPreviewService().build()

        self.assertEqual(payload["summary"]["candidate_pool_size"], 40)
        self.assertEqual(payload["summary"]["family_cap"], 3)
        self.assertEqual(payload["summary"]["selected_basket_size"], 10)
        self.assertEqual(len(payload["registry"]), 10)
        self.assertEqual(len(payload["selected_basket"]), 10)
        self.assertEqual(len(payload["performance"]["equity_curve"]), 30)
        self.assertTrue(all(entry["documentation_path"].startswith("crypto/strategies/docs/") for entry in payload["registry"]))


if __name__ == "__main__":
    unittest.main()
