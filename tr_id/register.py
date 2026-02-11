from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable
import time

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

    def _request(
        self,
        spec: TRSpec,
        symbol: str,
        access_token: str | None = None,
    ) -> TRResponse:
        access_token = access_token or self._auth.get_access_token()
        tr_id = self.config.tr_id.get(spec.name.value)
        if not tr_id:
            raise KeyError(f"Missing tr_id['{spec.name.value}'] in config.json")

        path = spec.path
        if not path:
            raise ValueError(f"Missing path for TR spec '{spec.name.value}'")
        if not path.startswith("/"):
            path = f"/{path}"

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


class TRBatchClient(TRClient):
    def call_batch(
        self,
        name: TRName | str,
        symbols: Iterable[str],
        *,
        concurrency: int = 5,
        batch_size: int = 50,
        retry: int = 1,
        delay_sec: float = 0.0,
    ) -> tuple[dict[str, TRResponse], dict[str, str]]:
        spec = self.registry.get(name)
        pending = list(symbols)
        results: dict[str, TRResponse] = {}
        errors: dict[str, str] = {}

        for attempt in range(retry + 1):
            if not pending:
                break

            access_token = self._auth.get_access_token()
            batch_errors: dict[str, str] = {}

            for batch in self._chunked(pending, batch_size):
                batch_results, batch_failures = self._call_batch(
                    spec, batch, access_token, concurrency
                )
                results.update(batch_results)
                batch_errors.update(batch_failures)

                if delay_sec > 0:
                    time.sleep(delay_sec)

            if not batch_errors or attempt == retry:
                errors.update(batch_errors)
                break

            pending = list(batch_errors.keys())

        return results, errors

    @staticmethod
    def _chunked(items: list[str], size: int) -> Iterable[list[str]]:
        if size <= 0:
            raise ValueError("batch_size must be positive")
        for idx in range(0, len(items), size):
            yield items[idx : idx + size]

    def _call_batch(
        self,
        spec: TRSpec,
        symbols: list[str],
        access_token: str,
        concurrency: int,
    ) -> tuple[dict[str, TRResponse], dict[str, str]]:
        if concurrency <= 0:
            raise ValueError("concurrency must be positive")

        results: dict[str, TRResponse] = {}
        errors: dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_map = {
                executor.submit(
                    self._request, spec, symbol, access_token
                ): symbol
                for symbol in symbols
            }
            for future in as_completed(future_map):
                symbol = future_map[future]
                try:
                    response = future.result()
                except Exception as exc:
                    errors[symbol] = str(exc)
                    continue

                if response.rt_cd == "0":
                    results[symbol] = response
                else:
                    errors[symbol] = f"{response.msg_cd} {response.msg1}"

        return results, errors
