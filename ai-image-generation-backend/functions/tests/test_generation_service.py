"""
tests/test_generation_service.py - Tests for generation service
"""

import pytest
from unittest.mock import Mock, patch
from services.generation_service import GenerationService


class TestGenerationService:
    @pytest.fixture
    def mock_db(self):
        """Create mock Firestore client"""
        return Mock()

    @pytest.fixture
    def generation_service(self, mock_db):
        """Create GenerationService instance with mock DB"""
        return GenerationService(mock_db)

    def test_generate_image_success_model_a(self, generation_service):
        """Test successful image generation with Model A"""
        with (
            patch("random.random", return_value=0.95),
            patch("time.sleep"),
        ):  # Skip sleep in tests
            result = generation_service.generate_image(
                "req123", "Model A", "realistic", "vibrant", "1024x1024", "test prompt"
            )

            assert result.startswith("https://placeholder-model-a.com/image_req123_")
            assert result.endswith(".jpg")

    def test_generate_image_success_model_b(self, generation_service):
        """Test successful image generation with Model B"""
        with patch("random.random", return_value=0.95), patch("time.sleep"):
            result = generation_service.generate_image(
                "req456", "Model B", "anime", "pastel", "512x512", "test prompt"
            )

            assert result.startswith("https://placeholder-model-b.com/image_req456_")
            assert result.endswith(".jpg")

    def test_generate_image_simulated_failure(self, generation_service):
        """Test simulated failure during generation"""
        with (
            patch("random.random", return_value=0.01),
            patch("time.sleep"),
        ):  # Force failure
            with pytest.raises(Exception) as exc_info:
                generation_service.generate_image(
                    "req789",
                    "Model A",
                    "realistic",
                    "vibrant",
                    "1024x1024",
                    "test prompt",
                )

            assert str(exc_info.value) in [
                "AI model temporarily unavailable",
                "Generation timeout",
                "Invalid prompt processing",
                "Resource allocation failed",
                "Model inference error",
            ]

    def test_validate_generation_parameters_valid(self, generation_service):
        """Test validation with valid parameters"""
        is_valid, error = generation_service.validate_generation_parameters(
            "Model A", "realistic", "vibrant", "1024x1024"
        )

        assert is_valid is True
        assert error is None

    def test_validate_generation_parameters_invalid_model(self, generation_service):
        """Test validation with invalid model"""
        is_valid, error = generation_service.validate_generation_parameters(
            "Model C", "realistic", "vibrant", "1024x1024"
        )

        assert is_valid is False
        assert "Invalid model" in error

    def test_validate_generation_parameters_invalid_style(self, generation_service):
        """Test validation with invalid style"""
        is_valid, error = generation_service.validate_generation_parameters(
            "Model A", "photorealistic", "vibrant", "1024x1024"
        )

        assert is_valid is False
        assert "Invalid style" in error

    def test_validate_generation_parameters_invalid_color(self, generation_service):
        """Test validation with invalid color"""
        is_valid, error = generation_service.validate_generation_parameters(
            "Model A", "realistic", "bright", "1024x1024"
        )

        assert is_valid is False
        assert "Invalid color" in error

    def test_validate_generation_parameters_invalid_size(self, generation_service):
        """Test validation with invalid size"""
        is_valid, error = generation_service.validate_generation_parameters(
            "Model A", "realistic", "vibrant", "2048x2048"
        )

        assert is_valid is False
        assert "Invalid size" in error
