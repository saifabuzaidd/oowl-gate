class IngestionError(Exception):
    """Base exception for all ingestion-related errors."""
    pass

class UnsupportedIaCFormatError(IngestionError):
    pass

class TerraformExecutionError(IngestionError):
    pass

class TerraformParseError(IngestionError):
    pass
