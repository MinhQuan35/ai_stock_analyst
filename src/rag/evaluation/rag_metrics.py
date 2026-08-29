"""
RAG Metrics - Evaluate RAG pipeline quality
"""
import re
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RAGMetrics:
    """Container for RAG evaluation metrics."""
    
    # Retrieval metrics
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    mrr: float = 0.0
    ndcg: float = 0.0
    
    # Generation metrics
    faithfulness: float = 0.0
    relevancy: float = 0.0
    answer_correctness: float = 0.0
    
    # Context metrics
    context_precision: float = 0.0
    context_recall: float = 0.0
    
    # Hallucination
    hallucination_rate: float = 0.0
    
    # Summary
    total_queries: int = 0
    total_retrieved: int = 0
    total_relevant: int = 0
    
    def to_dict(self) -> dict:
        return {
            "retrieval": {
                "precision_at_k": round(self.precision_at_k, 4),
                "recall_at_k": round(self.recall_at_k, 4),
                "mrr": round(self.mrr, 4),
                "ndcg": round(self.ndcg, 4),
            },
            "generation": {
                "faithfulness": round(self.faithfulness, 4),
                "relevancy": round(self.relevancy, 4),
                "answer_correctness": round(self.answer_correctness, 4),
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
            },
        }


class RAGEvaluator:
    """Evaluate RAG system performance."""
    
    def __init__(self):
        self.metrics = RAGMetrics()
        self.query_results: list[dict] = []
    
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
        """
        Evaluate a single RAG query.
        
        Args:
            query: User query
            answer: Generated answer
            context: Combined context
            retrieved_docs: List of retrieved documents
            relevant_docs: List of relevant (ground truth) documents
            ground_truth: Expected answer
            expected_context: Expected context
            k: Top K for retrieval metrics
        """
        retrieval = self._evaluate_retrieval(retrieved_docs, relevant_docs, k)
        generation = self._evaluate_generation(query, answer, context, ground_truth)
        context_metrics = self._evaluate_context(query, context, expected_context)
        
        result = {
            "retrieval": retrieval,
            "generation": generation,
            "context": context_metrics,
            "overall_score": self._calculate_overall(retrieval, generation),
        }
        
        self._update_metrics(retrieval, generation, context_metrics, len(retrieved_docs), len(set(retrieved_docs) & set(relevant_docs)))
        self.query_results.append({"query": query, "result": result})
        
        return result
    
    def _evaluate_retrieval(
        self,
        retrieved_docs: List[str],
        relevant_docs: List[str],
        k: int,
    ) -> dict:
        """Evaluate retrieval quality."""
        retrieved_set = set(retrieved_docs[:k])
        relevant_set = set(relevant_docs)
        
        # Precision@K
        precision = len(retrieved_set & relevant_set) / len(retrieved_set) if retrieved_set else 0
        
        # Recall@K
        recall = len(retrieved_set & relevant_set) / len(relevant_set) if relevant_set else 0
        
        # MRR
        mrr = 0.0
        for i, doc in enumerate(retrieved_docs[:k]):
            if doc in relevant_set:
                mrr = 1.0 / (i + 1)
                break
        
        # NDCG
        ndcg = self._calculate_ndcg(retrieved_docs[:k], relevant_docs, k)
        
        return {
            "precision": precision,
            "recall": recall,
            "mrr": mrr,
            "ndcg": ndcg,
        }
    
    def _evaluate_generation(
        self,
        query: str,
        answer: str,
        context: str,
        ground_truth: Optional[str] = None,
    ) -> dict:
        """Evaluate generation quality."""
        query_words = self._tokenize(query)
        answer_words = self._tokenize(answer)
        context_words = self._tokenize(context)
        
        # Faithfulness: answer words that appear in context
        faithfulness = (
            len(answer_words & context_words) / len(answer_words) 
            if answer_words else 0
        )
        
        # Relevancy: query words in answer
        relevancy = (
            len(query_words & answer_words) / len(query_words) 
            if query_words else 0
        )
        
        # Correctness
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
        self,
        query: str,
        context: str,
        expected_context: Optional[str] = None,
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
    
    def _calculate_overall(self, retrieval: dict, generation: dict) -> float:
        """Calculate overall score."""
        retrieval_score = (
            retrieval["precision"] + retrieval["recall"] + retrieval["mrr"]
        ) / 3
        generation_score = (
            generation["faithfulness"] + generation["relevancy"]
        ) / 2
        
        return (retrieval_score * 0.4) + (generation_score * 0.6)
    
    def _update_metrics(
        self, retrieval: dict, generation: dict, context: dict,
        total_retrieved: int, total_relevant: int,
    ):
        """Update running averages."""
        n = self.metrics.total_queries
        n_new = n + 1
        
        self.metrics.precision_at_k = self._running_avg(self.metrics.precision_at_k, retrieval["precision"], n)
        self.metrics.recall_at_k = self._running_avg(self.metrics.recall_at_k, retrieval["recall"], n)
        self.metrics.mrr = self._running_avg(self.metrics.mrr, retrieval["mrr"], n)
        self.metrics.ndcg = self._running_avg(self.metrics.ndcg, retrieval["ndcg"], n)
        self.metrics.faithfulness = self._running_avg(self.metrics.faithfulness, generation["faithfulness"], n)
        self.metrics.relevancy = self._running_avg(self.metrics.relevancy, generation["relevancy"], n)
        self.metrics.answer_correctness = self._running_avg(self.metrics.answer_correctness, generation["correctness"], n)
        self.metrics.context_precision = self._running_avg(self.metrics.context_precision, context["precision"], n)
        self.metrics.context_recall = self._running_avg(self.metrics.context_recall, context["recall"], n)
        self.metrics.hallucination_rate = self._running_avg(self.metrics.hallucination_rate, generation["hallucination"], n)
        
        self.metrics.total_queries = n_new
        self.metrics.total_retrieved += total_retrieved
        self.metrics.total_relevant += total_relevant
    
    def _running_avg(self, current_avg: float, new_value: float, n: int) -> float:
        """Calculate running average."""
        if n == 0:
            return new_value
        return (current_avg * n + new_value) / (n + 1)
    
    def _tokenize(self, text: str) -> set:
        """Simple tokenization."""
        return set(re.findall(r'\b\w+\b', text.lower()))
    
    def get_summary(self) -> RAGMetrics:
        """Get current metrics."""
        return self.metrics
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = RAGMetrics()
        self.query_results = []
    
    def print_summary(self):
        """Print metrics summary."""
        m = self.metrics
        print("\n" + "=" * 50)
        print("  RAG METRICS SUMMARY")
        print("=" * 50)
        print(f"\n  [Retrieval]")
        print(f"    Precision@K:  {m.precision_at_k:.2%}")
        print(f"    Recall@K:     {m.recall_at_k:.2%}")
        print(f"    MRR:          {m.mrr:.4f}")
        print(f"    NDCG:         {m.ndcg:.4f}")
        print(f"\n  [Generation]")
        print(f"    Faithfulness:       {m.faithfulness:.2%}")
        print(f"    Relevancy:          {m.relevancy:.2%}")
        print(f"    Answer Correctness: {m.answer_correctness:.2%}")
        print(f"\n  [Context]")
        print(f"    Precision:  {m.context_precision:.2%}")
        print(f"    Recall:     {m.context_recall:.2%}")
        print(f"\n  [Quality]")
        print(f"    Hallucination Rate: {m.hallucination_rate:.2%}")
        print(f"\n  [Summary]")
        print(f"    Total Queries:   {m.total_queries}")
        print(f"    Total Retrieved: {m.total_retrieved}")
        print(f"    Total Relevant:  {m.total_relevant}")
        print("=" * 50)
