from src.config.settings import Settings

class TestSettings(Settings):
    """Test settings for the application."""
    environment: str = "test"
    debug: bool = True
    
    # Test-specific settings
    test_redis_url: str = "redis://localhost:6379/1"  # Use different DB for tests
    test_timeout: float = 5.0
    
    class Config:
        env_prefix = "SYNAPSE_TEST_"

test_settings = TestSettings() 