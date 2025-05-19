"""
Real LLM Enhancer that uses DeepSeek to enhance prompts.
This replaces the simulated LLM enhancer with a real model.
"""

import logging
import os
import torch
from typing import Dict, List, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer

class DeepSeekLLMEnhancer:
    """
    Real LLM enhancer that uses DeepSeek to enhance and expand user prompts.
    
    Attributes:
        model: The DeepSeek language model
        tokenizer: The tokenizer for the model
        device: The device to run the model on (cuda or cpu)
    """
    
    def __init__(
        self, 
        model_name_or_path: str = "deepseek-ai/deepseek-coder-6.7b-instruct",
        device: Optional[str] = None,
        use_4bit: bool = True  # Use 4-bit quantization for memory efficiency
    ):
        """
        Initialize the DeepSeek LLM enhancer.
        
        Args:
            model_name_or_path: The model name or path to load
            device: The device to use for inference (cuda or cpu)
            use_4bit: Whether to use 4-bit quantization
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logging.info(f"Initializing DeepSeek LLM on {self.device}")
        
        if use_4bit and self.device == 'cuda':
            # Use 4-bit quantization for memory efficiency
            logging.info("Using 4-bit quantization")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                torch_dtype=torch.float16,
                load_in_4bit=True,
                device_map="auto"
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                device_map="auto" if self.device == 'cuda' else None
            )
            if self.device != 'cuda':
                self.model.to(self.device)
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        
        # Test the model with a simple prompt
        logging.info("Testing DeepSeek model with a simple prompt")
        self._test_model()
    
    def _test_model(self):
        """Test the model with a simple prompt."""
        try:
            result = self.enhance_prompt("A cat")
            logging.info(f"Test result: {result}")
        except Exception as e:
            logging.error(f"Error testing model: {e}")
    
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a user prompt with additional details for better image generation.
        
        Args:
            prompt: The user's original prompt
            
        Returns:
            str: Enhanced prompt with additional details
        """
        # Create a system message explaining the task
        system_message = """You are a creative prompt engineer for image generation. 
Your task is to enhance user prompts with descriptive details to make them more 
visually compelling. Add descriptive details, artistic style, lighting, and composition 
information that would make the image more vivid and detailed. Your enhanced prompt 
should be 2-3 times longer than the original prompt."""

        # Create the user message
        user_message = f"Here is my image prompt: \"{prompt}\"\nPlease enhance it to create a more vivid and detailed image."
        
        # Combine into a proper instruction format for DeepSeek
        instruction = f"{system_message}\n\nUser: {user_message}\n\nAssistant:"
        
        # Generate the response
        logging.info(f"Enhancing prompt: {prompt}")
        inputs = self.tokenizer(instruction, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        # Decode the response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the enhanced prompt part
        enhanced_prompt = response.split("Assistant:")[-1].strip()
        
        # Clean up the response: sometimes models add quotes or "Enhanced prompt:" prefix
        enhanced_prompt = enhanced_prompt.replace("Enhanced prompt:", "").strip()
        enhanced_prompt = enhanced_prompt.strip('"\'')
        
        logging.info(f"Enhanced prompt: {prompt} -> {enhanced_prompt}")
        return enhanced_prompt
    
    def is_memory_query(self, prompt: str) -> bool:
        """
        Detect if the prompt is requesting memory retrieval rather than creation.
        
        Args:
            prompt: The user's prompt
            
        Returns:
            bool: True if this is a memory query, False otherwise
        """
        memory_keywords = [
            "show me", "find", "retrieve", "get", "recall", "remember", 
            "like before", "like last time", "previous", "earlier", "last",
            "search for", "look for", "any", "all"
        ]
        
        return any(keyword in prompt.lower() for keyword in memory_keywords)
    
    def parse_memory_query(self, prompt: str) -> Dict:
        """
        Extract information from a memory-related query.
        
        Args:
            prompt: The user's memory query
            
        Returns:
            Dict: Extracted query parameters
        """
        # For memory queries, we'll continue using our rule-based approach
        # as it's more reliable for this specific task
        query = prompt.lower()
        result = {
            "is_memory_query": True,
            "search_terms": [],
            "limit": 5,
            "sort_by": "timestamp",
            "reverse": True
        }
        
        # Extract search terms (simple approach - could be more sophisticated)
        words = query.split()
        for i, word in enumerate(words):
            if word in ["like", "about", "with", "containing"] and i < len(words) - 1:
                result["search_terms"].append(words[i+1])
                
        # Look for time-related terms
        if any(term in query for term in ["recent", "latest", "newest"]):
            result["reverse"] = True
        elif any(term in query for term in ["oldest", "first", "earliest"]):
            result["reverse"] = False
            
        # Look for count terms
        if "last" in query and any(word.isdigit() for word in words):
            for i, word in enumerate(words):
                if word == "last" and i < len(words) - 1 and words[i+1].isdigit():
                    result["limit"] = int(words[i+1])
        
        # If no specific search terms, extract potential keywords
        if not result["search_terms"]:
            # Remove common words
            common_words = ["show", "me", "find", "get", "the", "a", "an", "in", "on", "with", "and", "or", "my"]
            filtered_words = [w for w in words if w not in common_words and len(w) > 3]
            
            # Handle plural/singular forms
            search_terms = []
            for word in filtered_words:
                search_terms.append(word)
                # Also handle simple plural forms (adding 's')
                if word.endswith('s') and word[:-1] not in common_words:
                    search_terms.append(word[:-1])
                
            result["search_terms"] = search_terms
        
        return result


# Singleton instance for global access
_llm_enhancer = None

def get_real_llm_enhancer() -> DeepSeekLLMEnhancer:
    """Get or create the singleton LLM enhancer instance"""
    global _llm_enhancer
    if _llm_enhancer is None:
        _llm_enhancer = DeepSeekLLMEnhancer()
    return _llm_enhancer