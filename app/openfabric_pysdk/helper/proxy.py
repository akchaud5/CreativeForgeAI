"""
Mock Proxy implementation for testing.
"""

class Proxy:
    """Mock Proxy class for communication."""
    
    def __init__(self, url, tag, ssl_verify=True):
        self.url = url
        self.tag = tag
        self.ssl_verify = ssl_verify
    
    def request(self, data, uid):
        """Mock request method."""
        return ExecutionResult(data)
    
    def execute(self, inputs, configs, uid):
        """Mock execute method."""
        return ExecutionResult(inputs)


class ExecutionResult:
    """Mock execution result."""
    
    def __init__(self, data=None):
        self._data = data
        self._status = "completed"  # Always completed in mock
    
    def wait(self):
        """Mock wait method."""
        pass
    
    def status(self):
        """Return execution status."""
        return self._status
    
    def data(self):
        """Return result data."""
        return self._data