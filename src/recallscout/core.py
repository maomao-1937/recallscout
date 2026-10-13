"""Second-pass semantic ranking of unselected source passages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class Passage:
    id: str
    text: str
    source: str = ""


def parse_passages(raw: Any) -> list[Passage]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("passages must be a non-empty JSON array")
    result: list[Passage] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"passage {index} must be an object")
        identifier = item.get("id")
        body = item.get("text")
        source = item.get("source", "")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError(f"passage {index} needs a non-empty string id")
        if identifier in seen:
            raise ValueError(f"duplicate passage id: {identifier}")
        if not isinstance(body, str) or not body.strip():
            raise ValueError(f"passage {identifier} needs non-empty text")
        if not isinstance(source, str):
            raise ValueError(f"passage {identifier} source must be a string")
        seen.add(identifier)
        result.append(Passage(identifier, body.strip(), source.strip()))
    return result


def parse_selection(raw: Any, ids: set[str]) -> tuple[str, list[str], list[str]]:
    if not isinstance(raw, dict):
        raise ValueError("selection must be a JSON object")
    topic = raw.get("topic")
    selected = raw.get("selected_ids", [])
    examples = raw.get("positive_examples", [])
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("selection needs a non-empty topic")
    if not isinstance(selected, list) or any(not isinstance(x, str) for x in selected):
        raise ValueError("selected_ids must be a list of passage IDs")
    if len(set(selected)) != len(selected):
        raise ValueError("selected_ids contains duplicates")
    missing = set(selected) - ids
    if missing:
        raise ValueError(f"unknown selected_ids: {', '.join(sorted(missing))}")
    if not isinstance(examples, list) or any(not isinstance(x, str) or not x.strip() for x in examples):
        raise ValueError("positive_examples must be a list of non-empty strings")
    return topic.strip(), selected, [x.strip() for x in examples]


def _normalize(vectors: Any, expected: int) -> np.ndarray:
    matrix = np.asarray(vectors, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != expected or not np.isfinite(matrix).all():
        raise ValueError("embedding model returned invalid vectors")
    lengths = np.linalg.norm(matrix, axis=1, keepdims=True)
    if np.any(lengths == 0):
        raise ValueError("embedding model returned a zero vector")
    return matrix / lengths


def audit(
    passages: list[Passage],
    topic: str,
    selected_ids: list[str],
    positive_examples: list[str],
    encoder: Any,
    *,
    limit: int = 10,
    min_score: float = 0.25,
) -> list[dict[str, Any]]:
    """Rank candidates; scores are similarities, never probabilities or recall."""
    if limit < 1:
        raise ValueError("limit must be positive")
    if not -1 <= min_score <= 1:
        raise ValueError("min_score must be between -1 and 1")
    selected_set = set(selected_ids)
    selected_passages = [p for p in passages if p.id in selected_set]
    anchors = [p.text for p in selected_passages] + positive_examples
    texts = [topic] + [p.text for p in passages] + anchors
    vectors = _normalize(encoder.encode(texts), len(texts))
    topic_vector = vectors[0]
    passage_vectors = vectors[1 : 1 + len(passages)]
    anchor_vectors = vectors[1 + len(passages) :]
    findings = []
    for p, vector in zip(passages, passage_vectors):
        if p.id in selected_set:
            continue
        topic_similarity = float(np.dot(vector, topic_vector))
        anchor_similarity = float(np.max(anchor_vectors @ vector)) if anchors else None
        score = topic_similarity if anchor_similarity is None else 0.55 * topic_similarity + 0.45 * anchor_similarity
        if score < min_score:
            continue
        best_anchor = anchors[int(np.argmax(anchor_vectors @ vector))] if anchors else None
        findings.append(
            {
                "id": p.id,
                "source": p.source,
                "text": p.text,
                "score": round(score, 4),
                "topic_similarity": round(topic_similarity, 4),
                "nearest_positive": best_anchor,
                "positive_similarity": round(anchor_similarity, 4) if anchor_similarity is not None else None,
            }
        )
    findings.sort(key=lambda x: (-x["score"], x["id"]))
    return findings[:limit]


def markdown_report(topic: str, selected_count: int, total_count: int, findings: list[dict[str, Any]]) -> str:
    lines = [
        "# RecallScout review queue",
        "",
        f"Topic: {topic}",
        f"Selected passages: {selected_count}/{total_count}",
        "",
        "These are semantic review candidates, not confirmed misses. A low score does not prove irrelevance; no recall rate is calculated without human labels.",
        "",
    ]
    if not findings:
        lines.append("No candidate passed the current score threshold. This does not prove complete extraction.")
    for item in findings:
        lines.extend(
            [
                f"## {item['id']} — score {item['score']:.4f}",
                "",
                f"Source: {item['source'] or 'not supplied'}",
                f"Passage: {item['text']}",
                f"Nearest selected/example: {item['nearest_positive'] or 'none supplied'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
