"""
Helper package.
"""

from openfabric_pysdk.helper.proxy import Proxy, ExecutionResult

# Re-export for easier imports
__all__ = ['Proxy', 'ExecutionResult']

def has_resource_fields(schema):
    """Mock has_resource_fields method."""
    return False


def json_schema_to_marshmallow(schema):
    """Mock json_schema_to_marshmallow method."""
    return lambda: None


def resolve_resources(url_template, result, schema):
    """Mock resolve_resources method."""
    return result