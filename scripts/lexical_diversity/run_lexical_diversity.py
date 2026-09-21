#!/usr/bin/env python3
"""Run complete pooled and source-level lexical-diversity analyses.

Pooled results use original word forms from the Hugging Face corpus. Source-level
results use the nine local Stanza lemma files created for the paper.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator
from xml.etree import ElementTree as ET
from zipfile import ZipFile

TOKEN_PATTERN = re.compile(r"\b\w+\b", flags=re.UNICODE)
METRIC_FIELDS = [
    "language",
    "source",
    "input_form",
    "tokens",
    "types",
    "TTR",
    "MATTR",
    "MTLD_corrected",
    "HLR",
    "Guiraud",
    "vocd_style_D",
]


def tokenize(text: str) -> list[str]:
    """Apply the lowercase Unicode word tokenizer used in the paper analysis."""
    return TOKEN_PATTERN.findall(text.lower())


def _mtld_one_direction(tokens: list[str], threshold: float = 0.72) -> float:
    """Calculate MTLD in one direction, including a partial final factor."""
    if not tokens:
        return math.nan

    factors = 0.0
    types = set()
    length = 0
    for token in tokens:
        types.add(token)
        length += 1
        if len(types) / length <= threshold:
            factors += 1.0
            types.clear()
            length = 0

    if length:
        tail_ttr = len(types) / length
        factors += (1.0 - tail_ttr) / (1.0 - threshold)
    return len(tokens) / factors if factors else math.inf


def mtld(tokens: list[str], threshold: float = 0.72) -> float:
    """Return mean forward/reverse MTLD with partial final factors."""
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1")
    forward = _mtld_one_direction(tokens, threshold)
    backward = _mtld_one_direction(tokens[::-1], threshold)
    return (forward + backward) / 2


def _model_ttr(d_value: float, sample_size: int) -> float:
    return 2.0 / (math.sqrt(1.0 + 2.0 * sample_size / d_value) + 1.0)


def _fit_d(curve: list[tuple[int, float]]) -> float:
    """Fit D to an observed sample-size/TTR curve."""

    def loss(log_d: float) -> float:
        d_value = math.exp(log_d)
        return sum(
            (_model_ttr(d_value, sample_size) - observed) ** 2
            for sample_size, observed in curve
        )

    lower, upper = math.log(1e-6), math.log(1e7)
    ratio = (math.sqrt(5) - 1) / 2
    left = upper - ratio * (upper - lower)
    right = lower + ratio * (upper - lower)
    for _ in range(160):
        if loss(left) < loss(right):
            upper = right
            right = left
            left = upper - ratio * (upper - lower)
        else:
            lower = left
            left = right
            right = lower + ratio * (upper - lower)
    estimate = math.exp((lower + upper) / 2)
    return math.inf if estimate >= 0.99e7 else estimate


def vocd_d(
    tokens: list[str], trials: int = 100, runs: int = 3, seed: int = 42
) -> float:
    """Estimate seeded vocd-style D using samples of 35 through 50 tokens."""
    if len(tokens) < 50:
        raise ValueError("vocd-D needs at least 50 tokens")
    if trials < 1 or runs < 1:
        raise ValueError("trials and runs must be positive")
    if len(set(tokens)) == len(tokens):
        return math.inf

    estimates = []
    for run in range(runs):
        rng = random.Random(seed + run)
        curve = []
        for sample_size in range(35, 51):
            mean_ttr = sum(
                len(set(rng.sample(tokens, sample_size))) / sample_size
                for _ in range(trials)
            ) / trials
            curve.append((sample_size, mean_ttr))
        estimates.append(_fit_d(curve))
    return sum(estimates) / runs


def mattr(tokens: list[str], window_size: int = 50) -> float:
    """Calculate MATTR efficiently with a sliding frequency window."""
    if not tokens:
        return math.nan
    if len(tokens) < window_size:
        return len(set(tokens)) / len(tokens)

    counts = Counter(tokens[:window_size])
    ttr_sum = len(counts) / window_size
    window_count = 1

    for outgoing, incoming in zip(tokens, tokens[window_size:]):
        counts[outgoing] -= 1
        if counts[outgoing] == 0:
            del counts[outgoing]
        counts[incoming] += 1
        ttr_sum += len(counts) / window_size
        window_count += 1

    return ttr_sum / window_count


def calculate_metrics(
    tokens: list[str], language: str, source: str, input_form: str
) -> dict[str, str | int | float]:
    """Calculate the complete metric set for one token sequence."""
    if not tokens:
        raise ValueError(f"No tokens found for {language}/{source}")

    frequencies = Counter(tokens)
    token_count = len(tokens)
    type_count = len(frequencies)
    hapax_count = sum(count == 1 for count in frequencies.values())

    return {
        "language": language,
        "source": source,
        "input_form": input_form,
        "tokens": token_count,
        "types": type_count,
        "TTR": type_count / token_count,
        "MATTR": mattr(tokens, window_size=50),
        "MTLD_corrected": mtld(tokens, threshold=0.72),
        "HLR": hapax_count / type_count,
        "Guiraud": type_count / math.sqrt(token_count),
        "vocd_style_D": vocd_d(tokens, trials=100, runs=3, seed=42),
    }


def read_text_files(paths: Iterable[Path]) -> tuple[list[str], int]:
    """Tokenize and concatenate UTF-8 text files in deterministic path order."""
    tokens: list[str] = []
    count = 0
    for path in sorted(paths):
        tokens.extend(tokenize(path.read_text(encoding="utf-8", errors="ignore")))
        count += 1
    return tokens, count


def _column_index(cell_reference: str) -> int:
    letters = "".join(character for character in cell_reference if character.isalpha())
    index = 0
    for character in letters.upper():
        index = index * 26 + ord(character) - ord("A") + 1
    return index - 1


def _cell_value(
    cell: ET.Element, namespace: dict[str, str], shared_strings: list[str]
) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(
            node.text or "" for node in cell.findall(".//m:is//m:t", namespace)
        )
    value = cell.find("m:v", namespace)
    if value is None or value.text is None:
        return ""
    if cell_type == "s":
        return shared_strings[int(value.text)]
    return value.text


def read_xlsx_column(path: Path, column_name: str) -> Iterator[str]:
    """Read a named column from the first XLSX sheet using the standard library."""
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    package_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    namespace = {"m": main_ns, "r": rel_ns}

    with ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for string_item in shared_root.findall("m:si", namespace):
                shared_strings.append(
                    "".join(
                        node.text or ""
                        for node in string_item.findall(".//m:t", namespace)
                    )
                )

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relation_targets = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in relationships.findall(f"{{{package_rel_ns}}}Relationship")
        }
        first_sheet = workbook.find("m:sheets/m:sheet", namespace)
        if first_sheet is None:
            raise ValueError(f"No worksheet found in {path}")
        relation_id = first_sheet.attrib[f"{{{rel_ns}}}id"]
        target = relation_targets[relation_id]
        worksheet_path = target.lstrip("/") if target.startswith("/xl/") else f"xl/{target}"
        worksheet = ET.fromstring(archive.read(worksheet_path))

        rows = worksheet.findall(".//m:sheetData/m:row", namespace)
        if not rows:
            raise ValueError(f"No rows found in {path}")

        header_by_index = {
            _column_index(cell.attrib["r"]): _cell_value(cell, namespace, shared_strings)
            for cell in rows[0].findall("m:c", namespace)
        }
        matching_indexes = [
            index for index, header in header_by_index.items() if header == column_name
        ]
        if not matching_indexes:
            raise ValueError(f"Column {column_name!r} not found in {path}")
        target_index = matching_indexes[0]

        for row in rows[1:]:
            cells = {
                _column_index(cell.attrib["r"]): _cell_value(
                    cell, namespace, shared_strings
                )
                for cell in row.findall("m:c", namespace)
            }
            value = cells.get(target_index, "").strip()
            if value:
                yield value


def write_csv(path: Path, rows: list[dict[str, str | int | float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file, fieldnames=METRIC_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def corpus_revision(corpus_root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(corpus_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus-root", type=Path, default=repository_root / "data" / "corpus"
    )
    parser.add_argument(
        "--results-root", type=Path, default=repository_root / "results"
    )
    arguments = parser.parse_args()

    corpus_root = arguments.corpus_root.resolve()
    results_root = arguments.results_root.resolve()
    kazakh_root = corpus_root / "Kazakh"
    russian_root = corpus_root / "Russian"
    russian_dialogue = russian_root / "russian_dialogue" / "Russian_childes.xlsx"

    excluded = [
        kazakh_root / "kazakh_all.txt",
        russian_root / "Names_ages_of_children.xlsx",
    ]
    required = [kazakh_root, russian_root, russian_dialogue]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs: " + ", ".join(missing))

    kazakh_paths = [
        path
        for path in kazakh_root.rglob("*.txt")
        if path.resolve() != excluded[0].resolve()
    ]
    russian_paths = list(russian_root.rglob("*.txt"))

    print("Loading pooled Kazakh word forms...")
    kazakh_tokens, kazakh_file_count = read_text_files(kazakh_paths)
    print("Loading pooled Russian word forms and dialogue...")
    russian_tokens, russian_file_count = read_text_files(russian_paths)
    dialogue_rows = list(read_xlsx_column(russian_dialogue, "SENTENCES"))
    for sentence in dialogue_rows:
        russian_tokens.extend(tokenize(sentence))

    pooled_rows = [
        calculate_metrics(russian_tokens, "Russian", "pooled", "word_forms"),
        calculate_metrics(kazakh_tokens, "Kazakh", "pooled", "word_forms"),
    ]

    source_inputs = [
        ("Russian", "by_ages_from_0-11", "ru_ages_lemmas.txt"),
        ("Russian", "ru_dialogue", "ru_dialogue_lemmas.txt"),
        ("Russian", "ru_folk_tales", "ru_folk_tales_lemmas.txt"),
        ("Russian", "ru_other_cultures", "ru_other_cultures_lemmas.txt"),
        ("Kazakh", "kazakh_fairytale", "fairy_tales_lemmas.txt"),
        ("Kazakh", "kazakh_subtitles", "subtitles_lemmas.txt"),
        ("Kazakh", "kazakh_journal", "journal_lemmas.txt"),
        ("Kazakh", "kazakh_books", "books_lemmas.txt"),
        ("Kazakh", "kazakh_educational", "educational_lemmas.txt"),
    ]

    source_rows = []
    for language, directory_name, filename in source_inputs:
        language_directory = "russian" if language == "Russian" else "kazakh"
        path = (
            results_root
            / "lemmatization"
            / language_directory
            / directory_name
            / filename
        )
        if not path.exists():
            raise FileNotFoundError(f"Missing lemma input: {path}")
        print(f"Calculating source metrics: {language}/{directory_name}")
        source_rows.append(
            calculate_metrics(
                tokenize(path.read_text(encoding="utf-8", errors="ignore")),
                language,
                path.stem,
                "lemmas",
            )
        )

    output_directory = results_root / "lexical_diversity"
    pooled_path = output_directory / "pooled_all_metrics.csv"
    source_path = output_directory / "source_level_all_metrics.csv"
    combined_path = output_directory / "all_lexical_diversity_metrics.csv"
    write_csv(pooled_path, pooled_rows)
    write_csv(source_path, source_rows)
    write_csv(combined_path, pooled_rows + source_rows)

    metadata = {
        "corpus": "esimijoq/Kazakh-Russian-Child-Directed-Speech-Corpus",
        "corpus_revision": corpus_revision(corpus_root),
        "excluded_inputs": [str(path.relative_to(corpus_root)) for path in excluded],
        "pooled_input_counts": {
            "kazakh_text_files": kazakh_file_count,
            "russian_text_files": russian_file_count,
            "russian_dialogue_rows": len(dialogue_rows),
        },
        "tokenizer": "lowercase Unicode regex \\b\\w+\\b",
        "MATTR_window": 50,
        "MTLD_threshold": 0.72,
        "MTLD_directions": "forward and reverse, with partial final factors",
        "vocd_sample_sizes": "35-50",
        "vocd_trials_per_size": 100,
        "vocd_runs": 3,
        "vocd_seed": 42,
        "outputs": [pooled_path.name, source_path.name, combined_path.name],
    }
    metadata_path = output_directory / "run_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    for row in pooled_rows + source_rows:
        print(
            f"{row['language']:7} {row['source']:24} "
            f"tokens={row['tokens']:>8,} types={row['types']:>7,} "
            f"MATTR={row['MATTR']:.4f} MTLD={row['MTLD_corrected']:.4f} "
            f"D={row['vocd_style_D']:.4f}"
        )
    print(f"Wrote {combined_path}")


if __name__ == "__main__":
    main()
