"""
OpenAI Generator Module
=======================
Implements hypothesis generation using OpenAI API.
"""

import os
import json
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI


class OpenAIGenerator:
    """
    Generates hypotheses using OpenAI API.
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "gpt-4",
                 temperature: float = 0.7,
                 max_tokens: int = 500,
                 n_hypotheses: int = 5):

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n_hypotheses = n_hypotheses

    def generate_hypotheses(self,
                           prompt: str,
                           context: Optional[str] = None,
                           n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate hypotheses using OpenAI.
        """
        n = n or self.n_hypotheses

        # Prepare messages
        messages = [
            {"role": "system", "content": "You are an expert hypothesis generator. Generate diverse, well-reasoned hypotheses."},
            {"role": "user", "content": prompt}
        ]

        if context:
            messages.insert(1, {"role": "system", "content": f"Context: {context}"})

        # Add instruction for multiple hypotheses
        messages.append({
            "role": "user",
            "content": f"Generate {n} distinct hypotheses. Format as JSON array with 'hypothesis' and 'confidence' fields."
        })

        # Generate
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            n=1
        )

        # Parse response
        content = response.choices[0].message.content

        try:
            # Try to parse as JSON
            hypotheses = json.loads(content)
            if isinstance(hypotheses, dict):
                hypotheses = [hypotheses]
        except json.JSONDecodeError:
            # Fallback: split by newline and parse
            lines = content.strip().split('\n')
            hypotheses = []
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    hypotheses.append({
                        'hypothesis': line.strip(),
                        'confidence': 0.5
                    })

        # Ensure we have the right number
        if len(hypotheses) > n:
            hypotheses = hypotheses[:n]
        elif len(hypotheses) < n:
            # Add additional variations
            for i in range(n - len(hypotheses)):
                hypotheses.append({
                    'hypothesis': f"Alternative hypothesis {i+1}",
                    'confidence': 0.3
                })

        # Format results
        results = []
        for i, h in enumerate(hypotheses):
            results.append({
                'id': f"hyp_{i+1}",
                'content': h.get('hypothesis', h.get('content', str(h))),
                'confidence': h.get('confidence', 0.5),
                'source': 'openai',
                'model': self.model,
                'metadata': {
                    'temperature': self.temperature,
                    'max_tokens': self.max_tokens
                }
            })

        return results

    def evaluate_hypothesis(self,
                           hypothesis: str,
                           criteria: List[str]) -> Dict[str, float]:
        """
        Evaluate a hypothesis using OpenAI.
        """
        prompt = f"""
        Evaluate the following hypothesis based on these criteria: {', '.join(criteria)}

        Hypothesis: {hypothesis}

        Provide scores (0-1) for each criterion in JSON format.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )

        try:
            scores = json.loads(response.choices[0].message.content)
            return scores
        except:
            # Fallback: return default scores
            return {c: 0.5 for c in criteria}

    def refine_hypothesis(self,
                         hypothesis: str,
                         feedback: str) -> str:
        """
        Refine a hypothesis based on feedback.
        """
        prompt = f"""
        Refine the following hypothesis based on this feedback:

        Hypothesis: {hypothesis}
        Feedback: {feedback}

        Provide the refined hypothesis.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert hypothesis refiner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()
