"""Content guardrails using AWS Bedrock."""
import boto3
from typing import Optional
from src.config import settings

class GuardrailManager:
    """Manages Bedrock Guardrails for content validation."""

    def __init__(self):
        """Initialize guardrail manager."""
        self.guardrail_id = getattr(settings, 'GUARDRAIL_ID', None)
        self.guardrail_version = getattr(settings, 'GUARDRAIL_VERSION', 'DRAFT')
        self.enabled = getattr(settings, 'GUARDRAIL_ENABLED', False)

        if self.enabled and self.guardrail_id:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=settings.AWS_REGION
            )
        
        else:
            self.client = None

    def apply_guardrail(
            self,
            text: str,
            source: str = "INPUT",
    ) -> Optional[str]:
        """
        Apply Bedrock Guardrail to text.

        Args:
            text: Content to validate
            source: "INPUT" or "OUTPUT"

        Returns:
            Validated text or None if blocked
        """
        if not self.enabled or not self.client or not self.guardrail_id:
            # Guardrails disabled or not configured
            return text
        
        try:
            response = self.client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source=source,
                content=[{"text":{"text": text}}],
            )

            #check if content was blocked
            action = response.get("action")

            if action == "GUARDRAIL_INTERVENED":
                # Content violated guardrails
                print(f"[Guardrail] {source} blocked: {text[:50]}...")
                return None
            
            # Content passed guardrails
            return text
        
        except Exception as e:
            print(f"[Guardrail] Error applying guardrail: {e}")
            #Fail open - allow content if guardrail fails
            return text
        

guardrail_manager = GuardrailManager()

def apply_input_guardrails(text: str) -> Optional[str]:
    """
    Validate user input.

    Args:
        text: User input text

    Returns:
        Validated text or None if blocked
    """
    return guardrail_manager.apply_guardrail(text, source="INPUT")

def apply_output_guardrails(text: str) -> Optional[str]:
    """
    Validate agent output.

    Args:
        text: Agent response text

    Returns:
        Validated text or None if blocked
    """
    return guardrail_manager.apply_guardrail(text, source="OUTPUT")