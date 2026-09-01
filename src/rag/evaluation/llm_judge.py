"""
LLM-as-Judge for RAG evaluation
Inspired by RAGAS paper: "Automated Evaluation of Retrieval Augmented Generation"
"""
import json
import re
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage

from src.llm import get_chat_model
from src.utils import logger


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
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return float(data.get("score", 0)), data.get("reason", "")
            
            # Fallback: find any number
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
        """Evaluate faithfulness (no hallucination)."""
        criteria = """**Faithfulness (0-1)**: Is the answer GROUNDED in the context? 
        - 1.0: All claims supported by context
        - 0.5: Some claims supported, some hallucinated
        - 0.0: Mostly hallucinated, contradicts context"""
        return self._evaluate(question, answer, context, criteria)
    
    def answer_relevancy(self, question: str, answer: str) -> tuple[float, str]:
        """Evaluate answer relevancy to question."""
        criteria = """**Answer Relevancy (0-1)**: Does the answer ADDRESS the question?
        - 1.0: Perfectly addresses the question
        - 0.5: Partially addresses
        - 0.0: Off-topic or doesn't address"""
        return self._evaluate(question, answer, "N/A", criteria)
    
    def context_relevancy(self, question: str, context: str) -> tuple[float, str]:
        """Evaluate context relevancy to question."""
        criteria = """**Context Relevancy (0-1)**: Is the context RELEVANT to the question?
        - 1.0: All context is relevant
        - 0.5: Half relevant
        - 0.0: Irrelevant context"""
        return self._evaluate(question, "N/A", context, criteria)
    
    def correctness(self, question: str, answer: str, ground_truth: str) -> tuple[float, str]:
        """Evaluate answer correctness vs ground truth."""
        criteria = f"""**Correctness (0-1)**: Is the answer CORRECT compared to ground truth?
        Ground truth: {ground_truth}
        - 1.0: Perfectly correct
        - 0.5: Partially correct
        - 0.0: Incorrect or contradicts"""
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
        
        # Faithfulness
        score, reason = self.faithfulness(question, answer, context)
        results["faithfulness"] = {"score": score, "reason": reason}
        
        # Answer Relevancy
        score, reason = self.answer_relevancy(question, answer)
        results["answer_relevancy"] = {"score": score, "reason": reason}
        
        # Context Relevancy
        score, reason = self.context_relevancy(question, context)
        results["context_relevancy"] = {"score": score, "reason": reason}
        
        # Correctness (if ground truth provided)
        if ground_truth:
            score, reason = self.correctness(question, answer, ground_truth)
            results["correctness"] = {"score": score, "reason": reason}
        
        return results
