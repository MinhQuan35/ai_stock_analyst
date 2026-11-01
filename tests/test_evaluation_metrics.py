"""Regression checks for the benchmark metric fixes (Phase 1)."""
from src.agent.evaluation import (
    calculate_entities_recall,
    calculate_map_at_k,
    calculate_numerical_accuracy,
    calculate_overall_answer_accuracy,
    calculate_tool_success_rate,
    extract_numbers_from_text,
)


def test_map_at_k_is_bounded():
    # Many chunks of the same document must not push AP above 1
    assert calculate_map_at_k(["a.md"] * 5, ["a.md"], 5) == 1.0
    assert calculate_map_at_k(["a.md", "a.md", "b.md"], ["a.md", "b.md"], 5) == 1.0
    # Perfect-ish ranking with one miss
    assert 0 < calculate_map_at_k(["x.md", "a.md"], ["a.md"], 5) <= 1.0


def test_number_extraction_handles_unit_suffixes():
    assert 16.5 in extract_numbers_from_text("P/E is 16.5x")
    assert 24.1 in extract_numbers_from_text("ROE of 24.1%")
    assert 1234.5 in extract_numbers_from_text("1,234.5 VND")


def test_numerical_accuracy_returns_none_without_numbers():
    assert calculate_numerical_accuracy("prose answer", "prose ground truth") is None
    assert calculate_numerical_accuracy("P/E 16.5x", "16.5x", [16.5]) == 1.0
    assert calculate_numerical_accuracy("price 52,700", "138,500", [138500.0]) == 0.0


def test_numerical_accuracy_accepts_unit_scaling():
    # answer in raw VND, ground truth in billion VND
    assert calculate_numerical_accuracy("13,788,500,000,000 VND", "13,788.50 tỷ VND", [13788.5]) == 1.0


def test_entities_recall_penalises_wrong_numbers():
    assert calculate_entities_recall("FPT trades at 52,700 VND", "138,500 VND") < 0.5
    assert calculate_entities_recall("FPT trades at 138,500 VND", "138,500 VND") == 1.0
    assert calculate_entities_recall("anything", "") is None


def test_tool_success_rejects_errors_and_empty_output():
    assert calculate_tool_success_rate([{"output": "Error retrieving data"}]) == 0.0
    assert calculate_tool_success_rate([{"output": ""}]) == 0.0
    assert calculate_tool_success_rate([{"output": "Close Price: 138,500 VND"}]) == 1.0
    assert calculate_tool_success_rate([]) is None


def test_overall_accuracy_is_none_without_signal():
    assert calculate_overall_answer_accuracy(None, None, None) is None
    assert calculate_overall_answer_accuracy(0.9) == 1
    assert calculate_overall_answer_accuracy(0.2) == 0
