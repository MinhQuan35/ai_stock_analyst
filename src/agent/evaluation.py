"""
Evaluation module - RAG evaluation metrics and LLM-as-Judge
"""
import json
import re
import math
from dataclasses import dataclass
from typing import List, Optional
from langchain_core.messages import SystemMessage, HumanMessage

from src.models import get_chat_model
from src.utils.logger import logger


class LLMJudge:
    """Use LLM to evaluate RAG outputs (RAGAS-style)."""
    
    JUDGE_PROMPT = """You are an expert evaluator for a RAG (Retrieval-Augmented Generation) system.

Evaluate the following on a scale from 0 to 1:

**Question**: {question}

**Answer**: {answer}

**Context**: {context}

{criteria}

Provide scores in JSON format. Be strict and accurate.
Only return valid JSON, no other text.

Format:
```json
{{
    "score": 0.X,
    "reason": "brief explanation"
}}
```"""
    
    CORRECTNESS_PROMPT = """You are an expert evaluator for a financial QA system.

**Question**: {question}

**Answer**: {answer}

**Ground Truth**: {ground_truth}

You are NOT given retrieval context. The Ground Truth above is authoritative.

**Correctness (0-1)**: Score 1.0 if the answer states the same key facts and numbers as the Ground Truth. Rounding differences below 1%, unit formatting such as raw VND vs billion VND, thousands separators, and extra supporting detail are all acceptable. Score 0.0 if any key fact or number is missing or contradicts the Ground Truth.

Only return valid JSON, no other text:
```json
{{"score": 0.X, "reason": "brief explanation"}}
```"""

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0):
        """Initialize LLM Judge."""
        self.llm = get_chat_model(temperature=temperature)
        logger.info(f"LLM Judge initialized: {model_name}")
    
    def _parse_score(self, response: str) -> tuple[float, str]:
        """Parse score from LLM response."""
        try:
            json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return float(data.get("score", 0)), data.get("reason", "")
            
            numbers = re.findall(r'0\.\d+|1\.0|0', response)
            if numbers:
                return float(numbers[0]), response[:100]
            
            return 0.0, "Could not parse"
        except Exception as e:
            logger.warning(f"Parse error: {e}")
            return 0.0, str(e)
    
    def _evaluate(self, question: str, answer: str, context: str, criteria: str) -> tuple[float, str]:
        """Generic LLM evaluation."""
        prompt = self.JUDGE_PROMPT.format(
            question=question,
            answer=answer,
            context=context,
            criteria=criteria,
        )
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            return self._parse_score(content)
        except Exception as e:
            logger.error(f"LLM Judge error: {e}")
            return 0.0, str(e)
    
    def faithfulness(self, question: str, answer: str, context: str) -> tuple[float, str]:
        """Evaluate faithfulness."""
        criteria = """**Faithfulness (0-1)**: Is the answer GROUNDED in the context?"""
        return self._evaluate(question, answer, context, criteria)
    
    def answer_relevancy(self, question: str, answer: str) -> tuple[float, str]:
        """Evaluate answer relevancy."""
        criteria = """**Answer Relevancy (0-1)**: Does the answer ADDRESS the question?"""
        return self._evaluate(question, answer, "N/A", criteria)
    
    def context_relevancy(self, question: str, context: str) -> tuple[float, str]:
        """Evaluate context relevancy."""
        criteria = """**Context Relevancy (0-1)**: Is the context RELEVANT to the question?"""
        return self._evaluate(question, "N/A", context, criteria)
    
    def correctness(self, question: str, answer: str, ground_truth: str) -> tuple[float, str]:
        """Evaluate correctness against ground truth (no retrieval context needed)."""
        prompt = self.CORRECTNESS_PROMPT.format(
            question=question,
            answer=answer,
            ground_truth=ground_truth,
        )
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            return self._parse_score(content)
        except Exception as e:
            logger.error(f"LLM Judge correctness error: {e}")
            return 0.0, str(e)
    
    def evaluate_all(
        self,
        question: str,
        answer: str,
        context: str,
        ground_truth: Optional[str] = None,
    ) -> dict:
        """Evaluate all metrics at once."""
        results = {}
        score, reason = self.faithfulness(question, answer, context)
        results["faithfulness"] = {"score": score, "reason": reason}
        
        score, reason = self.answer_relevancy(question, answer)
        results["answer_relevancy"] = {"score": score, "reason": reason}
        
        score, reason = self.context_relevancy(question, context)
        results["context_relevancy"] = {"score": score, "reason": reason}
        
        if ground_truth:
            score, reason = self.correctness(question, answer, ground_truth)
            results["correctness"] = {"score": score, "reason": reason}
        
        return results


def normalize_source_name(src: str) -> str:
    """Normalize source document name to basename for robust matching."""
    if not src:
        return ""
    import os
    from pathlib import Path
    return Path(src).name.lower().strip()


FINANCIAL_TICKERS = {
    "fpt", "vcb", "vnm", "hpg", "mwg", "bid", "vic", "vhm", "msn", "tcb", "mbb", "vnindex", "vn30",
    "nvda", "aapl", "msft", "tsla", "amd", "tsm", "asml", "orcl", "pltr", "amzn", "googl",
}
_PERIOD_RE = re.compile(r"q[1-4]\s*(?:fy)?\s*20\d{2}|fy\s*20\d{2}")


# Number followed by optional unit suffix (16.5x, 24.1%, $30.77B) - no trailing \b
NUM_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")
_UNIT_SCALES = (1.0, 1e3, 1e6, 1e9, 1e12)


def extract_numbers_from_text(text: str) -> List[float]:
    """Extract numeric values (handles 16.5x, 24.1%, 1,234.5)."""
    vals = []
    for m in NUM_RE.findall(text or ""):
        try:
            vals.append(float(m.replace(",", "")))
        except ValueError:
            pass
    return vals


def _numbers_match(val: float, target: float, tolerance: float) -> bool:
    """Compare two numbers, allowing common financial unit multipliers."""
    if abs(target) < 1e-6:
        return abs(val) < 1e-6
    for scale in _UNIT_SCALES:
        if abs(val * scale - target) / abs(target) <= tolerance:
            return True
        if abs(val / scale - target) / abs(target) <= tolerance:
            return True
    return False


def calculate_numerical_accuracy(
    answer: str,
    ground_truth: str,
    expected_values: Optional[List[float]] = None,
    tolerance: float = 0.02
) -> Optional[float]:
    """Fraction of expected numeric facts present in the answer.

    Returns None when the query makes no numeric claim (excluded from averages
    instead of being counted as a free 1.0).
    """
    targets = expected_values if expected_values else extract_numbers_from_text(ground_truth)
    if not targets:
        return None

    answer_nums = extract_numbers_from_text(answer)
    if not answer_nums:
        return 0.0

    matched = sum(1 for t in targets if any(_numbers_match(v, t, tolerance) for v in answer_nums))
    return matched / len(targets)


def calculate_tool_selection_accuracy(actual_tools: List[str], expected_tools: List[str]) -> float:
    """Calculate Tool Selection Accuracy (% of expected tools correctly selected)."""
    if not expected_tools:
        return 1.0 if not actual_tools else 0.5
    
    act_set = set(actual_tools)
    exp_set = set(expected_tools)
    
    if exp_set.issubset(act_set):
        return 1.0
    
    overlap = len(act_set & exp_set)
    return overlap / len(exp_set)


def _dedupe_sources(sources: List[str]) -> List[str]:
    """Collapse repeated chunks of the same document, preserving rank order."""
    seen = set()
    out = []
    for s in sources:
        n = normalize_source_name(s)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def calculate_map_at_k(retrieved_docs: List[str], relevant_docs: List[str], k: int = 5) -> Optional[float]:
    """Mean Average Precision at K over unique documents (bounded 0..1)."""
    retrieved = _dedupe_sources(retrieved_docs)[:k]
    relevant = {normalize_source_name(d) for d in relevant_docs}

    if not relevant:
        return None

    hits = 0
    ap = 0.0
    for i, doc in enumerate(retrieved, 1):
        if doc in relevant:
            hits += 1
            ap += hits / i

    return min(ap / len(relevant), 1.0)


def calculate_hit_at_k(retrieved_docs: List[str], relevant_docs: List[str], ks: Optional[List[int]] = None) -> dict:
    """Calculate Hit@K for K in [1, 3, 5, 10] over unique documents."""
    if ks is None:
        ks = [1, 3, 5, 10]
    norm_retrieved = _dedupe_sources(retrieved_docs)
    norm_relevant = {normalize_source_name(d) for d in relevant_docs}
    
    if not norm_relevant:
        return {f"hit@{k}": None for k in ks}

    results = {}
    for k in ks:
        subset = norm_retrieved[:k]
        hit = 1.0 if any(d in norm_relevant for d in subset) else 0.0
        results[f"hit@{k}"] = hit
    return results


FINANCIAL_TICKERS = {
    "fpt", "vcb", "vnm", "hpg", "mwg", "bid", "vic", "vhm", "msn", "tcb", "mbb", "vnindex", "vn30",
    "nvda", "aapl", "msft", "tsla", "amd", "tsm", "asml", "orcl", "pltr", "amzn", "googl",
}
_PERIOD_RE = re.compile(r"q[1-4]\s*(?:fy)?\s*20\d{2}|fy\s*20\d{2}")


def calculate_entities_recall(answer: str, ground_truth: str) -> Optional[float]:
    """Recall of key facts (tickers, reporting periods, numbers) from GT in the answer.

    Returns None when the ground truth has no checkable facts.
    """
    gt = (ground_truth or "").lower()
    ans = (answer or "").lower()
    if not gt:
        return None

    tickers = [t for t in FINANCIAL_TICKERS if re.search(rf"\b{re.escape(t)}\b", gt)]
    periods = _PERIOD_RE.findall(gt)
    gt_nums = extract_numbers_from_text(gt)
    ans_nums = extract_numbers_from_text(ans)

    total = len(tickers) + len(periods) + len(gt_nums)
    if total == 0:
        return None

    found = sum(1 for t in tickers if re.search(rf"\b{re.escape(t)}\b", ans))
    ans_compact = ans.replace(" ", "")
    found += sum(1 for p in periods if p.replace(" ", "") in ans_compact)
    found += sum(1 for n in gt_nums if any(_numbers_match(a, n, 0.02) for a in ans_nums))

    return found / total


_TOOL_ERROR_MARKERS = (
    "error",
    "unable to fetch",
    "no price history",
    "not available",
    "no relevant documents",
)


def calculate_tool_success_rate(tool_calls_detail: List[dict]) -> Optional[float]:
    """Fraction of tool calls that returned usable (non-empty, non-error) output."""
    if not tool_calls_detail:
        return None
    ok = 0
    for call in tool_calls_detail:
        output = str(call.get("output", "")).strip().lower()
        usable = bool(output) and not output.startswith(_TOOL_ERROR_MARKERS)
        if call.get("success", True) and usable:
            ok += 1
    return ok / len(tool_calls_detail)


def calculate_fallback_rate(fallback_triggered: bool) -> float:
    """Calculate fallback rate."""
    return 1.0 if fallback_triggered else 0.0


def calculate_overall_answer_accuracy(
    correctness_score: Optional[float],
    numerical_acc: Optional[float] = None,
    entities_rec: Optional[float] = None,
) -> Optional[int]:
    """Binary answer correctness. None when there is not enough signal to judge."""
    if correctness_score is not None:
        return 1 if correctness_score >= 0.7 else 0
    if numerical_acc is not None or entities_rec is not None:
        num = numerical_acc if numerical_acc is not None else 1.0
        ent = entities_rec if entities_rec is not None else 1.0
        return 1 if num >= 0.9 and ent >= 0.7 else 0
    return None


@dataclass
class RAGMetrics:
    """Container for RAG & Agent evaluation metrics."""
    # Retrieval
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    mrr: float = 0.0
    ndcg: float = 0.0
    map_at_k: float = 0.0
    hit_at_1: float = 0.0
    hit_at_3: float = 0.0
    hit_at_5: float = 0.0
    hit_at_10: float = 0.0
    
    # Chunk-level Context
    context_precision: float = 0.0
    context_recall: float = 0.0
    
    # Generation & Accuracy
    overall_answer_accuracy: Optional[int] = None  # binary 0 or 1
    numerical_accuracy: Optional[float] = None
    entities_recall: Optional[float] = None
    answer_correctness: float = 0.0
    faithfulness_word: float = 0.0
    relevancy_word: float = 0.0
    
    # Agentic & Tool Execution
    tool_selection_accuracy: float = 1.0
    tool_success_rate: Optional[float] = None
    fallback_rate: float = 0.0
    
    # LLM Judge
    faithfulness_llm: float = 0.0
    relevancy_llm: float = 0.0
    context_relevancy_llm: float = 0.0
    correctness_llm: float = 0.0
    hallucination_rate: float = 0.0
    
    # Summary
    total_queries: int = 0
    total_retrieved: int = 0
    total_relevant: int = 0
    method: str = "comprehensive"

    def to_dict(self) -> dict:
        return {
            "retrieval": {
                "precision_at_k": self.precision_at_k,
                "recall_at_k": self.recall_at_k,
                "mrr": self.mrr,
                "ndcg": self.ndcg,
                "map_at_k": self.map_at_k,
                "hit_at_1": self.hit_at_1,
                "hit_at_3": self.hit_at_3,
                "hit_at_5": self.hit_at_5,
                "hit_at_10": self.hit_at_10,
            },
            "context_chunk_level": {
                "precision": self.context_precision,
                "recall": self.context_recall,
            },
            "generation": {
                "overall_answer_accuracy": self.overall_answer_accuracy,
                "numerical_accuracy": self.numerical_accuracy,
                "entities_recall": self.entities_recall,
                "answer_correctness": self.answer_correctness,
                "faithfulness_word": self.faithfulness_word,
                "relevancy_word": self.relevancy_word,
            },
            "agent_tools": {
                "tool_selection_accuracy": self.tool_selection_accuracy,
                "tool_success_rate": self.tool_success_rate,
                "fallback_rate": self.fallback_rate,
            },
            "llm_judge": {
                "faithfulness": self.faithfulness_llm,
                "relevancy": self.relevancy_llm,
                "context_relevancy": self.context_relevancy_llm,
                "correctness": self.correctness_llm,
            },
            "hallucination_rate": self.hallucination_rate,
            "summary": {
                "total_queries": self.total_queries,
                "total_retrieved": self.total_retrieved,
                "total_relevant": self.total_relevant,
                "method": self.method,
            },
        }


class RAGEvaluator:
    """Comprehensive Evaluator for RAG & Agent systems."""
    
    def __init__(self, use_llm_judge: bool = True):
        self.metrics = RAGMetrics()
        self.use_llm_judge = use_llm_judge
        self.query_results: list[dict] = []
        
        if use_llm_judge:
            try:
                self.llm_judge = LLMJudge()
                self.metrics.method = "llm_judge"
            except Exception as e:
                logger.warning(f"LLM Judge unavailable: {e}")
                self.use_llm_judge = False
                self.metrics.method = "word_overlap"
    
    def evaluate(
        self,
        query: str,
        answer: str,
        context: str,
        retrieved_docs: List[str],
        relevant_docs: List[str],
        ground_truth: Optional[str] = None,
        expected_context: Optional[str] = None,
        expected_values: Optional[List[float]] = None,
        expected_tools: Optional[List[str]] = None,
        actual_tools: Optional[List[str]] = None,
        tool_calls_detail: Optional[List[dict]] = None,
        fallback_triggered: bool = False,
        k: int = 5,
    ) -> dict:
        """Run full evaluation suite for a single query."""
        # 1. Retrieval Metrics
        retrieval = self._evaluate_retrieval(retrieved_docs, relevant_docs, k)
        
        # 2. Context Metrics (Chunk-level)
        context_metrics = self._evaluate_context(retrieved_docs, relevant_docs, context, expected_context, k)
        
        # 3. Word-level Generation Metrics
        generation_word = self._evaluate_generation_word(query, answer, context, ground_truth)
        
        # 4. Financial Generation Metrics (Numerical & Entities)
        numerical_acc = calculate_numerical_accuracy(answer, ground_truth or "", expected_values=expected_values)
        entities_rec = calculate_entities_recall(answer, ground_truth or "")
        
        # 5. Agent & Tool Metrics
        tool_sel_acc = calculate_tool_selection_accuracy(actual_tools or [], expected_tools or [])
        tool_succ_rate = calculate_tool_success_rate(tool_calls_detail or [])
        fallback_rate = calculate_fallback_rate(fallback_triggered)
        
        # 6. LLM-as-Judge
        generation_llm = None
        correctness_score = None
        if self.use_llm_judge and ground_truth:
            try:
                generation_llm = self.llm_judge.evaluate_all(
                    question=query,
                    answer=answer,
                    context=context,
                    ground_truth=ground_truth,
                )
                correctness_score = generation_llm.get("correctness", {}).get("score")
            except Exception as e:
                logger.error(f"LLM Judge failed: {e}")
                
        # 7. Overall Answer Accuracy (binary 0 or 1)
        overall_acc = calculate_overall_answer_accuracy(
            correctness_score=correctness_score,
            numerical_acc=numerical_acc,
            entities_rec=entities_rec
        )
        
        result = {
            "retrieval": retrieval,
            "context_chunk_level": context_metrics,
            "generation_word": generation_word,
            "financial_accuracy": {
                "numerical_accuracy": numerical_acc,
                "entities_recall": entities_rec,
                "overall_answer_accuracy": overall_acc,
            },
            "agent_tools": {
                "tool_selection_accuracy": tool_sel_acc,
                "tool_success_rate": tool_succ_rate,
                "fallback_rate": fallback_rate,
            },
        }
        
        if generation_llm:
            result["generation_llm"] = generation_llm
            
        return result
    
    def _evaluate_retrieval(self, retrieved_docs: List[str], relevant_docs: List[str], k: int) -> dict:
        """Document-level retrieval metrics over unique sources (deduped, rank preserving)."""
        norm_retrieved = _dedupe_sources(retrieved_docs)[:k]
        norm_relevant = {normalize_source_name(d) for d in relevant_docs}
        
        if not norm_relevant:
            return {"precision": None, "doc_precision": None, "recall": None, "mrr": None, "ndcg": None,
                    "map_at_k": None, **{f"hit@{i}": None for i in (1, 3, 5, 10)}}

        overlap = len(set(norm_retrieved) & norm_relevant)
        precision = overlap / k  # standard P@k: relevant docs in top-k / k
        doc_precision = overlap / len(norm_retrieved) if norm_retrieved else None
        recall = overlap / len(norm_relevant)
        
        # MRR
        mrr = 0.0
        for rank, doc in enumerate(norm_retrieved, 1):
            if doc in norm_relevant:
                mrr = 1.0 / rank
                break
                
        # NDCG@K
        dcg = 0.0
        idcg = 0.0
        for rank, doc in enumerate(norm_retrieved, 1):
            rel = 1.0 if doc in norm_relevant else 0.0
            dcg += rel / math.log2(rank + 1)
        for rank in range(1, min(len(norm_relevant), k) + 1):
            idcg += 1.0 / math.log2(rank + 1)
        ndcg = (dcg / idcg) if idcg > 0 else 0.0
        
        # MAP@K
        map_k = calculate_map_at_k(retrieved_docs, relevant_docs, k)
        
        # Hit@K
        hits = calculate_hit_at_k(retrieved_docs, relevant_docs, [1, 3, 5, 10])
        
        res = {
            "precision": precision,
            "doc_precision": doc_precision,
            "recall": recall,
            "mrr": mrr,
            "ndcg": ndcg,
            "map_at_k": map_k,
        }
        res.update(hits)
        return res
    
    def _evaluate_context(
        self,
        retrieved_docs: List[str],
        relevant_docs: List[str],
        context: str,
        expected_context: Optional[str] = None,
        k: int = 5,
    ) -> dict:
        """Calculate Chunk-level Context Precision and Context Recall."""
        norm_retrieved = _dedupe_sources(retrieved_docs)[:k]
        norm_relevant = {normalize_source_name(d) for d in relevant_docs}
        
        if not norm_relevant:
            return {"precision": None, "recall": None}
        
        # Chunk-level Context Precision:
        # Standard RAGAS context precision = sum(P@k * is_rel(k)) / total_relevant_in_top_k
        weighted_prec_sum = 0.0
        rel_chunks_found = 0
        for i, doc in enumerate(norm_retrieved, 1):
            if doc in norm_relevant:
                rel_chunks_found += 1
                weighted_prec_sum += (rel_chunks_found / i)
                
        context_precision = (weighted_prec_sum / rel_chunks_found) if rel_chunks_found > 0 else 0.0
        context_recall = rel_chunks_found / len(norm_relevant) if norm_relevant else 1.0
        
        return {
            "precision": context_precision,
            "recall": min(context_recall, 1.0)
        }
    
    def _evaluate_generation_word(self, query: str, answer: str, context: str, ground_truth: Optional[str] = None) -> dict:
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        answer_words = set(re.findall(r'\b\w+\b', answer.lower()))
        context_words = set(re.findall(r'\b\w+\b', context.lower()))
        
        faithfulness = len(answer_words & context_words) / len(answer_words) if answer_words else 0.0
        relevancy = len(query_words & answer_words) / len(query_words) if query_words else 0.0
        
        return {
            "faithfulness": faithfulness,
            "relevancy": relevancy,
            "hallucination": 1.0 - faithfulness
        }
    
    def get_summary(self) -> RAGMetrics:
        return self.metrics
    
    def reset(self):
        self.metrics = RAGMetrics()

