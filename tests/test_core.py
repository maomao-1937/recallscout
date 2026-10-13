import numpy as np
import pytest

from recallscout.core import Passage, audit, markdown_report, parse_passages, parse_selection


class FakeEncoder:
    def encode(self, texts):
        mapping = {
            "travel": [1.0, 0.0],
            "train trip": [0.95, 0.05],
            "packed a bag": [0.9, 0.1],
            "invoice": [0.0, 1.0],
        }
        return np.array([mapping[x] for x in texts], dtype=float)


def test_parse_passages_rejects_duplicate_ids():
    with pytest.raises(ValueError, match="duplicate"):
        parse_passages([{"id": "a", "text": "one"}, {"id": "a", "text": "two"}])


def test_parse_passages_rejects_blank_text():
    with pytest.raises(ValueError, match="non-empty text"):
        parse_passages([{"id": "a", "text": " "}])


def test_selection_rejects_unknown_id():
    with pytest.raises(ValueError, match="unknown"):
        parse_selection({"topic": "travel", "selected_ids": ["missing"]}, {"a"})


def test_selection_allows_query_without_positives():
    assert parse_selection({"topic": "travel"}, {"a"}) == ("travel", [], [])


def test_audit_ranks_unselected_semantic_match_first():
    passages = [Passage("a", "train trip"), Passage("b", "packed a bag"), Passage("c", "invoice")]
    result = audit(passages, "travel", ["a"], [], FakeEncoder(), min_score=0.4)
    assert [x["id"] for x in result] == ["b"]
    assert result[0]["nearest_positive"] == "train trip"


def test_audit_query_only_returns_candidates():
    result = audit([Passage("b", "packed a bag")], "travel", [], [], FakeEncoder())
    assert result[0]["positive_similarity"] is None


def test_audit_rejects_invalid_limit():
    with pytest.raises(ValueError, match="limit"):
        audit([Passage("b", "packed a bag")], "travel", [], [], FakeEncoder(), limit=0)


def test_report_disclaims_no_guarantee():
    assert "does not prove complete extraction" in markdown_report("travel", 0, 1, [])
