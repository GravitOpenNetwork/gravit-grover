"""
Coherence Validator Module
==========================
Validates hypothesis coherence using LLM evaluation.
"""

import json
from typing import List, Dict, Any, Optional
import numpy as np


class CoherenceValidator:
    """
    Validates coherence of hypotheses.
    """

    def __init__(self,
                 use_openai: bool = False,
                 api_key: Optional[str] = None,
                 model: str = "gpt-4",
                 coherence_threshold: float = 0.5):

        self.use_openai = use_openai
        self.api_key = api_key
        self.model = model
        self.coherence_threshold = coherence_threshold

        if use_openai:
            import openai
            self.client = openai.OpenAI(api_key=api_key)

    def validate_coherence(self,
                          hypothesis: str,
                          context: Optional[str] = None) -> float:
        """
        Validate coherence of a hypothesis.
        """
        if self.use_openai:
            return self._validate_openai(hypothesis, context)
        else:
            return self._validate_heuristic(hypothesis, context)

    def validate_batch(self,
                      hypotheses: List[str],
                      context: Optional[str] = None) -> List[float]:
        """
        Validate coherence of multiple hypotheses.
        """
        return [self.validate_coherence(h, context) for h in hypotheses]

    def _validate_openai(self,
                        hypothesis: str,
                        context: Optional[str] = None) -> float:
        """
        Validate coherence using OpenAI.
        """
        prompt = f"""
        Evaluate the coherence of this hypothesis on a scale of 0-1:

        Hypothesis: {hypothesis}

        Coherence criteria:
        - Logical consistency
        - Internal consistency
        - Factual plausibility
        - Clarity

        Provide only a number between 0 and 1.
        """

        if context:
            prompt = f"Context: {context}\n\n{prompt}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert coherence validator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10
        )

        try:
            score = float(response.choices[0].message.content.strip())
            return np.clip(score, 0.0, 1.0)
        except:
            return 0.5

    def _validate_heuristic(self,
                           hypothesis: str,
                           context: Optional[str] = None) -> float:
        """
        Validate coherence using heuristic rules.
        """
        score = 0.5

        # Length heuristic
        if len(hypothesis) > 20:
            score += 0.1

        # Word variety heuristic
        words = hypothesis.split()
        unique_words = len(set(words))
        if len(words) > 0 and unique_words / len(words) > 0.5:
            score += 0.1

        # Sentence structure heuristic
        if '.' in hypothesis or '?' in hypothesis:
            score += 0.1

        # Context coherence (if provided)
        if context:
            # Check if key terms from context appear in hypothesis
            context_words = set(context.lower().split())
            hypothesis_words = set(hypothesis.lower().split())
            overlap = len(context_words & hypothesis_words)
            if overlap > 0:
                score += min(0.2, overlap / 10)

        return np.clip(score, 0.0, 1.0)

    def get_coherence_report(self,
                           hypotheses: List[str],
                           context: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed coherence report.
        """
        scores = self.validate_batch(hypotheses, context)

        report = {
            'n_hypotheses': len(hypotheses),
            'scores': scores,
            'average_score': np.mean(scores),
            'std_score': np.std(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'valid': [s >= self.coherence_threshold for s in scores],
            'valid_count': sum(s >= self.coherence_threshold for s in scores)
        }

        # Identify best and worst hypotheses
        if hypotheses:
            best_idx = np.argmax(scores)
            worst_idx = np.argmin(scores)
            report['best_hypothesis'] = hypotheses[best_idx]
            report['best_score'] = scores[best_idx]
            report['worst_hypothesis'] = hypotheses[worst_idx]
            report['worst_score'] = scores[worst_idx]

        return report

    def filter_coherent(self,
                       hypotheses: List[str],
                       context: Optional[str] = None,
                       threshold: Optional[float] = None) -> List[str]:
        """
        Filter hypotheses by coherence threshold.
        """
        if threshold is None:
            threshold = self.coherence_threshold

        scores = self.validate_batch(hypotheses, context)
        return [h for h, s in zip(hypotheses, scores) if s >= threshold]

    def rank_by_coherence(self,
                         hypotheses: List[str],
                         context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Rank hypotheses by coherence.
        """
        scores = self.validate_batch(hypotheses, context)

        # Sort by score
        pairs = list(zip(hypotheses, scores))
        pairs.sort(key=lambda x: x[1], reverse=True)

        return [
            {'hypothesis': h, 'coherence': s}
            for h, s in pairs
        ]
