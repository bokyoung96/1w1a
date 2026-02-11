from __future__ import annotations

from typing import Dict

import httpx

from config import KISAuth, KISConfig, setup_logging
from root import ROOT
from tr_id.protocol import TRName, TRResponse, TRSpec
from tr_id.bid_ask_list import BidAskListSpec


class TRRegistry:
    def __init__(self) -> None:
        self._specs: Dict[TRName, TRSpec] = {}

    def register(self, spec: TRSpec) -> None:
        name = spec.name
        if name in self._specs:
            raise ValueError(f"TR already registered: {name.value}")
        self._specs[name] = spec

    def get(self, name: TRName | str) -> TRSpec:
        key = self._coerce_name(name)
        try:
            return self._specs[key]
        except KeyError as exc:
            available = ", ".join(n.value for n in self._specs) or "<none>"
            raise KeyError(f"Unknown TR '{key.value}'. Available: {available}") from exc

    def all(self) -> tuple[TRSpec, ...]:
        return tuple(self._specs.values())

    @staticmethod
    def _coerce_name(name: TRName | str) -> TRName:
        if isinstance(name, TRName):
            return name
        try:
            return TRName(name)
        except ValueError:
            if name in TRName.__members__:
                return TRName[name]
            raise


TR_REGISTRY = TRRegistry()
TR_REGISTRY.register(BidAskListSpec())


class TRClient:
    def __init__(
        self,
        config_path: str | None = None,
        *,
        registry: TRRegistry | None = None,
        timeout: float = 10.0,
    ) -> None:
        config_path = config_path or ROOT.config_path_str
        self.config = KISConfig(config_path)
        setup_logging(self.config.config_dir)

        self.registry = registry or TR_REGISTRY
        self._client = httpx.Client(timeout=timeout)
        self._auth = KISAuth(self.config, self._client)

    def call(self, name: TRName | str, symbol: str) -> TRResponse:
        spec = self.registry.get(name)
        return self._request(spec, symbol)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "TRClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _request(self, spec: TRSpec, symbol: str) -> TRResponse:
        tr_id = self.config.tr_id.get(spec.name.value)
        if not tr_id:
            raise KeyError(f"Missing tr_id['{spec.name.value}'] in config.json")

        path = spec.path
        if not path:
            raise ValueError(f"Missing path for TR spec '{spec.name.value}'")
        if not path.startswith("/"):
            path = f"/{path}"

        access_token = self._auth.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "appKey": self.config.app_key,
            "appSecret": self.config.app_secret,
            "tr_id": tr_id,
        }
        params = dict(spec.params(symbol))

        url = f"{self.config.base_url}{path}"
        response = self._client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return spec.parse(response)
