from __future__ import annotations

import argparse
import json
from importlib import import_module
from pathlib import Path
from typing import Sequence

from .config import build_config
from .pipeline import ArasPipeline
from .storage import SqliteArasStore


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="analysts.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_config = subparsers.add_parser("show-config")
    show_config.add_argument("--base-dir", default=".")

    auth = subparsers.add_parser("auth-login")
    auth.add_argument("--base-dir", default=".")

    run_once = subparsers.add_parser("run-once")
    run_once.add_argument("--channel", required=True)
    run_once.add_argument("--base-dir", default=".")
    run_once.add_argument("--fixtures")

    summarize_latest = subparsers.add_parser("summarize-latest")
    summarize_latest.add_argument("--channel", required=True)
    summarize_latest.add_argument("--base-dir", default=".")

    return parser


def build_default_pipeline(*, base_dir: Path, fixtures_path: str | None = None) -> ArasPipeline:
    config = build_config(base_dir)
    store = SqliteArasStore(config.paths.state_db)
    telethon_module = import_module("analysts.telethon_client")
    if fixtures_path:
        client = telethon_module.FixtureTelegramClient.from_fixture_path(Path(fixtures_path))
        return ArasPipeline(client=client, store=store, config=config)
    client = telethon_module.TelethonChannelClient(base_dir=base_dir, config=config)
    return ArasPipeline(client=client, store=store, config=config)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    base_dir = Path(args.base_dir)

    if args.command == "show-config":
        config = build_config(base_dir)
        payload = config.to_display_dict()
        print(json.dumps(payload, indent=2, default=str, sort_keys=True))
        return 0

    if args.command == "auth-login":
        config = build_config(base_dir)
        telethon_module = import_module("analysts.telethon_client")
        telethon_module.auth_login(base_dir=base_dir, config=config)
        return 0

    if args.command == "run-once":
        pipeline = build_default_pipeline(base_dir=base_dir, fixtures_path=args.fixtures)
        execution = pipeline.run_once(channel=args.channel)
        print(
            " ".join(
                [
                    f"downloaded={execution.summary.downloaded}",
                    f"duplicates={execution.summary.duplicates}",
                    f"ignored={execution.summary.ignored}",
                    f"next_offset={execution.summary.next_offset}",
                    f"processed_files={len(execution.processed_files)}",
                    f"summaries={len(execution.summaries)}",
                ]
            )
        )
        return 0

    if args.command == "summarize-latest":
        pipeline = build_default_pipeline(base_dir=base_dir)
        execution = pipeline.summarize_latest(channel=args.channel)
        print(
            " ".join(
                [
                    f"processed_files={len(execution.processed_files)}",
                    f"summaries={len(execution.summaries)}",
                    f"message_id={execution.summary.next_offset}",
                ]
            )
        )
        return 0

    parser.error(f"Unhandled command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
