"""
Mock-up of the Openfabric SDK utility module for testing purposes.
"""

class SchemaUtil:
    """Schema utility class."""
    
    @staticmethod
    def create(instance, data):
        """Create an instance from data."""
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance