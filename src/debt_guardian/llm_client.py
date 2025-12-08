"""
Ollama LLM client for DebtGuardian.

This module integrates with Ollama to use Qwen2.5-Coder:7b locally.
"""
import json
import logging
from typing import Dict, Any, Optional, List
import ollama

from debt_guardian.config import DebtGuardianConfig
from debt_guardian.schemas.td_schema import TechnicalDebtInstance, TechnicalDebtReport

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with Ollama LLM.
    
    Uses Qwen2.5-Coder:7b which achieved 77% recall in the study.
    """
    
    def __init__(self, config: DebtGuardianConfig):
        self.config = config
        self.client = ollama.Client(host=config.ollama_base_url)
        self._verify_model_available()
    
    def _verify_model_available(self):
        """Verify that the required model is available in Ollama"""
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            if self.config.llm_model not in model_names:
                logger.warning(
                    f"Model {self.config.llm_model} not found. "
                    f"Available models: {model_names}. "
                    f"Please run: ollama pull {self.config.llm_model}"
                )
        except Exception as e:
            logger.error(f"Failed to verify Ollama model availability: {e}")
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.config.ollama_base_url}. "
                f"Please ensure Ollama is running."
            )
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a completion using the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            temperature: Override config temperature
            max_tokens: Override config max tokens
            
        Returns:
            Generated text response
        """
        options = {
            'temperature': temperature or self.config.temperature,
            'num_predict': max_tokens or self.config.max_tokens,
        }
        
        messages = []
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        try:
            response = self.client.chat(
                model=self.config.llm_model,
                messages=messages,
                options=options
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating response from Ollama: {e}")
            raise
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        expected_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a structured response (JSON format).
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            expected_format: Expected format (currently only 'json')
            
        Returns:
            Parsed JSON response as dictionary
        """
        # Add JSON format instruction to prompt
        json_instruction = (
            "\n\nIMPORTANT: Return your response as valid JSON only. "
            "Do not include any markdown formatting or explanations. "
            "Just the raw JSON object."
        )
        
        full_prompt = prompt + json_instruction
        
        response_text = self.generate(
            full_prompt,
            system_prompt=system_prompt
        )
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response_text}")
            raise ValueError(
                f"LLM did not return valid JSON. Response: {response_text[:200]}..."
            )
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is healthy and model is available.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            self._verify_model_available()
            
            # Try a simple generation
            response = self.generate(
                "Respond with 'OK' if you can read this.",
                temperature=0.0
            )
            
            return 'ok' in response.lower()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
