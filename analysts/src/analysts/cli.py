from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from .config import build_config


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="analysts.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_config = subparsers.add_parser("show-config")
    show_config.add_argument("--base-dir", default=".")

    run_once = subparsers.add_parser("run-once")
    run_once.add_argument("--channel", required=True)
    run_once.add_argument("--base-dir", default=".")
    run_once.add_argument("--fixtures")

    return parser


def build_default_pipeline(*, base_dir: Path, fixtures_path: str | None = None):
    raise RuntimeError(
        "Default pipeline wiring depends on parser/router/agents lanes. "
        "Use tests to inject a pipeline or run from a merged checkout with those modules available."
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    base_dir = Path(args.base_dir)

    if args.command == "show-config":
        config = build_config(base_dir)
        payload = asdict(config)
        print(json.dumps(payload, indent=2, default=str, sort_keys=True))
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
                    f"wiki_pages={len(execution.wiki_pages)}",
                    f"signal_files={len(execution.signal_files)}",
                ]
            )
        )
        return 0

    parser.error(f"Unhandled command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
