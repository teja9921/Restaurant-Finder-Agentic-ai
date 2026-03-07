"""Configuration management."""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load restaurant-finder-api/.env when running `python -m src.main`
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_PROJECT_ROOT / ".env", override=False)


class Settings:
    """Application settings."""

    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    AWS_PROFILE: Optional[str] = os.getenv("AWS_PROFILE", "bedrock-dev")

    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "").strip()
    BEDROCK_INFERENCE_PROFILE_ID: Optional[str] = os.getenv(
        "BEDROCK_INFERENCE_PROFILE_ID", ""
    ).strip() or None

    # MCP Gateway Configuration
    GATEWAY_URL: Optional[str] = os.getenv("GATEWAY_URL")
    GATEWAY_ID: Optional[str] = os.getenv("GATEWAY_ID")
    
    # Memory configuration
    MEMORY_ID: Optional[str] = os.getenv("MEMORY_ID")

    GUARDRAIL_ENABLED: bool = os.getenv("GUARDRAIL_ENABLED", "false").lower() == "true"
    GUARDRAIL_ID: Optional[str] = os.getenv("GUARDRAIL_ID")
    GUARDRAIL_VERSION: str = os.getenv("GUARDRAIL_VERSION", "DRAFT")
    
    @property
    def BEDROCK_TARGET_ID(self) -> str:
        """Inference profile takes precedence over direct model IDs."""
        target_id = self.BEDROCK_INFERENCE_PROFILE_ID or self.BEDROCK_MODEL_ID
        if not target_id:
            raise ValueError(
                "Missing Bedrock target. Set BEDROCK_INFERENCE_PROFILE_ID "
                "(recommended) or BEDROCK_MODEL_ID in restaurant-finder-api/.env."
            )
        return target_id

    # Service Configuration
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "restaurant-finder-agent")


settings = Settings()
