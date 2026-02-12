"""Configuration management for the docstring generation agent."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Application configuration."""
    # API Configuration (OpenAI or OpenRouter)
    api_key: str
    api_base_url: str = "https://api.openai.com/v1"
    default_model: str = "gpt-4"
    default_temperature: float = 0.2
    
    # Generation Settings
    default_style: str = "google"
    max_iterations: int = 3
    quality_threshold: float = 0.8
    skip_existing: bool = True
    
    # Server Settings
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables.
        
        Supports OpenAI or OpenRouter API.
        Set OPENROUTER_API_KEY to use OpenRouter.
        Set OPENAI_API_KEY to use OpenAI directly.
        """
        # Check for OpenRouter first, then OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY environment variable is required")
        
        # Determine if using OpenRouter
        is_openrouter = os.getenv("OPENROUTER_API_KEY") is not None
        api_base_url = "https://openrouter.ai/api/v1" if is_openrouter else "https://api.openai.com/v1"
        
        # Default model depends on provider
        if is_openrouter:
            default_model = os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
        else:
            default_model = os.getenv("DEFAULT_MODEL", "gpt-4")
        
        return cls(
            api_key=api_key,
            api_base_url=api_base_url,
            default_model=default_model,
            default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.2")),
            default_style=os.getenv("DEFAULT_STYLE", "google"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "3")),
            quality_threshold=float(os.getenv("QUALITY_THRESHOLD", "0.8")),
            skip_existing=os.getenv("SKIP_EXISTING", "true").lower() == "true",
            server_host=os.getenv("SERVER_HOST", "0.0.0.0"),
            server_port=int(os.getenv("SERVER_PORT", "8000")),
        )
    
    @classmethod
    def default(cls) -> "Config":
        """Create default configuration (for testing)."""
        return cls(
            api_key="test-key",
            api_base_url="https://api.openai.com/v1",
            default_model="gpt-4",
            default_temperature=0.2,
            default_style="google",
            max_iterations=3,
            quality_threshold=0.8,
            skip_existing=True,
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
