from pathlib import Path

from analysts.config import build_config


def test_build_config_loads_gmail_settings(tmp_path: Path) -> None:
    (tmp_path / "config.local.json").write_text(
        """
        {
          "gmail": {
            "account_name": "reports-primary",
            "client_secret_path": "secrets/gmail-client.json",
            "token_path": "secrets/gmail-token.json",
            "query": "label:broker-reports newer_than:14d",
            "body_candidate_rules": {"min_chars": 800, "require_structure": true},
            "zip_allow_extensions": [".pdf", ".txt", ".html"],
            "poll_interval_seconds": 300
          }
        }
        """.strip()
    )

    config = build_config(tmp_path)

    assert config.gmail is not None
    assert config.gmail.account_name == "reports-primary"
    assert config.gmail.query == "label:broker-reports newer_than:14d"
    assert config.gmail.body_candidate_rules.min_chars == 800
    assert config.gmail.zip_allow_extensions == (".pdf", ".txt", ".html")
