"""
Local Generator Module
======================
Implements hypothesis generation using HuggingFace models.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any, Optional


class LocalGenerator:
    """
    Generates hypotheses using local HuggingFace models.
    """

    def __init__(self,
                 model_name: str = "gpt2",
                 device: str = "cuda" if torch.cuda.is_available() else "cpu",
                 temperature: float = 0.7,
                 max_length: int = 500,
                 n_hypotheses: int = 5):

        self.model_name = model_name
        self.device = device
        self.temperature = temperature
        self.max_length = max_length
        self.n_hypotheses = n_hypotheses

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.to(device)

        # Add padding token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_hypotheses(self,
                           prompt: str,
                           context: Optional[str] = None,
                           n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate hypotheses using local model.
        """
        n = n or self.n_hypotheses

        # Prepare prompt
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\n{prompt}"

        # Add instruction for multiple hypotheses
        full_prompt += f"\n\nGenerate {n} distinct hypotheses:"

        # Tokenize
        inputs = self.tokenizer(full_prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate
        outputs = self.model.generate(
            **inputs,
            max_length=self.max_length,
            temperature=self.temperature,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            do_sample=True,
            num_return_sequences=n
        )

        # Decode outputs
        hypotheses = []
        for i, output in enumerate(outputs):
            text = self.tokenizer.decode(output, skip_special_tokens=True)
            # Extract hypothesis (take text after prompt)
            hypothesis_text = text[len(full_prompt):].strip()

            if not hypothesis_text:
                hypothesis_text = f"Hypothesis {i+1}"

            hypotheses.append({
                'id': f"hyp_{i+1}",
                'content': hypothesis_text,
                'confidence': 0.5 + 0.3 * (i / n),  # Confidence increases with rank
                'source': 'local',
                'model': self.model_name,
                'metadata': {
                    'temperature': self.temperature,
                    'max_length': self.max_length
                }
            })

        return hypotheses

    def generate_with_beam_search(self,
                                 prompt: str,
                                 beam_width: int = 5,
                                 context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate hypotheses using beam search.
        """
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\n{prompt}"

        full_prompt += "\n\nGenerate hypotheses:"

        # Tokenize
        inputs = self.tokenizer(full_prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate with beam search
        outputs = self.model.generate(
            **inputs,
            max_length=self.max_length,
            num_beams=beam_width,
            num_return_sequences=beam_width,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )

        # Decode outputs
        hypotheses = []
        for i, output in enumerate(outputs):
            text = self.tokenizer.decode(output, skip_special_tokens=True)
            hypothesis_text = text[len(full_prompt):].strip()

            hypotheses.append({
                'id': f"hyp_{i+1}",
                'content': hypothesis_text or f"Hypothesis {i+1}",
                'confidence': 0.7 - 0.05 * i,
                'source': 'local_beam',
                'model': self.model_name,
                'metadata': {
                    'beam_width': beam_width,
                    'max_length': self.max_length
                }
            })

        return hypotheses

    def evaluate_hypothesis(self,
                           hypothesis: str,
                           criteria: List[str]) -> Dict[str, float]:
        """
        Evaluate a hypothesis using the model.
        """
        prompt = f"""
        Evaluate this hypothesis: {hypothesis}
        Criteria: {', '.join(criteria)}
        Provide scores (0-1) for each criterion.
        """

        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Simple evaluation: use model to generate scores
        # This is a placeholder - in practice, would use a more sophisticated method
        scores = {c: 0.5 + 0.3 * (i / len(criteria)) for i, c in enumerate(criteria)}

        return scores

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        """
        return {
            'model_name': self.model_name,
            'device': self.device,
            'vocab_size': self.model.config.vocab_size,
            'hidden_size': self.model.config.hidden_size,
            'num_parameters': sum(p.numel() for p in self.model.parameters())
        }
