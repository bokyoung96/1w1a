from __future__ import annotations

from pathlib import Path


class GmailApiClient:
    def __init__(self, *, credentials_path: Path, token_path: Path) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path

    def ensure_authorized(self) -> None:  # pragma: no cover - live OAuth deferred
        raise NotImplementedError("Live Gmail OAuth is not implemented yet.")

    def list_message_ids(self, *, query: str, page_token: str | None = None, limit: int = 50) -> dict:  # pragma: no cover
        raise NotImplementedError("Live Gmail API listing is not implemented yet.")

    def get_message(self, *, message_id: str) -> dict:  # pragma: no cover
        raise NotImplementedError("Live Gmail API message fetch is not implemented yet.")
