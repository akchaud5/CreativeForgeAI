"""
Mock-up of the Openfabric SDK starter module for testing purposes.
"""

class Starter:
    """Starter class for igniting the application."""
    
    @staticmethod
    def ignite(debug=False, host="0.0.0.0", port=8888):
        """Start the application."""
        print(f"[MOCK] Starting application on {host}:{port} (debug={debug})")
        print("[MOCK] This is a mock starter that doesn't actually start a server.")
        print("[MOCK] Use the test_pipeline.py script to test the application.")