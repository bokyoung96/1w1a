#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "graphify-out"
LOG = OUT / "run.log"

# Use source checkouts instead of pip-installed packages.
sys.path.insert(0, "/tmp/networkx-src")
sys.path.insert(0, "/tmp/graphify-src")

import networkx as nx

from graphify.analyze import god_nodes, suggest_questions, surprising_connections
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.export import to_cypher, to_html, to_obsidian, to_json, to_svg
from graphify.report import generate
from graphify.wiki import to_wiki


SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    ".worktrees",
    ".superpowers",
    "dist",
    "build",
    "site",
    "parquet",
    "results",
    "graphify-out",
}

CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx"}
DOC_EXTS = {".md", ".txt", ".rst"}
DATA_EXTS = {".csv", ".xlsx", ".xls"}

STOPWORDS = {
    "and",
    "the",
    "for",
    "with",
    "from",
    "into",
    "plan",
    "design",
    "implementation",
    "report",
    "dashboard",
    "backtesting",
    "stock",
    "series",
    "data",
    "raw",
    "file",
    "files",
    "spec",
    "specs",
}

RAW_TOKEN_MAP = {
    "adj": "adjusted",
    "c": "close",
    "o": "open",
    "h": "high",
    "l": "low",
    "v": "volume",
    "mktcap": "market cap",
    "flt": "free float",
    "ocf": "operating cash flow",
    "gp": "gross profit",
    "ni": "net income",
    "op": "operating profit",
    "asset": "assets",
    "liability": "liabilities",
    "equity": "equity",
    "sha": "shares outstanding",
    "out": "outstanding",
    "wics": "WICS sector",
    "sec": "sector",
    "big": "large cap sector",
    "foreign": "foreign ownership",
    "institution": "institutional trading",
    "retail": "retail trading",
    "ratio": "ratio",
    "k200": "KOSPI200",
    "ksdq": "KOSDAQ",
    "yn": "membership flag",
    "bm": "benchmark",
    "eps": "earnings per share",
    "nfq1": "next quarter",
    "nfq2": "following quarter",
    "nfy1": "next fiscal year",
    "lfq0": "latest quarter",
    "trs": "trading restriction",
    "ban": "ban list",
    "options": "options data",
}


def _normalize_ticker(value: object) -> str:
    raw = str(value).strip().upper()
    if not raw:
        return raw
    if raw.startswith("A"):
        return raw
    if raw.isdigit():
        return f"A{raw.zfill(6)}"
    return raw


def _ticker_code(value: object) -> str:
    ticker = _normalize_ticker(value)
    return ticker[1:] if ticker.startswith("A") else ticker


def materialize_raw_reference_docs(raw_dir: Path) -> list[Path]:
    generated: list[Path] = []
    generated.extend(_materialize_map_reference_docs(raw_dir))
    generated.extend(_materialize_gics_reference_docs(raw_dir))
    return generated


def _materialize_map_reference_docs(raw_dir: Path) -> list[Path]:
    path = raw_dir / "map.xlsx"
    if not path.exists():
        return []

    workbook = pd.ExcelFile(path)
    generated: list[Path] = []

    sector_frames = []
    ticker_frames = []
    for sheet_name in workbook.sheet_names:
        frame = workbook.parse(sheet_name)
        columns = {str(column).strip().lower(): column for column in frame.columns}
        if {"code", "name"} <= set(columns):
            sector_frames.append(frame.loc[:, [columns["code"], columns["name"]]].dropna())
        if {"ticker", "name"} <= set(columns):
            ticker_frames.append(frame.loc[:, [columns["ticker"], columns["name"]]].dropna())

    if sector_frames:
        sector_pairs = pd.concat(sector_frames, ignore_index=True).drop_duplicates().sort_values(by=["Code", "Name"])
        sector_pairs.columns = ["Code", "Name"]
        sector_path = raw_dir / "map_sector_codes.md"
        lines = [
            "# Map Sector Codes",
            "",
            "> Source: `raw/map.xlsx` sheet `sector_map`",
            "",
            "Korean sector code to sector name mapping used by the dataset layer and reporting references.",
            "",
            "| Sector Code | Sector Name |",
            "| --- | --- |",
        ]
        for _, row in sector_pairs.iterrows():
            lines.append(f"| `{str(row['Code']).strip()}` | {str(row['Name']).strip()} |")
        lines.extend(["", f"Total mappings: **{len(sector_pairs)}**", ""])
        sector_path.write_text("\n".join(lines), encoding="utf-8")
        generated.append(sector_path)

    if ticker_frames:
        ticker_pairs = pd.concat(ticker_frames, ignore_index=True).drop_duplicates()
        ticker_pairs.columns = ["Ticker", "Name"]
        ticker_pairs["Ticker"] = ticker_pairs["Ticker"].map(_normalize_ticker)
        ticker_pairs["Code"] = ticker_pairs["Ticker"].map(_ticker_code)
        ticker_pairs = ticker_pairs.sort_values(by=["Ticker", "Name"]).loc[:, ["Ticker", "Code", "Name"]]

        ticker_path = raw_dir / "map_ticker_name_index.md"
        lines = [
            "# Map Ticker Name Index",
            "",
            "> Source: `raw/map.xlsx` sheet `Sheet3`",
            "",
            "Ticker to six-digit code to Korean company name mapping for lookup-oriented LLM use.",
            "",
            "| Ticker | Code | Name |",
            "| --- | --- | --- |",
        ]
        for _, row in ticker_pairs.iterrows():
            lines.append(
                f"| `{str(row['Ticker']).strip()}` | `{str(row['Code']).strip()}` | {str(row['Name']).strip()} |"
            )
        lines.extend(["", f"Total mappings: **{len(ticker_pairs)}**", ""])
        ticker_path.write_text("\n".join(lines), encoding="utf-8")
        generated.append(ticker_path)

    return generated


def _materialize_gics_reference_docs(raw_dir: Path) -> list[Path]:
    gics_path = raw_dir / "snp_ksdq_gics_sector_big.xlsx"
    if not gics_path.exists():
        return []

    frame = pd.read_excel(gics_path)
    frame = frame.rename(columns={str(column).strip(): str(column).strip() for column in frame.columns})
    required = {"DATE", "TICKER", "GICS_SECTOR_NAME"}
    if not required <= set(frame.columns):
        return []

    mappings = frame.loc[:, ["DATE", "TICKER", "GICS_SECTOR_NAME"]].dropna().copy()
    mappings["DATE"] = pd.to_datetime(mappings["DATE"]).dt.normalize()
    mappings["TICKER"] = mappings["TICKER"].map(_normalize_ticker)
    mappings["CODE"] = mappings["TICKER"].map(_ticker_code)
    mappings["GICS_SECTOR_NAME"] = mappings["GICS_SECTOR_NAME"].astype(str).str.strip()
    mappings = mappings.drop_duplicates(subset=["DATE", "TICKER"], keep="last").sort_values(["DATE", "TICKER"])

    pivot = mappings.pivot(index="DATE", columns="TICKER", values="GICS_SECTOR_NAME").sort_index().sort_index(axis=1)
    pivot.index.name = "date"
    pivot.columns.name = None
    pivot_path = raw_dir / "snp_ksdq_gics_sector_big_pivot.csv"
    pivot.to_csv(pivot_path, encoding="utf-8")

    stock_name_map: dict[str, str] = {}
    map_xlsx = raw_dir / "map.xlsx"
    if map_xlsx.exists():
        workbook = pd.ExcelFile(map_xlsx)
        for sheet_name in workbook.sheet_names:
            sheet = workbook.parse(sheet_name)
            columns = {str(column).strip().lower(): column for column in sheet.columns}
            if {"ticker", "name"} <= set(columns):
                pairs = sheet.loc[:, [columns["ticker"], columns["name"]]].dropna()
                for _, row in pairs.iterrows():
                    stock_name_map[_normalize_ticker(row.iloc[0])] = str(row.iloc[1]).strip()

    latest_date = pd.Timestamp(mappings["DATE"].max())
    latest = mappings.loc[mappings["DATE"].eq(latest_date), ["TICKER", "CODE", "GICS_SECTOR_NAME"]].copy()
    latest["Name"] = latest["TICKER"].map(lambda ticker: stock_name_map.get(str(ticker), ""))
    latest = latest.sort_values(["GICS_SECTOR_NAME", "TICKER"]).loc[:, ["TICKER", "CODE", "Name", "GICS_SECTOR_NAME"]]

    latest_path = raw_dir / "snp_ksdq_gics_sector_latest.md"
    lines = [
        "# KOSDAQ GICS Sector Latest Mapping",
        "",
        "> Source: `raw/snp_ksdq_gics_sector_big.xlsx` sheet `KOSDAQ_Hist_GICS260331`",
        "",
        f"Latest available KOSDAQ GICS sector mapping as of `{latest_date.date()}`.",
        "",
        "| Ticker | Code | Name | GICS Sector |",
        "| --- | --- | --- | --- |",
    ]
    for _, row in latest.iterrows():
        lines.append(
            f"| `{row['TICKER']}` | `{row['CODE']}` | {str(row['Name']).strip()} | {row['GICS_SECTOR_NAME']} |"
        )
    lines.extend(["", f"Total tickers: **{len(latest)}**", ""])
    latest_path.write_text("\n".join(lines), encoding="utf-8")

    membership_path = raw_dir / "snp_ksdq_gics_sector_membership.md"
    membership_lines = [
        "# KOSDAQ GICS Sector Membership",
        "",
        "> Source: `raw/snp_ksdq_gics_sector_big.xlsx` sheet `KOSDAQ_Hist_GICS260331`",
        "",
        f"Sector-to-ticker membership grouped from the latest available snapshot on `{latest_date.date()}`.",
        "",
    ]
    for sector_name, group in latest.groupby("GICS_SECTOR_NAME", sort=True):
        membership_lines.append(f"## {sector_name}")
        membership_lines.append("")
        membership_lines.append(f"Ticker count: **{len(group)}**")
        membership_lines.append("")
        membership_lines.append("| Ticker | Code | Name |")
        membership_lines.append("| --- | --- | --- |")
        for _, row in group.iterrows():
            membership_lines.append(f"| `{row['TICKER']}` | `{row['CODE']}` | {str(row['Name']).strip()} |")
        membership_lines.append("")
    membership_path.write_text("\n".join(membership_lines), encoding="utf-8")

    return [pivot_path, latest_path, membership_path]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def log(message: str) -> None:
    OUT.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def prepare_output_paths(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    for child in out_dir.iterdir():
        if child.name in {"generate_graphify.py", "__pycache__"}:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    for dirname in ("obsidian", "wiki"):
        (out_dir / dirname).mkdir(parents=True, exist_ok=True)


class GraphBuilder:
    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}
        self.edges: dict[tuple[str, str, str, str], dict] = {}
        self.hyperedges: list[dict] = []
        self.doc_texts: dict[str, str] = {}
        self.code_texts: dict[str, str] = {}
        self.dataset_tokens: dict[str, set[str]] = {}
        self.symbol_index: defaultdict[str, set[str]] = defaultdict(set)
        self.file_nodes: dict[str, str] = {}
        self.function_calls: list[tuple[str, str, str, int]] = []
        self.py_module_to_file: dict[str, str] = {}

    def add_node(
        self,
        node_id: str,
        label: str,
        file_type: str,
        source_file: str,
        source_location: str | None = None,
        source_url: str | None = None,
        captured_at: str | None = None,
        author: str | None = None,
        contributor: str | None = None,
    ) -> None:
        if node_id in self.nodes:
            return
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "file_type": file_type,
            "source_file": source_file,
            "source_location": source_location,
            "source_url": source_url,
            "captured_at": captured_at,
            "author": author,
            "contributor": contributor,
        }

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        confidence: str,
        source_file: str,
        source_location: str | None = None,
        confidence_score: float | None = None,
        weight: float = 1.0,
    ) -> None:
        if source == target:
            return
        if source not in self.nodes or target not in self.nodes:
            return
        if confidence_score is None:
            confidence_score = {"EXTRACTED": 1.0, "INFERRED": 0.75, "AMBIGUOUS": 0.2}[confidence]
        key = (source, target, relation, source_file)
        if key in self.edges:
            return
        self.edges[key] = {
            "source": source,
            "target": target,
            "relation": relation,
            "confidence": confidence,
            "confidence_score": confidence_score,
            "source_file": source_file,
            "source_location": source_location,
            "weight": weight,
        }

    def add_hyperedge(
        self,
        hyper_id: str,
        label: str,
        nodes: list[str],
        relation: str,
        source_file: str,
        confidence: str = "INFERRED",
        confidence_score: float = 0.8,
    ) -> None:
        uniq = [n for n in nodes if n in self.nodes]
        if len(uniq) < 3:
            return
        self.hyperedges.append(
            {
                "id": hyper_id,
                "label": label,
                "nodes": uniq,
                "relation": relation,
                "confidence": confidence,
                "confidence_score": confidence_score,
                "source_file": source_file,
            }
        )

    def add_file_node(self, path: Path, file_type: str) -> str:
        source = rel(path)
        node_id = f"file_{slug(source)}"
        self.add_node(node_id, path.name, file_type, source)
        self.file_nodes[source] = node_id
        return node_id

    def scan(self) -> tuple[list[Path], list[Path], list[Path]]:
        code_files: list[Path] = []
        doc_files: list[Path] = []
        data_files: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for fname in filenames:
                if fname.startswith("."):
                    continue
                path = Path(dirpath) / fname
                ext = path.suffix.lower()
                if ext in CODE_EXTS:
                    code_files.append(path)
                elif ext in DOC_EXTS:
                    doc_files.append(path)
                elif ext in DATA_EXTS:
                    data_files.append(path)
        code_files.sort()
        doc_files.sort()
        data_files.sort()
        return code_files, doc_files, data_files

    def build_module_map(self, code_files: list[Path]) -> None:
        for path in code_files:
            if path.suffix.lower() != ".py":
                continue
            source = rel(path)
            module = source[:-3].replace("/", ".")
            self.py_module_to_file[module] = source
            if module.endswith(".__init__"):
                self.py_module_to_file[module[:-9]] = source

    def pretty_dataset_label(self, path: Path) -> tuple[str, set[str]]:
        stem = path.stem
        parts = [p for p in re.split(r"[_\W]+", stem) if p]
        normalized: list[str] = []
        tokens: set[str] = set()
        for part in parts:
            lower = part.lower()
            if lower == "qw":
                continue
            tokens.add(lower)
            normalized.append(RAW_TOKEN_MAP.get(lower, lower.upper() if lower.isupper() else lower))
        if "raw/options" in rel(path).replace("\\", "/"):
            normalized.insert(0, "options")
            tokens.add("options")
        if "raw/ksdq" in rel(path).replace("\\", "/"):
            normalized.insert(0, "KOSDAQ")
            tokens.add("ksdq")
        label = " ".join(word.title() for word in normalized) if normalized else stem
        return label, tokens

    def handle_python(self, path: Path) -> None:
        source = rel(path)
        file_node = self.add_file_node(path, "code")
        text = path.read_text(encoding="utf-8", errors="ignore")
        self.code_texts[source] = text.lower()
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return

        class_ids: dict[str, str] = {}
        func_ids: dict[str, str] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_id = f"class_{slug(source)}_{slug(node.name)}"
                class_ids[node.name] = class_id
                self.add_node(class_id, node.name, "code", source, f"L{node.lineno}")
                self.add_edge(file_node, class_id, "contains", "EXTRACTED", source, f"L{node.lineno}")
                self.symbol_index[node.name.lower()].add(class_id)
                doc = ast.get_docstring(node)
                if doc and len(doc.split()) > 8:
                    rat_id = f"rationale_{slug(source)}_{slug(node.name)}"
                    self.add_node(rat_id, f"{node.name} rationale", "rationale", source, f"L{node.lineno}")
                    self.add_edge(rat_id, class_id, "rationale_for", "EXTRACTED", source, f"L{node.lineno}")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parent = None
                for maybe_parent in ast.walk(tree):
                    for child in ast.iter_child_nodes(maybe_parent):
                        if child is node and isinstance(maybe_parent, ast.ClassDef):
                            parent = maybe_parent.name
                name = f"{parent}.{node.name}" if parent else node.name
                func_id = f"func_{slug(source)}_{slug(name)}"
                func_ids[name] = func_id
                self.add_node(func_id, f"{name}()", "code", source, f"L{node.lineno}")
                owner = class_ids.get(parent, file_node) if parent else file_node
                self.add_edge(owner, func_id, "contains", "EXTRACTED", source, f"L{node.lineno}")
                self.symbol_index[node.name.lower()].add(func_id)
                if parent:
                    self.symbol_index[name.lower()].add(func_id)
                doc = ast.get_docstring(node)
                if doc and len(doc.split()) > 8:
                    rat_id = f"rationale_{slug(source)}_{slug(name)}"
                    self.add_node(rat_id, f"{name} rationale", "rationale", source, f"L{node.lineno}")
                    self.add_edge(rat_id, func_id, "rationale_for", "EXTRACTED", source, f"L{node.lineno}")
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        call_name = None
                        if isinstance(child.func, ast.Name):
                            call_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            call_name = child.func.attr
                        if call_name:
                            self.function_calls.append((func_id, call_name.lower(), source, getattr(child, "lineno", node.lineno)))

            if isinstance(node, ast.Import):
                for alias in node.names:
                    mapped = self.py_module_to_file.get(alias.name)
                    if mapped and mapped in self.file_nodes:
                        self.add_edge(file_node, self.file_nodes[mapped], "imports", "EXTRACTED", source, f"L{node.lineno}")
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                if node.level:
                    current_parts = source[:-3].split("/")[:-1]
                    trimmed = current_parts[: max(0, len(current_parts) - (node.level - 1))]
                    module_parts = module_name.split(".") if module_name else []
                    module_name = ".".join(trimmed + module_parts)
                mapped = self.py_module_to_file.get(module_name)
                if mapped and mapped in self.file_nodes:
                    self.add_edge(file_node, self.file_nodes[mapped], "imports_from", "EXTRACTED", source, f"L{node.lineno}")

    def handle_typescript_like(self, path: Path) -> None:
        source = rel(path)
        file_node = self.add_file_node(path, "code")
        text = path.read_text(encoding="utf-8", errors="ignore")
        self.code_texts[source] = text.lower()

        for match in re.finditer(r"""import\s+.*?\s+from\s+['"]([^'"]+)['"]""", text):
            target = match.group(1)
            if target.startswith("."):
                resolved = (path.parent / target).resolve()
                candidates = [resolved.with_suffix(ext) for ext in (".ts", ".tsx", ".js", ".jsx")]
                candidates.append(resolved / "index.ts")
                candidates.append(resolved / "index.tsx")
                for candidate in candidates:
                    try_rel = os.path.relpath(candidate, ROOT)
                    if try_rel in self.file_nodes:
                        self.add_edge(file_node, self.file_nodes[try_rel], "imports_from", "EXTRACTED", source, f"L{text[:match.start()].count(chr(10)) + 1}")
                        break

        patterns = [
            r"""export\s+function\s+([A-Za-z0-9_]+)""",
            r"""function\s+([A-Za-z0-9_]+)\s*\(""",
            r"""const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\(""",
            r"""const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?[^=]*=>""",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                name = match.group(1)
                func_id = f"func_{slug(source)}_{slug(name)}"
                line = text[:match.start()].count("\n") + 1
                self.add_node(func_id, f"{name}()", "code", source, f"L{line}")
                self.add_edge(file_node, func_id, "contains", "EXTRACTED", source, f"L{line}")
                self.symbol_index[name.lower()].add(func_id)

    def handle_markdown(self, path: Path) -> None:
        source = rel(path)
        file_node = self.add_file_node(path, "document")
        text = path.read_text(encoding="utf-8", errors="ignore")
        self.doc_texts[source] = text.lower()
        for match in re.finditer(r"^(#{1,3})\s+(.+)$", text, re.MULTILINE):
            level = len(match.group(1))
            heading = match.group(2).strip()
            node_id = f"doc_{slug(source)}_{slug(heading)}"
            line = text[:match.start()].count("\n") + 1
            self.add_node(node_id, heading, "document", source, f"L{line}")
            self.add_edge(file_node, node_id, "contains", "EXTRACTED", source, f"L{line}")
            if level == 1:
                self.symbol_index[heading.lower()].add(node_id)

    def handle_data(self, path: Path) -> None:
        source = rel(path)
        file_node = self.add_file_node(path, "document")
        label, tokens = self.pretty_dataset_label(path)
        dataset_id = f"dataset_{slug(source)}"
        self.add_node(dataset_id, label, "document", source)
        self.add_edge(file_node, dataset_id, "contains", "EXTRACTED", source)
        self.dataset_tokens[dataset_id] = tokens
        for token in tokens:
            self.symbol_index[token].add(dataset_id)

        if path.suffix.lower() in {".csv", ".xlsx", ".xls"}:
            workbook_id = f"sheet_{slug(source)}_workbook"
            self.add_node(workbook_id, f"{path.stem} data shape", "document", source)
            self.add_edge(dataset_id, workbook_id, "references", "EXTRACTED", source)

    def resolve_calls(self) -> None:
        for func_id, call_name, source_file, line in self.function_calls:
            candidates = list(self.symbol_index.get(call_name, []))
            if not candidates:
                continue
            target = sorted(candidates)[0]
            self.add_edge(func_id, target, "calls", "INFERRED", source_file, f"L{line}", 0.82)

    def add_semantic_links(self) -> None:
        important_symbols = {
            token: ids
            for token, ids in self.symbol_index.items()
            if len(token) >= 4 and len(ids) <= 10
        }

        for source_file, text in self.doc_texts.items():
            file_node = self.file_nodes[source_file]
            for token, ids in important_symbols.items():
                if token not in text:
                    continue
                for target_id in sorted(ids)[:2]:
                    if self.nodes[target_id]["source_file"] == source_file:
                        continue
                    relation = "rationale_for" if self.nodes[target_id]["file_type"] == "code" else "references"
                    self.add_edge(file_node, target_id, relation, "INFERRED", source_file, confidence_score=0.72)

        for source_file, text in self.code_texts.items():
            file_node = self.file_nodes[source_file]
            for dataset_id, tokens in self.dataset_tokens.items():
                shared = [token for token in tokens if len(token) >= 3 and token in text]
                if not shared:
                    continue
                score = min(0.9, 0.62 + (0.06 * len(shared)))
                self.add_edge(file_node, dataset_id, "references", "INFERRED", source_file, confidence_score=score)

        docs = [path for path in self.doc_texts]
        for i, left in enumerate(docs):
            left_tokens = set(re.findall(r"[a-z][a-z0-9_]{3,}", self.doc_texts[left])) - STOPWORDS
            for right in docs[i + 1 :]:
                right_tokens = set(re.findall(r"[a-z][a-z0-9_]{3,}", self.doc_texts[right])) - STOPWORDS
                overlap = left_tokens & right_tokens
                if len(overlap) < 6:
                    continue
                self.add_edge(
                    self.file_nodes[left],
                    self.file_nodes[right],
                    "semantically_similar_to",
                    "INFERRED",
                    left,
                    confidence_score=0.68,
                )

        datasets_by_group: defaultdict[str, list[str]] = defaultdict(list)
        for dataset_id in self.dataset_tokens:
            source = self.nodes[dataset_id]["source_file"]
            group = source.split("/")[1] if source.count("/") >= 1 else source
            datasets_by_group[group].append(dataset_id)
        for group, node_ids in datasets_by_group.items():
            if len(node_ids) >= 3:
                self.add_hyperedge(
                    f"hyper_{slug(group)}",
                    f"{group.title()} data family",
                    sorted(node_ids)[:10],
                    "participate_in",
                    f"raw/{group}",
                )

        plan_nodes = [nid for nid, data in self.nodes.items() if data["source_file"].startswith("docs/superpowers/plans/")]
        spec_nodes = [nid for nid, data in self.nodes.items() if data["source_file"].startswith("docs/superpowers/specs/")]
        if len(plan_nodes) >= 3:
            self.add_hyperedge("hyper_plans", "Implementation planning corpus", plan_nodes[:12], "form", "docs/superpowers/plans")
        if len(spec_nodes) >= 3:
            self.add_hyperedge("hyper_specs", "Design spec corpus", spec_nodes[:12], "form", "docs/superpowers/specs")

    def extraction(self) -> dict:
        return {
            "nodes": list(self.nodes.values()),
            "edges": list(self.edges.values()),
            "hyperedges": self.hyperedges,
            "input_tokens": 0,
            "output_tokens": 0,
        }


def count_words(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        try:
            if path.suffix.lower() in {".csv", ".xlsx", ".xls"}:
                total += len(path.stem.split("_"))
            else:
                total += len(path.read_text(encoding="utf-8", errors="ignore").split())
        except Exception:
            continue
    return total


def label_communities(G, communities: dict[int, list[str]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for cid, nodes in communities.items():
        sources = [G.nodes[n].get("source_file", "") for n in nodes if G.nodes[n].get("source_file")]
        prefix_counts = Counter()
        token_counts = Counter()
        for source in sources:
            parts = source.split("/")
            if parts:
                prefix = " ".join(parts[:2] if len(parts) > 1 else parts[:1])
                prefix_counts[prefix] += 1
            for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_]{2,}", source.replace("/", " ")):
                if token.lower() not in STOPWORDS:
                    token_counts[token.lower()] += 1
        if prefix_counts:
            top_prefix, _ = prefix_counts.most_common(1)[0]
            if token_counts:
                extra = [tok for tok, _ in token_counts.most_common(3) if tok not in top_prefix.lower()]
                if extra:
                    labels[cid] = f"{top_prefix.replace('_', ' ').title()} {extra[0].title()}"
                    continue
            labels[cid] = top_prefix.replace("_", " ").title()
            continue
        labels[cid] = f"Community {cid}"
    return labels


def assign_community_attrs(G, communities: dict[int, list[str]]) -> None:
    for cid, nodes in communities.items():
        for node in nodes:
            G.nodes[node]["community"] = cid


def safe_graphml_export(G, communities: dict[int, list[str]], output_path: str) -> None:
    node_community = {node: cid for cid, nodes in communities.items() for node in nodes}
    H = nx.Graph()
    for node_id, data in G.nodes(data=True):
        attrs = {}
        for key, value in data.items():
            if value is None:
                attrs[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                attrs[key] = value
            else:
                attrs[key] = json.dumps(value, ensure_ascii=False)
        attrs["community"] = node_community.get(node_id, -1)
        H.add_node(node_id, **attrs)
    for u, v, data in G.edges(data=True):
        attrs = {}
        for key, value in data.items():
            if value is None:
                attrs[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                attrs[key] = value
            else:
                attrs[key] = json.dumps(value, ensure_ascii=False)
        H.add_edge(u, v, **attrs)
    nx.write_graphml(H, output_path)


def guarded_export(name: str, fn) -> None:
    log(name)
    try:
        fn()
    except Exception as exc:
        (OUT / f"{name.replace('.', '_')}.error.txt").write_text(str(exc), encoding="utf-8")
        log(f"{name}.error {exc}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    prepare_output_paths(OUT)
    LOG.write_text("", encoding="utf-8")
    log("start")
    generated_docs = materialize_raw_reference_docs(ROOT / "raw")
    if generated_docs:
        log(f"raw_docs.materialized count={len(generated_docs)}")
    builder = GraphBuilder()
    log("scan.begin")
    code_files, doc_files, data_files = builder.scan()
    log(f"scan.done code={len(code_files)} docs={len(doc_files)} data={len(data_files)}")
    builder.build_module_map(code_files)

    log("code.begin")
    for path in code_files:
        if path.suffix.lower() == ".py":
            builder.handle_python(path)
        else:
            builder.handle_typescript_like(path)
    log(f"code.done nodes={len(builder.nodes)} edges={len(builder.edges)}")

    log("docs.begin")
    for path in doc_files:
        builder.handle_markdown(path)
    log(f"docs.done nodes={len(builder.nodes)} edges={len(builder.edges)}")

    log("data.begin")
    for path in data_files:
        builder.handle_data(path)
    log(f"data.done nodes={len(builder.nodes)} edges={len(builder.edges)}")

    log("semantic.begin")
    builder.resolve_calls()
    builder.add_semantic_links()
    log(f"semantic.done nodes={len(builder.nodes)} edges={len(builder.edges)}")

    extraction = builder.extraction()
    log("extract.write")
    (OUT / "graph-extract.json").write_text(json.dumps(extraction, indent=2), encoding="utf-8")

    log("graph.build")
    G = build_from_json(extraction)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    labels = label_communities(G, communities)
    assign_community_attrs(G, communities)
    log(f"graph.built nodes={G.number_of_nodes()} edges={G.number_of_edges()} communities={len(communities)}")

    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    suggested = suggest_questions(G, communities, labels)

    total_files = len(code_files) + len(doc_files) + len(data_files)
    total_words = count_words(code_files + doc_files + data_files)
    detection = {
        "total_files": total_files,
        "total_words": total_words,
        "warning": None,
    }
    log("report.begin")
    report = generate(G, communities, cohesion, labels, gods, surprises, detection, {"input": 0, "output": 0}, str(ROOT), suggested_questions=suggested)

    guarded_export("export.json", lambda: to_json(G, communities, str(OUT / "graph.json")))
    guarded_export("export.html", lambda: to_html(G, communities, str(OUT / "graph.html"), community_labels=labels))
    guarded_export("export.graphml", lambda: safe_graphml_export(G, communities, str(OUT / "graph.graphml")))
    guarded_export("export.cypher", lambda: to_cypher(G, str(OUT / "cypher.txt")))
    guarded_export("export.obsidian", lambda: to_obsidian(G, communities, str(OUT / "obsidian"), community_labels=labels, cohesion=cohesion))
    guarded_export("export.wiki", lambda: to_wiki(G, communities, str(OUT / "wiki"), community_labels=labels, cohesion=cohesion, god_nodes_data=gods))
    guarded_export("export.svg", lambda: to_svg(G, communities, str(OUT / "graph.svg"), community_labels=labels))

    log("report.write")
    (OUT / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    (OUT / "labels.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")
    (OUT / "summary.json").write_text(
        json.dumps(
            {
                "total_files": total_files,
                "counts": {
                    "code": len(code_files),
                    "document": len(doc_files),
                    "data": len(data_files),
                },
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "communities": len(communities),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUT / "cost.json").write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "date": datetime.now(timezone.utc).isoformat(),
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "files": total_files,
                    }
                ],
                "total_input_tokens": 0,
                "total_output_tokens": 0,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest = {}
    for path in code_files + doc_files + data_files:
        try:
            manifest[rel(path)] = path.stat().st_mtime
        except OSError:
            continue
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    log("done")

    print(
        json.dumps(
            {
                "total_files": total_files,
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "communities": len(communities),
                "god_nodes": gods[:5],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
