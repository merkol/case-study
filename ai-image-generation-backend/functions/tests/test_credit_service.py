"""
tests/test_credit_service.py - Tests for credit service
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from services.credit_service import CreditService
from models.transaction import TransactionType


class TestCreditService:
    @pytest.fixture
    def mock_db(self):
        """Create mock Firestore client"""
        return Mock()

    @pytest.fixture
    def credit_service(self, mock_db):
        """Create CreditService instance with mock DB"""
        return CreditService(mock_db)

    def test_get_user_credits_existing_user(self, credit_service, mock_db):
        """Test getting credits for existing user"""
        # Mock user document
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"credits": 50}

        mock_db.collection.return_value.document.return_value.get.return_value = (
            mock_doc
        )

        # Test
        credits = credit_service.get_user_credits("user123")

        assert credits == 50
        # Check that collection was called with "users" at some point
        mock_db.collection.assert_any_call("users")

    def test_get_user_credits_nonexistent_user(self, credit_service, mock_db):
        """Test getting credits for non-existent user returns 0"""
        # Mock non-existent user
        mock_doc = Mock()
        mock_doc.exists = False

        mock_db.collection.return_value.document.return_value.get.return_value = (
            mock_doc
        )

        # Test
        credits = credit_service.get_user_credits("nonexistent")

        assert credits == 0

    def test_deduct_credits_success(self, credit_service, mock_db):
        """Test successful credit deduction"""
        # Mock transaction and user document
        mock_transaction = Mock()
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {"credits": 50}

        mock_transaction.get.return_value = mock_user_doc

        # Mock document references
        mock_user_ref = Mock()
        mock_transaction_ref = Mock()
        mock_transaction_ref.id = "trans123"

        mock_db.collection.return_value.document.side_effect = [
            mock_user_ref,  # First call for user
            mock_transaction_ref,  # Second call for transaction
        ]

        # Test
        result = credit_service.deduct_credits(
            mock_transaction, "user123", 10, "req123"
        )

        assert result is True
        mock_transaction.update.assert_called_once()
        mock_transaction.set.assert_called_once()

    def test_deduct_credits_insufficient_funds(self, credit_service, mock_db):
        """Test credit deduction with insufficient funds"""
        # Mock transaction and user document
        mock_transaction = Mock()
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {"credits": 5}

        mock_transaction.get.return_value = mock_user_doc

        # Mock user reference
        mock_user_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_user_ref

        # Test
        result = credit_service.deduct_credits(
            mock_transaction, "user123", 10, "req123"
        )

        assert result is False
        mock_transaction.update.assert_not_called()

    def test_refund_credits_success(self, credit_service, mock_db):
        """Test successful credit refund"""
        with patch("firebase_admin.firestore.transactional") as mock_transactional:
            # Setup mock transaction
            mock_transaction_instance = Mock()
            mock_db.transaction.return_value = mock_transaction_instance

            # Mock the transactional decorator to just call the function
            mock_transactional.side_effect = lambda func: func

            # Test
            result = credit_service.refund_credits("user123", 10, "req123")

            assert mock_db.transaction.called

    def test_get_transaction_history(self, credit_service, mock_db):
        """Test getting transaction history"""
        # Mock transaction documents
        mock_doc1 = Mock()
        mock_doc1.id = "trans1"
        mock_doc1.to_dict.return_value = {
            "userId": "user123",
            "type": "deduction",
            "credits": 3,
            "timestamp": datetime.now(timezone.utc),
        }

        mock_doc2 = Mock()
        mock_doc2.id = "trans2"
        mock_doc2.to_dict.return_value = {
            "userId": "user123",
            "type": "refund",
            "credits": 1,
            "timestamp": datetime.now(timezone.utc),
        }

        # Mock the Firestore query chain
        mock_stream = [mock_doc1, mock_doc2]
        mock_limit = Mock()
        mock_limit.stream.return_value = mock_stream

        mock_order_by = Mock()
        mock_order_by.limit.return_value = mock_limit

        mock_where = Mock()
        mock_where.order_by.return_value = mock_order_by

        # Mock the transactions_collection directly on the service instance
        mock_transactions_collection = Mock()
        mock_transactions_collection.where.return_value = mock_where
        credit_service.transactions_collection = mock_transactions_collection

        # Test
        transactions = credit_service.get_transaction_history("user123")

        assert len(transactions) == 2
        assert transactions[0]["transactionId"] == "trans1"
        assert transactions[1]["transactionId"] == "trans2"

    def test_create_user_with_credits_success(self, credit_service, mock_db):
        """Test successful user creation with credits"""
        # Mock document references
        mock_user_ref = Mock()
        mock_transaction_ref = Mock()
        mock_transaction_ref.id = "trans123"

        mock_db.collection.return_value.document.side_effect = [
            mock_user_ref,  # users collection
            mock_transaction_ref,  # transactions collection
            mock_transaction_ref,  # transactions collection for set
        ]

        # Test
        result = credit_service.create_user_with_credits(
            "user123", 50, "test@example.com"
        )

        assert result is True
        mock_user_ref.set.assert_called_once()

    def test_create_user_with_credits_default_amount(self, credit_service, mock_db):
        """Test user creation with default credit amount"""
        # Mock document references
        mock_user_ref = Mock()
        mock_transaction_ref = Mock()
        mock_transaction_ref.id = "trans123"

        mock_db.collection.return_value.document.side_effect = [
            mock_user_ref,
            mock_transaction_ref,
            mock_transaction_ref,
        ]

        # Test with default credits (should be 50)
        result = credit_service.create_user_with_credits("user123")

        assert result is True

    def test_get_user_credits_error_handling(self, credit_service, mock_db):
        """Test error handling in get_user_credits"""
        # Mock database error
        mock_db.collection.return_value.document.return_value.get.side_effect = (
            Exception("DB error")
        )

        # Should return 0 on error
        credits = credit_service.get_user_credits("user123")
        assert credits == 0

    def test_deduct_credits_user_not_found(self, credit_service, mock_db):
        """Test deduct_credits when user doesn't exist"""
        # Mock transaction and non-existent user
        mock_transaction = Mock()
        mock_user_doc = Mock()
        mock_user_doc.exists = False

        mock_transaction.get.return_value = mock_user_doc

        mock_user_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_user_ref

        # Test
        result = credit_service.deduct_credits(
            mock_transaction, "user123", 10, "req123"
        )

        assert result is False

    def test_deduct_credits_error_handling(self, credit_service, mock_db):
        """Test error handling in deduct_credits"""
        # Mock transaction that raises exception
        mock_transaction = Mock()
        mock_transaction.get.side_effect = Exception("Transaction error")

        mock_user_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_user_ref

        # Test
        result = credit_service.deduct_credits(
            mock_transaction, "user123", 10, "req123"
        )

        assert result is False

    def test_refund_credits_error_handling(self, credit_service, mock_db):
        """Test error handling in refund_credits"""
        # Mock database error
        mock_db.transaction.side_effect = Exception("Transaction error")

        # Test
        result = credit_service.refund_credits("user123", 10, "req123")

        assert result is False

    def test_get_transaction_history_error_handling(self, credit_service, mock_db):
        """Test error handling in get_transaction_history"""
        # Mock the transactions_collection to raise an error
        mock_transactions_collection = Mock()
        mock_transactions_collection.where.side_effect = Exception("Query error")
        credit_service.transactions_collection = mock_transactions_collection

        # Test
        transactions = credit_service.get_transaction_history("user123")

        assert transactions == []

    def test_create_user_with_credits_error_handling(self, credit_service, mock_db):
        """Test error handling in create_user_with_credits"""
        # Mock database error
        mock_db.collection.return_value.document.return_value.set.side_effect = (
            Exception("DB error")
        )

        # Test
        result = credit_service.create_user_with_credits("user123", 50)

        assert result is False
