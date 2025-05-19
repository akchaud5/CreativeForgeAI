import os
import base64
import logging
import time
import uuid
from datetime import datetime
from typing import Optional, Tuple

class FileManager:
    """
    Handles storage and retrieval of generated images and 3D models.
    """
    
    def __init__(self, storage_base_dir: Optional[str] = None):
        """
        Initialize the file manager
        
        Args:
            storage_base_dir: Base directory for file storage
        """
        self.logger = logging.getLogger(__name__)
        
        if storage_base_dir is None:
            # Default to a directory in the application path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_base_dir = os.path.join(base_dir, "datastore")
        
        self.storage_base_dir = storage_base_dir
        self.image_dir = os.path.join(storage_base_dir, "images")
        self.model_dir = os.path.join(storage_base_dir, "models")
        
        # Create directories if they don't exist
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.logger.info(f"FileManager initialized with storage at {storage_base_dir}")
    
    def save_image(self, image_data: str, user_id: str) -> str:
        """
        Save an image from base64 data
        
        Args:
            image_data: Base64-encoded image data
            user_id: User ID for organizing files
            
        Returns:
            Path to the saved image file
        """
        try:
            # Generate a unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{user_id}_{timestamp}_{uuid.uuid4().hex[:8]}.png"
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(self.image_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            file_path = os.path.join(user_dir, filename)
            
            # Check if the image data has a Base64 header and remove it
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
            
            # Decode and save the image
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(image_data))
            
            self.logger.info(f"Image saved to {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error saving image: {str(e)}")
            return ""
    
    def save_model(self, model_data: str, user_id: str) -> str:
        """
        Save a 3D model from base64 data
        
        Args:
            model_data: Base64-encoded model data
            user_id: User ID for organizing files
            
        Returns:
            Path to the saved model file
        """
        try:
            # Generate a unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{user_id}_{timestamp}_{uuid.uuid4().hex[:8]}.glb"
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(self.model_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            file_path = os.path.join(user_dir, filename)
            
            # Check if the model data has a Base64 header and remove it
            if "base64," in model_data:
                model_data = model_data.split("base64,")[1]
            
            # Decode and save the model
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(model_data))
            
            self.logger.info(f"3D model saved to {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error saving 3D model: {str(e)}")
            return ""
    
    def get_image_as_base64(self, image_path: str) -> Tuple[bool, str]:
        """
        Get an image as base64 data
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (success, base64_data)
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            return False, ""
        
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            return True, image_data
        except Exception as e:
            self.logger.error(f"Error reading image: {str(e)}")
            return False, ""
    
    def get_model_as_base64(self, model_path: str) -> Tuple[bool, str]:
        """
        Get a 3D model as base64 data
        
        Args:
            model_path: Path to the model file
            
        Returns:
            Tuple of (success, base64_data)
        """
        if not os.path.exists(model_path):
            self.logger.error(f"Model not found: {model_path}")
            return False, ""
        
        try:
            with open(model_path, "rb") as f:
                model_data = base64.b64encode(f.read()).decode("utf-8")
            return True, model_data
        except Exception as e:
            self.logger.error(f"Error reading model: {str(e)}")
            return False, ""