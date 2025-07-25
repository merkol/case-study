"""
tests/test_validators.py - Tests for request validator
"""

import pytest
from validators.request_validator import RequestValidator


class TestRequestValidator:
    @pytest.fixture
    def validator(self):
        """Create RequestValidator instance"""
        return RequestValidator()

    def test_validate_generation_request_valid(self, validator):
        """Test validation with valid request data"""
        data = {
            "userId": "user123",
            "model": "Model A",
            "style": "realistic",
            "color": "vibrant",
            "size": "1024x1024",
            "prompt": "A beautiful sunset",
        }

        result = validator.validate_generation_request(data)
        assert result["valid"] is True

    def test_validate_generation_request_missing_field(self, validator):
        """Test validation with missing required field"""
        data = {
            "userId": "user123",
            "model": "Model A",
            "style": "realistic",
            "color": "vibrant",
            # Missing size
            "prompt": "A beautiful sunset",
        }

        result = validator.validate_generation_request(data)
        assert result["valid"] is False
        assert "Missing required field: size" in result["error"]

    def test_validate_generation_request_empty_userid(self, validator):
        """Test validation with empty userId"""
        data = {
            "userId": "  ",
            "model": "Model A",
            "style": "realistic",
            "color": "vibrant",
            "size": "1024x1024",
            "prompt": "A beautiful sunset",
        }

        result = validator.validate_generation_request(data)
        assert result["valid"] is False
        assert "userId cannot be empty" in result["error"]

    def test_validate_generation_request_invalid_model(self, validator):
        """Test validation with invalid model"""
        data = {
            "userId": "user123",
            "model": "Model C",
            "style": "realistic",
            "color": "vibrant",
            "size": "1024x1024",
            "prompt": "A beautiful sunset",
        }

        result = validator.validate_generation_request(data)
        assert result["valid"] is False
        assert "Invalid model" in result["error"]

    def test_validate_generation_request_empty_prompt(self, validator):
        """Test validation with empty prompt"""
        data = {
            "userId": "user123",
            "model": "Model A",
            "style": "realistic",
            "color": "vibrant",
            "size": "1024x1024",
            "prompt": "",
        }

        result = validator.validate_generation_request(data)
        assert result["valid"] is False
        assert "Prompt cannot be empty" in result["error"]

    def test_validate_generation_request_long_prompt(self, validator):
        """Test validation with overly long prompt"""
        data = {
            "userId": "user123",
            "model": "Model A",
            "style": "realistic",
            "color": "vibrant",
            "size": "1024x1024",
            "prompt": "x" * 1001,  # Over 1000 characters
        }

        result = validator.validate_generation_request(data)
        assert result["valid"] is False
        assert "Prompt must be less than 1000 characters" in result["error"]

    def test_get_credit_cost(self, validator):
        """Test getting credit cost for different sizes"""
        assert validator.get_credit_cost("512x512") == 1
        assert validator.get_credit_cost("1024x1024") == 3
        assert validator.get_credit_cost("1024x1792") == 4
        assert validator.get_credit_cost("invalid") is None

    def test_validate_user_id_valid(self, validator):
        """Test user ID validation with valid IDs"""
        assert validator.validate_user_id("user123") is True
        assert validator.validate_user_id("user-123") is True
        assert validator.validate_user_id("user_123") is True
        assert validator.validate_user_id("USER123") is True

    def test_validate_user_id_invalid(self, validator):
        """Test user ID validation with invalid IDs"""
        assert validator.validate_user_id("") is False
        assert validator.validate_user_id("user@123") is False
        assert validator.validate_user_id("user 123") is False
        assert validator.validate_user_id("x" * 129) is False
