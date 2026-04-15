from __future__ import annotations

import asyncio
import argparse
import json
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Sequence

from .config import build_config
from .fetcher import TelegramFetcher
from .graphify import GraphifyCorpusBuilder
from .pipeline import ArasPipeline
from .raw_reports import RawReportCatalog
from .storage import SqliteArasStore
from .watcher import WatchUntilRunner


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

    summarize_recent = subparsers.add_parser("summarize-recent")
    summarize_recent.add_argument("--channel", required=True)
    summarize_recent.add_argument("--limit", type=int, default=10)
    summarize_recent.add_argument("--base-dir", default=".")

    watch_until = subparsers.add_parser("watch-until")
    watch_until.add_argument("--channel", required=True)
    watch_until.add_argument("--until", required=True)
    watch_until.add_argument("--base-dir", default=".")

    graphify_update = subparsers.add_parser("graphify-update")
    graphify_update.add_argument("--base-dir", default=".")

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


def build_watch_runner(*, base_dir: Path) -> WatchUntilRunner:
    config = build_config(base_dir)
    store = SqliteArasStore(config.paths.state_db)
    telethon_module = import_module("analysts.telethon_client")
    client = telethon_module.TelethonChannelClient(base_dir=base_dir, config=config)
    pipeline = ArasPipeline(client=client, store=store, config=config)
    fetcher = TelegramFetcher(client=client, store=store, config=config)
    return WatchUntilRunner(client=client, message_ingestor=fetcher, pipeline=pipeline)


def parse_watch_deadline(until: str) -> datetime:
    return datetime.fromisoformat(until)


def print_watch_summary(*, result) -> None:
    print(
        " ".join(
            [
                f"downloaded={result.downloaded}",
                f"duplicates={result.duplicates}",
                f"ignored={result.ignored}",
                f"summarized={result.summarized}",
                f"retries={result.summarize_retries}",
            ]
        )
    )


def run_watch_until(*, base_dir: Path, channel: str, until: str) -> int:
    result = asyncio.run(build_watch_runner(base_dir=base_dir).watch_until(channel=channel, until=parse_watch_deadline(until)))
    print_watch_summary(result=result)
    return 0


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

    if args.command == "watch-until":
        return run_watch_until(base_dir=base_dir, channel=args.channel, until=args.until)

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


    if args.command == "graphify-update":
        config = build_config(base_dir)
        result = GraphifyCorpusBuilder(config).update()
        print(
            " ".join(
                [
                    f"reports={result.report_count}",
                    f"manifest={result.manifest_path}",
                    f"graphify_invoked={str(result.graphify_invoked).lower()}",
                ]
            )
        )
        return 0

    if args.command == "summarize-recent":
        pipeline = build_default_pipeline(base_dir=base_dir)
        reports = [report for report in pipeline.store.list_reports() if report.channel == args.channel]
        if not reports:
            reports = RawReportCatalog(raw_dir=pipeline.config.paths.raw_dir, channel=args.channel).recent_reports(args.limit)
        else:
            reports = reports[-args.limit:]
        total_processed = 0
        total_summaries = 0
        for report in reports:
            execution = pipeline.summarize_report(report)
            total_processed += len(execution.processed_files)
            total_summaries += len(execution.summaries)
        print(
            " ".join(
                [
                    f"reports={len(reports)}",
                    f"processed_files={total_processed}",
                    f"summaries={total_summaries}",
                ]
            )
        )
        return 0

    parser.error(f"Unhandled command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
