"""
Crawler exceptions.
"""

class CrawlerError(Exception):
    """Base exception for crawler errors."""
    pass

class RateLimitError(CrawlerError):
    """Raised when rate limit is exceeded."""
    pass

class FetchError(CrawlerError):
    """Raised when page fetch fails."""
    pass

class ParseError(CrawlerError):
    """Raised when content parsing fails."""
    pass 