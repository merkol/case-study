"""
Request Validator - Validates generation request inputs
"""

from typing import Dict, Any, Optional


class RequestValidator:
    """Validator for generation request inputs"""

    # Valid options
    VALID_MODELS = ["Model A", "Model B"]
    VALID_STYLES = [
        "realistic",
        "anime",
        "oil painting",
        "sketch",
        "cyberpunk",
        "watercolor",
    ]
    VALID_COLORS = ["vibrant", "monochrome", "pastel", "neon", "vintage"]
    VALID_SIZES = ["512x512", "1024x1024", "1024x1792"]

    # Credit costs by size
    CREDIT_COSTS = {"512x512": 1, "1024x1024": 3, "1024x1792": 4}

    def validate_generation_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate generation request data

        Args:
            data: Request data dictionary

        Returns:
            Dictionary with 'valid' boolean and optional 'error' message
        """
        # Check required fields
        required_fields = ["userId", "model", "style", "color", "size", "prompt"]
        for field in required_fields:
            if field not in data:
                return {"valid": False, "error": f"Missing required field: {field}"}
            # Special handling for string fields that shouldn't be empty
            if field in ["userId", "prompt"] and isinstance(data[field], str):
                if not data[field].strip():
                    field_name = "userId" if field == "userId" else field.capitalize()
                    return {"valid": False, "error": f"{field_name} cannot be empty"}

        # Validate userId
        user_id = data.get("userId", "").strip()
        if not user_id:
            return {"valid": False, "error": "userId cannot be empty"}

        # Validate model
        model = data.get("model")
        if model not in self.VALID_MODELS:
            return {
                "valid": False,
                "error": f"Invalid model. Must be one of: {', '.join(self.VALID_MODELS)}",
            }

        # Validate style
        style = data.get("style")
        if style not in self.VALID_STYLES:
            return {
                "valid": False,
                "error": f"Invalid style. Must be one of: {', '.join(self.VALID_STYLES)}",
            }

        # Validate color
        color = data.get("color")
        if color not in self.VALID_COLORS:
            return {
                "valid": False,
                "error": f"Invalid color. Must be one of: {', '.join(self.VALID_COLORS)}",
            }

        # Validate size
        size = data.get("size")
        if size not in self.VALID_SIZES:
            return {
                "valid": False,
                "error": f"Invalid size. Must be one of: {', '.join(self.VALID_SIZES)}",
            }

        # Validate prompt
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return {"valid": False, "error": "Prompt cannot be empty"}

        if len(prompt) > 1000:
            return {"valid": False, "error": "Prompt must be less than 1000 characters"}

        # All validations passed
        return {"valid": True}

    def get_credit_cost(self, size: str) -> Optional[int]:
        """
        Get credit cost for a given image size

        Args:
            size: Image size string

        Returns:
            Credit cost or None if invalid size
        """
        return self.CREDIT_COSTS.get(size)

    def validate_user_id(self, user_id: str) -> bool:
        """
        Validate user ID format

        Args:
            user_id: User ID to validate

        Returns:
            True if valid, False otherwise
        """
        if not user_id or not isinstance(user_id, str):
            return False

        # Remove whitespace
        user_id = user_id.strip()

        # Check length (reasonable limits)
        if len(user_id) < 1 or len(user_id) > 128:
            return False

        # Check for valid characters (alphanumeric, dash, underscore)
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", user_id):
            return False

        return True
