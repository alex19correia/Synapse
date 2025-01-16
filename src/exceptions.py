"""Custom exceptions for the Synapse project."""

class SynapseError(Exception):
    """Base exception class for all Synapse errors."""
    pass

class DatabaseError(SynapseError):
    """Exception raised for database-related errors."""
    pass

class MessageValidationError(SynapseError):
    """Exception raised for message validation errors."""
    pass

class RateLimitError(SynapseError):
    """Exception raised when rate limits are exceeded."""
    pass

class AuthenticationError(SynapseError):
    """Exception raised for authentication failures."""
    pass

class ConfigurationError(SynapseError):
    """Exception raised for configuration-related errors."""
    pass

class LLMError(SynapseError):
    """Exception raised for LLM-related errors."""
    pass

class CrawlerError(SynapseError):
    """Exception raised for crawler-related errors."""
    pass 