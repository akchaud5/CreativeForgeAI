"""
Mock-up of the Openfabric SDK context module for testing purposes.
"""

class AppModel:
    """Application model containing request and response objects."""
    
    def __init__(self):
        self.request = None
        self.response = None


class State:
    """Application state."""
    
    def __init__(self):
        self.data = {}