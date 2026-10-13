"""CLI for local read-only review of likely omitted passages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import audit, markdown_report, parse_passages, parse_selection
from .model import MODEL_NAME, get_model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find candidate passages missed by a topic extraction")
    parser.add_argument("passages", type=Path, help="JSON array of {id,text,source} passages")
    parser.add_argument("selection", type=Path, help="JSON object with topic and selected_ids")
    parser.add_argument("--out", type=Path, default=Path("report.md"), help="Markdown review queue")
    parser.add_argument("--json-out", type=Path, help="Optional machine-readable review queue")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--min-score", type=float, default=0.25)
    args = parser.parse_args(argv)
    try:
        raw_passages = json.loads(args.passages.read_text(encoding="utf-8"))
        raw_selection = json.loads(args.selection.read_text(encoding="utf-8"))
        passages = parse_passages(raw_passages)
        topic, selected, examples = parse_selection(raw_selection, {p.id for p in passages})
        results = audit(passages, topic, selected, examples, get_model(), limit=args.limit, min_score=args.min_score)
        report = markdown_report(topic, len(selected), len(passages), results)
        args.out.write_text(report, encoding="utf-8")
        if args.json_out:
            args.json_out.write_text(
                json.dumps(
                    {"topic": topic, "model": MODEL_NAME, "selected_count": len(selected), "total_count": len(passages), "candidates": results},
                    ensure_ascii=False,
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
        print(f"Wrote {len(results)} review candidates to {args.out}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"recallscout: {exc}", file=sys.stderr)
        return 2
