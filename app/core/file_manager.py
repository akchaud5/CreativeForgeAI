import os
import base64
from datetime import datetime
from typing import Optional, Tuple, Union

class FileManager:
    """
    Manages file operations for storing and retrieving image and 3D model files.
    
    Attributes:
        _base_dir (str): Base directory for file storage
        _image_dir (str): Directory for image files
        _model_dir (str): Directory for 3D model files
    """
    
    def __init__(self, base_dir: str = 'datastore'):
        """
        Initialize file manager with storage paths.
        
        Args:
            base_dir: Base directory for file storage
        """
        self._base_dir = base_dir
        self._image_dir = os.path.join(base_dir, 'images')
        self._model_dir = os.path.join(base_dir, 'models')
        
        # Create directories if they don't exist
        os.makedirs(self._image_dir, exist_ok=True)
        os.makedirs(self._model_dir, exist_ok=True)
    
    def save_image(self, image_data: bytes, identifier: str) -> str:
        """
        Save image data to a file.
        
        Args:
            image_data: Binary image data
            identifier: Unique identifier for the file
            
        Returns:
            str: Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"img_{identifier}_{timestamp}.png"
        filepath = os.path.join(self._image_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
            
        return filepath
    
    def save_model(self, model_data: bytes, identifier: str) -> str:
        """
        Save 3D model data to a file.
        
        Args:
            model_data: Binary model data
            identifier: Unique identifier for the file
            
        Returns:
            str: Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"model_{identifier}_{timestamp}.glb"
        filepath = os.path.join(self._model_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(model_data)
            
        return filepath
    
    def load_file(self, filepath: str) -> Optional[bytes]:
        """
        Load file data from disk.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Optional[bytes]: File data if found, None otherwise
        """
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'rb') as f:
            return f.read()
    
    def get_file_info(self, filepath: str) -> Tuple[bool, int, str]:
        """
        Get information about a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Tuple[bool, int, str]: (exists, size, file_type)
        """
        if not os.path.exists(filepath):
            return (False, 0, "")
            
        size = os.path.getsize(filepath)
        _, ext = os.path.splitext(filepath)
        return (True, size, ext.lstrip('.'))
    
    def encode_to_base64(self, data: bytes) -> str:
        """
        Encode binary data to base64 string.
        
        Args:
            data: Binary data
            
        Returns:
            str: Base64-encoded string
        """
        return base64.b64encode(data).decode('utf-8')
    
    def decode_from_base64(self, encoded: str) -> bytes:
        """
        Decode base64 string to binary data.
        
        Args:
            encoded: Base64-encoded string
            
        Returns:
            bytes: Decoded binary data
        """
        return base64.b64decode(encoded)


# Singleton instance for global access
_file_manager = None

def get_file_manager() -> FileManager:
    """Get or create the singleton file manager instance"""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager