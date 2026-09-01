"""
RAG Metrics - Evaluate RAG pipeline quality
Supports: Word overlap, LLM-as-Judge (RAGAS-style)
"""
import re
import math
from dataclasses import dataclass, field
from typing import List, Optional, Literal

from src.rag.evaluation.llm_judge import LLMJudge
from src.utils import logger


@dataclass
class RAGMetrics:
    """Container for RAG evaluation metrics."""
    
    # Retrieval metrics (traditional)
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    mrr: float = 0.0
    ndcg: float = 0.0
    
    # Generation metrics (word overlap)
    faithfulness_word: float = 0.0
    relevancy_word: float = 0.0
    answer_correctness: float = 0.0
    
    # LLM-as-Judge metrics (RAGAS-style)
    faithfulness_llm: float = 0.0
    relevancy_llm: float = 0.0
    context_relevancy_llm: float = 0.0
    correctness_llm: float = 0.0
    
    # Context metrics
    context_precision: float = 0.0
    context_recall: float = 0.0
    
    # Hallucination
    hallucination_rate: float = 0.0
    
    # Summary
    total_queries: int = 0
    total_retrieved: int = 0
    total_relevant: int = 0
    method: str = "word_overlap"  # or "llm_judge"
    
    def to_dict(self) -> dict:
        return {
            "retrieval": {
                "precision_at_k": round(self.precision_at_k, 4),
                "recall_at_k": round(self.recall_at_k, 4),
                "mrr": round(self.mrr, 4),
                "ndcg": round(self.ndcg, 4),
            },
            "generation": {
                "faithfulness_word": round(self.faithfulness_word, 4),
                "relevancy_word": round(self.relevancy_word, 4),
                "answer_correctness": round(self.answer_correctness, 4),
            },
            "llm_judge": {
                "faithfulness": round(self.faithfulness_llm, 4),
                "relevancy": round(self.relevancy_llm, 4),
                "context_relevancy": round(self.context_relevancy_llm, 4),
                "correctness": round(self.correctness_llm, 4),
            },
            "context": {
                "precision": round(self.context_precision, 4),
                "recall": round(self.context_recall, 4),
            },
            "hallucination_rate": round(self.hallucination_rate, 4),
            "summary": {
                "total_queries": self.total_queries,
                "total_retrieved": self.total_retrieved,
                "total_relevant": self.total_relevant,
                "method": self.method,
            },
        }


class RAGEvaluator:
    """Evaluate RAG system performance with multiple methods."""
    
    def __init__(self, use_llm_judge: bool = True):
        """Initialize evaluator."""
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
        k: int = 5,
    ) -> dict:
        """Evaluate a single RAG query."""
        # Traditional metrics (always computed)
        retrieval = self._evaluate_retrieval(retrieved_docs, relevant_docs, k)
        generation_word = self._evaluate_generation_word(query, answer, context, ground_truth)
        context_metrics = self._evaluate_context(query, context, expected_context)
        
        result = {
            "retrieval": retrieval,
            "generation_word": generation_word,
            "context": context_metrics,
        }
        
        # LLM-as-Judge (if enabled)
        generation_llm = None
        if self.use_llm_judge:
            try:
                generation_llm = self.llm_judge.evaluate_all(
                    question=query,
                    answer=answer,
                    context=context,
                    ground_truth=ground_truth,
                )
                result["generation_llm"] = generation_llm
            except Exception as e:
                logger.error(f"LLM Judge failed: {e}")
        
        result["overall_score"] = self._calculate_overall(retrieval, generation_word, generation_llm)
        
        self._update_metrics(retrieval, generation_word, context_metrics, 
                            generation_llm, len(retrieved_docs), 
                            len(set(retrieved_docs) & set(relevant_docs)))
        self.query_results.append({"query": query, "result": result})
        
        return result
    
    def _evaluate_retrieval(
        self, retrieved_docs: List[str], relevant_docs: List[str], k: int,
    ) -> dict:
        """Evaluate retrieval quality (word-based)."""
        retrieved_set = set(retrieved_docs[:k])
        relevant_set = set(relevant_docs)
        
        precision = len(retrieved_set & relevant_set) / len(retrieved_set) if retrieved_set else 0
        recall = len(retrieved_set & relevant_set) / len(relevant_set) if relevant_set else 0
        
        mrr = 0.0
        for i, doc in enumerate(retrieved_docs[:k]):
            if doc in relevant_set:
                mrr = 1.0 / (i + 1)
                break
        
        ndcg = self._calculate_ndcg(retrieved_docs[:k], relevant_docs, k)
        
        return {"precision": precision, "recall": recall, "mrr": mrr, "ndcg": ndcg}
    
    def _evaluate_generation_word(
        self, query: str, answer: str, context: str, ground_truth: Optional[str] = None,
    ) -> dict:
        """Evaluate generation quality (word overlap)."""
        query_words = self._tokenize(query)
        answer_words = self._tokenize(answer)
        context_words = self._tokenize(context)
        
        faithfulness = (
            len(answer_words & context_words) / len(answer_words) 
            if answer_words else 0
        )
        relevancy = (
            len(query_words & answer_words) / len(query_words) 
            if query_words else 0
        )
        
        correctness = 0.0
        if ground_truth:
            truth_words = self._tokenize(ground_truth)
            correctness = (
                len(answer_words & truth_words) / len(truth_words) 
                if truth_words else 0
            )
        
        return {
            "faithfulness": faithfulness,
            "relevancy": relevancy,
            "correctness": correctness,
            "hallucination": 1.0 - faithfulness,
        }
    
    def _evaluate_context(
        self, query: str, context: str, expected_context: Optional[str] = None,
    ) -> dict:
        """Evaluate context quality."""
        query_words = self._tokenize(query)
        context_words = self._tokenize(context)
        
        precision = (
            len(query_words & context_words) / len(context_words)
            if context_words else 0
        )
        
        recall = 0.0
        if expected_context:
            expected_words = self._tokenize(expected_context)
            recall = (
                len(context_words & expected_words) / len(expected_words)
                if expected_words else 0
            )
        
        return {"precision": precision, "recall": recall}
    
    def _calculate_ndcg(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calculate NDCG@K."""
        relevant_set = set(relevant)
        dcg = 0.0
        for i, doc in enumerate(retrieved[:k]):
            if doc in relevant_set:
                dcg += 1.0 / math.log2(i + 2)
        
        ideal_relevant = min(len(relevant_set), k)
        idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_relevant))
        return dcg / idcg if idcg > 0 else 0.0
    
    def _calculate_overall(
        self, retrieval: dict, generation_word: dict, generation_llm: Optional[dict] = None,
    ) -> float:
        """Calculate overall score."""
        retrieval_score = (
            retrieval["precision"] + retrieval["recall"] + retrieval["mrr"]
        ) / 3
        
        # Use LLM judge if available, else word overlap
        if generation_llm:
            gen_score = (
                generation_llm["faithfulness"]["score"] + 
                generation_llm["answer_relevancy"]["score"]
            ) / 2
        else:
            gen_score = (
                generation_word["faithfulness"] + generation_word["relevancy"]
            ) / 2
        
        return (retrieval_score * 0.4) + (gen_score * 0.6)
    
    def _update_metrics(
        self, retrieval: dict, generation_word: dict, context: dict,
        generation_llm: Optional[dict], total_retrieved: int, total_relevant: int,
    ):
        """Update running averages."""
        n = self.metrics.total_queries
        
        # Retrieval
        self.metrics.precision_at_k = self._avg(self.metrics.precision_at_k, retrieval["precision"], n)
        self.metrics.recall_at_k = self._avg(self.metrics.recall_at_k, retrieval["recall"], n)
        self.metrics.mrr = self._avg(self.metrics.mrr, retrieval["mrr"], n)
        self.metrics.ndcg = self._avg(self.metrics.ndcg, retrieval["ndcg"], n)
        
        # Generation (word)
        self.metrics.faithfulness_word = self._avg(self.metrics.faithfulness_word, generation_word["faithfulness"], n)
        self.metrics.relevancy_word = self._avg(self.metrics.relevancy_word, generation_word["relevancy"], n)
        self.metrics.answer_correctness = self._avg(self.metrics.answer_correctness, generation_word["correctness"], n)
        
        # LLM Judge
        if generation_llm:
            self.metrics.faithfulness_llm = self._avg(self.metrics.faithfulness_llm, generation_llm["faithfulness"]["score"], n)
            self.metrics.relevancy_llm = self._avg(self.metrics.relevancy_llm, generation_llm["answer_relevancy"]["score"], n)
            self.metrics.context_relevancy_llm = self._avg(self.metrics.context_relevancy_llm, generation_llm["context_relevancy"]["score"], n)
            self.metrics.correctness_llm = self._avg(self.metrics.correctness_llm, generation_llm.get("correctness", {}).get("score", 0), n)
        
        # Context
        self.metrics.context_precision = self._avg(self.metrics.context_precision, context["precision"], n)
        self.metrics.context_recall = self._avg(self.metrics.context_recall, context["recall"], n)
        
        # Hallucination
        self.metrics.hallucination_rate = self._avg(self.metrics.hallucination_rate, generation_word["hallucination"], n)
        
        self.metrics.total_queries = n + 1
        self.metrics.total_retrieved += total_retrieved
        self.metrics.total_relevant += total_relevant
    
    def _avg(self, current: float, new: float, n: int) -> float:
        """Running average."""
        if n == 0:
            return new
        return (current * n + new) / (n + 1)
    
    def _tokenize(self, text: str) -> set:
        """Simple tokenization."""
        return set(re.findall(r'\b\w+\b', text.lower()))
    
    def get_summary(self) -> RAGMetrics:
        """Get current metrics."""
        return self.metrics
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = RAGMetrics()
        self.metrics.method = "llm_judge" if self.use_llm_judge else "word_overlap"
        self.query_results = []
    
    def print_summary(self):
        """Print metrics summary."""
        m = self.metrics
        print("\n" + "=" * 60)
        print("  RAG METRICS SUMMARY")
        print(f"  Method: {m.method.upper()}")
        print("=" * 60)
        
        print("\n  [Retrieval]")
        print(f"    Precision@K:  {m.precision_at_k:.2%}")
        print(f"    Recall@K:     {m.recall_at_k:.2%}")
        print(f"    MRR:          {m.mrr:.4f}")
        print(f"    NDCG:         {m.ndcg:.4f}")
        
        print("\n  [Generation - Word Overlap]")
        print(f"    Faithfulness:       {m.faithfulness_word:.2%}")
        print(f"    Relevancy:          {m.relevancy_word:.2%}")
        print(f"    Answer Correctness: {m.answer_correctness:.2%}")
        
        if self.use_llm_judge:
            print("\n  [Generation - LLM Judge (RAGAS)]")
            print(f"    Faithfulness:       {m.faithfulness_llm:.2%}")
            print(f"    Relevancy:          {m.relevancy_llm:.2%}")
            print(f"    Context Relevancy:  {m.context_relevancy_llm:.2%}")
            print(f"    Correctness:        {m.correctness_llm:.2%}")
        
        print("\n  [Context]")
        print(f"    Precision:  {m.context_precision:.2%}")
        print(f"    Recall:     {m.context_recall:.2%}")
        
        print("\n  [Quality]")
        print(f"    Hallucination Rate: {m.hallucination_rate:.2%}")
        
        print(f"\n  [Summary]")
        print(f"    Total Queries:   {m.total_queries}")
        print(f"    Total Retrieved: {m.total_retrieved}")
        print(f"    Total Relevant:  {m.total_relevant}")
        print("=" * 60)
