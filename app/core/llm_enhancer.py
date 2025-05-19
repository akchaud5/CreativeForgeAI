import logging
import random
import re
from typing import Dict, List, Optional

class LLMEnhancer:
    """
    Simulates a local LLM to enhance and expand user prompts for better image generation.
    In a real implementation, this would use a locally deployed model like DeepSeek or LLaMA.
    
    This simulation demonstrates the architecture while avoiding external API dependencies.
    """
    
    # Predefined details for various prompt categories
    DESCRIPTIVE_DETAILS = {
        "animal": [
            "with intricate fur patterns", "showing detailed skin texture", 
            "with realistic eyes that reflect light", "in dynamic motion",
            "with anatomically correct features", "showcasing natural behavior"
        ],
        "person": [
            "with detailed facial expressions", "wearing intricate clothing with fabric folds",
            "in dynamic pose showing emotion", "with realistic skin texture and tone",
            "with detailed hair that catches the light", "with anatomically correct proportions"
        ],
        "landscape": [
            "with atmospheric perspective", "showing realistic lighting conditions",
            "with detailed foliage and terrain", "featuring realistic water reflections",
            "with volumetric clouds and sky", "showing accurate environmental details"
        ],
        "object": [
            "with realistic material textures", "showing accurate surface reflections",
            "with fine mechanical details", "featuring realistic wear patterns",
            "with proper scale and proportions", "showing intricate design elements"
        ],
        "fantasy": [
            "with otherworldly lighting effects", "showing magical atmospheric elements",
            "with surreal yet consistent physics", "featuring imaginative yet cohesive design",
            "with fantastical but believable textures", "showcasing impossible yet harmonious compositions"
        ],
        "sci-fi": [
            "with futuristic lighting and reflections", "showing advanced technological details",
            "with mechanical and electronic elements", "featuring sleek, functional design",
            "with holographic or energy effects", "showcasing innovative yet plausible concepts"
        ]
    }
    
    # Style additions to enhance prompts
    STYLE_ENHANCEMENTS = [
        "photorealistic", "hyperdetailed", "8k resolution", "dramatic lighting",
        "cinematic composition", "professional photography", "volumetric lighting",
        "physically accurate rendering", "detailed textures", "high dynamic range",
        "award-winning", "trending on artstation", "octane render"
    ]
    
    # Words to normalize for search (singular/plural forms)
    WORD_NORMALIZATIONS = {
        "cities": "city",
        "castles": "castle",
        "dragons": "dragon",
        "robots": "robot",
        "mountains": "mountain",
        "islands": "island",
        "clouds": "cloud",
        "towers": "tower",
        "buildings": "building"
    }
    
    def __init__(self):
        """Initialize the LLM enhancer."""
        logging.info("Initializing LLM Enhancer (simulation)")
    
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a user prompt with additional details for better image generation.
        
        Args:
            prompt: The user's original prompt
            
        Returns:
            str: Enhanced prompt with additional details
        """
        # Lowercase for easier matching
        prompt_lower = prompt.lower()
        
        # Determine the category of the prompt
        category = self._classify_prompt(prompt_lower)
        
        # Get relevant details for the category
        details = self.DESCRIPTIVE_DETAILS.get(category, self.DESCRIPTIVE_DETAILS["object"])
        
        # Select random details and styles
        selected_details = random.sample(details, min(2, len(details)))
        selected_styles = random.sample(self.STYLE_ENHANCEMENTS, min(3, len(self.STYLE_ENHANCEMENTS)))
        
        # Create enhanced prompt with original prompt first, then details, then style
        enhanced_prompt = f"{prompt}, {', '.join(selected_details)}, {', '.join(selected_styles)}"
        
        logging.info(f"Enhanced prompt: {prompt} -> {enhanced_prompt}")
        return enhanced_prompt
    
    def _classify_prompt(self, prompt: str) -> str:
        """
        Classify a prompt into a category based on keywords.
        
        Args:
            prompt: Lowercase user prompt
            
        Returns:
            str: Category label
        """
        # Simple keyword-based classification
        if any(word in prompt for word in ["person", "man", "woman", "child", "portrait", "face", "people"]):
            return "person"
        elif any(word in prompt for word in ["animal", "dog", "cat", "bird", "wildlife", "creature"]):
            return "animal"
        elif any(word in prompt for word in ["landscape", "mountain", "ocean", "forest", "sunset", "nature"]):
            return "landscape"
        elif any(word in prompt for word in ["magic", "dragon", "wizard", "fairy", "mythical", "fantasy"]):
            return "fantasy"
        elif any(word in prompt for word in ["robot", "spaceship", "futuristic", "tech", "sci-fi"]):
            return "sci-fi"
        else:
            return "object"
    
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
            
            # Normalize words (singular/plural)
            normalized_words = []
            for word in filtered_words:
                # Check if we have a normalized form
                normalized = self.WORD_NORMALIZATIONS.get(word, word)
                # Also handle simple plural forms (adding 's')
                if word.endswith('s') and word[:-1] not in common_words:
                    normalized = word[:-1]
                normalized_words.append(normalized)
                
            if normalized_words:
                result["search_terms"] = normalized_words
                
                # Also include original words for exact matches
                for word in filtered_words:
                    if word not in result["search_terms"]:
                        result["search_terms"].append(word)
        
        return result


# Singleton instance for global access
_llm_enhancer = None

def get_llm_enhancer() -> LLMEnhancer:
    """Get or create the singleton LLM enhancer instance"""
    global _llm_enhancer
    if _llm_enhancer is None:
        _llm_enhancer = LLMEnhancer()
    return _llm_enhancer