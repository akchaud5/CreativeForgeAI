"""
Lightweight LLM Enhancer that uses smaller models or API-based alternatives.
Provides the same interface as real_llm_enhancer.py but with lower memory usage.
"""

import logging
import os
import json
from typing import Dict, List, Optional
import random

# Avoid importing torch and transformers to save memory
# Instead, we'll implement a creative rule-based enhancer

class LiteLLMEnhancer:
    """
    Memory-efficient LLM enhancer that uses rules and templates
    instead of loading a large model into memory.
    
    This class mimics the interface of DeepSeekLLMEnhancer but uses
    much less memory.
    """
    
    def __init__(self):
        """Initialize the lite LLM enhancer."""
        logging.info("Initializing Lite LLM Enhancer (low memory version)")
        self._load_templates()
    
    def _load_templates(self):
        """Load enhancement templates and styles."""
        # Artistic styles that can be applied
        self.artistic_styles = [
            "photorealistic", "digital art", "oil painting", "watercolor", 
            "sketch", "anime", "pixel art", "3D render", "cinematic",
            "fantasy art", "concept art", "illustrated", "cartoon"
        ]
        
        # Lighting conditions
        self.lighting = [
            "soft lighting", "dramatic lighting", "backlit", "golden hour light",
            "blue hour", "studio lighting", "natural light", "neon lights",
            "moonlight", "sunrise", "sunset", "ambient occlusion", "ray tracing"
        ]
        
        # Perspective options
        self.perspectives = [
            "wide angle", "close-up", "bird's eye view", "worm's eye view",
            "isometric view", "panoramic", "macro shot", "telephoto", "fisheye lens",
            "front view", "side view", "three-quarter view"
        ]
        
        # Quality enhancers
        self.quality = [
            "high resolution", "detailed", "highly detailed", "intricate details",
            "sharp focus", "8K", "ultrarealistic", "professional", "award-winning",
            "masterpiece", "trending on artstation", "vivid colors"
        ]
        
        # Templates for different subject types
        self.templates = {
            "landscape": "{subject}, {style}, {lighting}, {perspective}, {quality}",
            "character": "{subject}, {style}, {lighting}, with {quality} details",
            "object": "{subject}, {style}, {lighting}, {perspective} view, {quality}",
            "abstract": "{subject}, {style}, {quality}, {lighting}",
            "scene": "{subject}, {style}, {lighting}, {perspective}, {quality}"
        }
    
    def _test_model(self):
        """Test the model with a simple prompt."""
        try:
            result = self.enhance_prompt("A cat")
            logging.info(f"Test result: {result}")
        except Exception as e:
            logging.error(f"Error testing model: {e}")
    
    def _categorize_prompt(self, prompt: str) -> str:
        """Categorize the prompt to apply the appropriate template."""
        prompt_lower = prompt.lower()
        
        # Simple categorization based on keywords
        if any(word in prompt_lower for word in ["landscape", "mountain", "forest", "beach", "nature", "sky"]):
            return "landscape"
        elif any(word in prompt_lower for word in ["person", "man", "woman", "character", "face", "portrait"]):
            return "character"
        elif any(word in prompt_lower for word in ["object", "item", "tool", "device", "food"]):
            return "object"
        elif any(word in prompt_lower for word in ["abstract", "concept", "surreal"]):
            return "abstract"
        else:
            return "scene"  # Default category
    
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a user prompt with additional details for better image generation.
        
        Args:
            prompt: The user's original prompt
            
        Returns:
            str: Enhanced prompt with additional details
        """
        # Check if this is a memory query
        if self.is_memory_query(prompt):
            return prompt  # Don't enhance memory queries
        
        # Get the category
        category = self._categorize_prompt(prompt)
        
        # Select random elements for enhancement
        style = random.choice(self.artistic_styles)
        light = random.choice(self.lighting)
        perspective = random.choice(self.perspectives)
        quality_aspect = random.choice(self.quality)
        
        # Get the template
        template = self.templates.get(category, self.templates["scene"])
        
        # Format the template
        enhanced = template.format(
            subject=prompt,
            style=style,
            lighting=light,
            perspective=perspective,
            quality=quality_aspect
        )
        
        # Add some random additional details based on the category
        if category == "landscape":
            times_of_day = ["dawn", "morning", "midday", "afternoon", "dusk", "night"]
            weathers = ["clear sky", "cloudy", "foggy", "rainy", "snowy", "stormy"]
            enhanced += f", {random.choice(times_of_day)}, {random.choice(weathers)}"
        
        elif category == "character":
            emotions = ["happy", "sad", "thoughtful", "excited", "calm", "intense"]
            positions = ["standing", "sitting", "walking", "resting", "action pose"]
            enhanced += f", {random.choice(emotions)} expression, {random.choice(positions)}"
        
        elif category == "object":
            materials = ["metal", "wood", "glass", "plastic", "stone", "ceramic", "fabric"]
            textures = ["smooth", "rough", "polished", "textured", "patterned", "glossy", "matte"]
            enhanced += f", made of {random.choice(materials)}, {random.choice(textures)} texture"
        
        logging.info(f"Enhanced prompt: {prompt} -> {enhanced}")
        return enhanced
    
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

def get_lite_llm_enhancer() -> LiteLLMEnhancer:
    """Get or create the singleton LLM enhancer instance"""
    global _llm_enhancer
    if _llm_enhancer is None:
        _llm_enhancer = LiteLLMEnhancer()
    return _llm_enhancer