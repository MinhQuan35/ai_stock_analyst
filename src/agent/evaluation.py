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
        """Evaluate correctness vs ground truth."""
        criteria = f"""**Correctness (0-1)**: Is the answer CORRECT compared to ground truth: {ground_truth}"""
        return self._evaluate(question, answer, "N/A", criteria)
    
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


@dataclass
class RAGMetrics:
    """Container for RAG evaluation metrics."""
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    mrr: float = 0.0
    ndcg: float = 0.0
    faithfulness_word: float = 0.0
    relevancy_word: float = 0.0
    answer_correctness: float = 0.0
    faithfulness_llm: float = 0.0
    relevancy_llm: float = 0.0
    context_relevancy_llm: float = 0.0
    correctness_llm: float = 0.0
    context_precision: float = 0.0
    context_recall: float = 0.0
    hallucination_rate: float = 0.0
    total_queries: int = 0
    total_retrieved: int = 0
    total_relevant: int = 0
    method: str = "word_overlap"

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
    """Evaluate RAG system performance."""
    
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
        k: int = 5,
    ) -> dict:
        retrieval = self._evaluate_retrieval(retrieved_docs, relevant_docs, k)
        generation_word = self._evaluate_generation_word(query, answer, context, ground_truth)
        context_metrics = self._evaluate_context(query, context, expected_context)
        
        result = {
            "retrieval": retrieval,
            "generation_word": generation_word,
            "context": context_metrics,
        }
        
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
        
        return result
    
    def _evaluate_retrieval(self, retrieved_docs: List[str], relevant_docs: List[str], k: int) -> dict:
        retrieved_set = set(retrieved_docs[:k])
        relevant_set = set(relevant_docs)
        precision = len(retrieved_set & relevant_set) / len(retrieved_set) if retrieved_set else 0
        recall = len(retrieved_set & relevant_set) / len(relevant_set) if relevant_set else 0
        return {"precision": precision, "recall": recall, "mrr": 0.0, "ndcg": 0.0}
    
    def _evaluate_generation_word(self, query: str, answer: str, context: str, ground_truth: Optional[str] = None) -> dict:
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        answer_words = set(re.findall(r'\b\w+\b', answer.lower()))
        context_words = set(re.findall(r'\b\w+\b', context.lower()))
        
        faithfulness = len(answer_words & context_words) / len(answer_words) if answer_words else 0
        relevancy = len(query_words & answer_words) / len(query_words) if query_words else 0
        
        return {"faithfulness": faithfulness, "relevancy": relevancy, "correctness": 0.0, "hallucination": 1.0 - faithfulness}
    
    def _evaluate_context(self, query: str, context: str, expected_context: Optional[str] = None) -> dict:
        return {"precision": 0.0, "recall": 0.0}
    
    def get_summary(self) -> RAGMetrics:
        return self.metrics
    
    def reset(self):
        self.metrics = RAGMetrics()
