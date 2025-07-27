"""
tests/test_report_service.py - Comprehensive tests for report service
"""

import sys
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta
from services.report_service import ReportService

# Mock Firebase Admin SDK before it's imported
sys.modules["firebase_admin"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()
sys.modules["firebase_admin.initialize_app"] = MagicMock()
sys.modules["firebase_admin.credentials"] = MagicMock()


class TestReportService:
    @pytest.fixture
    def mock_db(self):
        """Fixture for a mocked Firestore client with comprehensive test data."""
        mock_db = MagicMock()

        # Create collection references
        mock_requests_collection = MagicMock()
        mock_transactions_collection = MagicMock()
        mock_reports_collection = MagicMock()

        def collection_side_effect(name):
            if name == "generation_requests":
                return mock_requests_collection
            elif name == "credit_transactions":
                return mock_transactions_collection
            elif name == "weekly_reports":
                return mock_reports_collection
            return MagicMock()

        mock_db.collection.side_effect = collection_side_effect

        # Store collections for later access
        mock_db._requests_collection = mock_requests_collection
        mock_db._transactions_collection = mock_transactions_collection
        mock_db._reports_collection = mock_reports_collection

        return mock_db

    @pytest.fixture
    def sample_requests_data(self):
        """Fixture providing comprehensive generation request test data."""
        now = datetime.now(timezone.utc)
        return [
            {
                "id": "req1",
                "data": {
                    "createdAt": now - timedelta(days=1),
                    "status": "completed",
                    "model": "Model A",
                    "size": "1024x1024",
                    "style": "realistic",
                    "color": "vibrant",
                    "creditsCharged": 3,
                    "userId": "user1",
                },
            },
            {
                "id": "req2",
                "data": {
                    "createdAt": now - timedelta(days=2),
                    "status": "completed",
                    "model": "Model A",
                    "size": "1024x1792",
                    "style": "anime",
                    "color": "pastel",
                    "creditsCharged": 4,
                    "userId": "user1",
                },
            },
            {
                "id": "req3",
                "data": {
                    "createdAt": now - timedelta(days=3),
                    "status": "failed",
                    "model": "Model B",
                    "size": "512x512",
                    "style": "sketch",
                    "color": "monochrome",
                    "creditsCharged": 1,
                    "userId": "user2",
                },
            },
            {
                "id": "req4",
                "data": {
                    "createdAt": now - timedelta(days=4),
                    "status": "completed",
                    "model": "Model A",
                    "size": "1024x1024",
                    "style": "oil painting",
                    "color": "vintage",
                    "creditsCharged": 3,
                    "userId": "user2",
                },
            },
            {
                "id": "req5",
                "data": {
                    "createdAt": now - timedelta(days=5),
                    "status": "pending",
                    "model": "Model B",
                    "size": "512x512",
                    "style": "cyberpunk",
                    "color": "neon",
                    "creditsCharged": 1,
                    "userId": "user3",
                },
            },
            {
                "id": "req6",
                "data": {
                    "createdAt": now - timedelta(days=6),
                    "status": "failed",
                    "model": "Model A",
                    "size": "1024x1792",
                    "style": "watercolor",
                    "color": "vibrant",
                    "creditsCharged": 4,
                    "userId": "user3",
                },
            },
        ]

    @pytest.fixture
    def sample_transactions_data(self):
        """Fixture providing comprehensive transaction test data."""
        now = datetime.now(timezone.utc)
        return [
            {
                "id": "txn1",
                "data": {
                    "type": "deduction",
                    "credits": 3,
                    "timestamp": now - timedelta(days=1),
                    "userId": "user1",
                    "reason": "Image generation",
                    "generationRequestId": "req1",
                },
            },
            {
                "id": "txn2",
                "data": {
                    "type": "deduction",
                    "credits": 4,
                    "timestamp": now - timedelta(days=2),
                    "userId": "user1",
                    "reason": "Image generation",
                    "generationRequestId": "req2",
                },
            },
            {
                "id": "txn3",
                "data": {
                    "type": "deduction",
                    "credits": 1,
                    "timestamp": now - timedelta(days=3),
                    "userId": "user2",
                    "reason": "Image generation",
                    "generationRequestId": "req3",
                },
            },
            {
                "id": "txn4",
                "data": {
                    "type": "refund",
                    "credits": 1,
                    "timestamp": now - timedelta(days=3),
                    "userId": "user2",
                    "reason": "Failed generation",
                    "generationRequestId": "req3",
                },
            },
            {
                "id": "txn5",
                "data": {
                    "type": "deduction",
                    "credits": 3,
                    "timestamp": now - timedelta(days=4),
                    "userId": "user2",
                    "reason": "Image generation",
                    "generationRequestId": "req4",
                },
            },
            {
                "id": "txn6",
                "data": {
                    "type": "credit",
                    "credits": 50,
                    "timestamp": now - timedelta(days=5),
                    "userId": "user3",
                    "reason": "Initial credits",
                },
            },
            {
                "id": "txn7",
                "data": {
                    "type": "deduction",
                    "credits": 4,
                    "timestamp": now - timedelta(days=6),
                    "userId": "user3",
                    "reason": "Image generation",
                    "generationRequestId": "req6",
                },
            },
            {
                "id": "txn8",
                "data": {
                    "type": "refund",
                    "credits": 4,
                    "timestamp": now - timedelta(days=6),
                    "userId": "user3",
                    "reason": "Failed generation",
                    "generationRequestId": "req6",
                },
            },
        ]

    def create_mock_doc(self, doc_id, data):
        """Helper to create a mock Firestore document."""
        mock_doc = MagicMock()
        mock_doc.id = doc_id
        mock_doc.to_dict.return_value = data
        return mock_doc

    def setup_mock_collections(
        self, mock_db, requests_data=None, transactions_data=None, reports_data=None
    ):
        """Helper to setup mock collection responses."""

        # Setup requests collection
        if requests_data:
            mock_request_docs = [
                self.create_mock_doc(item["id"], item["data"]) for item in requests_data
            ]
            mock_db._requests_collection.where.return_value.where.return_value.stream.return_value = mock_request_docs

        # Setup transactions collection
        if transactions_data:
            mock_transaction_docs = [
                self.create_mock_doc(item["id"], item["data"])
                for item in transactions_data
            ]
            mock_db._transactions_collection.where.return_value.where.return_value.stream.return_value = mock_transaction_docs

        # Setup reports collection
        mock_report_doc = MagicMock()
        mock_report_doc.id = "test_report_id"
        mock_db._reports_collection.document.return_value = mock_report_doc

        if reports_data:
            mock_report_docs = [
                self.create_mock_doc(item["id"], item["data"]) for item in reports_data
            ]
            mock_db._reports_collection.where.return_value.where.return_value.order_by.return_value.stream.return_value = mock_report_docs

        return mock_report_doc

    def test_generate_weekly_report_success(
        self, mock_db, sample_requests_data, sample_transactions_data
    ):
        """Test successful generation of a weekly report with comprehensive data."""
        mock_report_doc = self.setup_mock_collections(
            mock_db, sample_requests_data, sample_transactions_data
        )

        report_service = ReportService(db=mock_db)
        report_id = report_service.generate_weekly_report()

        # Verify report was created
        assert report_id == "test_report_id"
        mock_report_doc.set.assert_called_once()

        # Get the report data that was saved
        report_data = mock_report_doc.set.call_args[0][0]

        # Verify request metrics
        assert report_data["totalRequests"] == 6
        assert report_data["successfulRequests"] == 3  # completed status
        assert report_data["failedRequests"] == 2  # failed status
        assert report_data["successRate"] == 50.0  # 3/6 * 100

        # Verify credit metrics
        assert (
            report_data["totalCreditsConsumed"] == 15
        )  # Sum of all deduction transactions
        assert (
            report_data["totalCreditsRefunded"] == 5
        )  # Sum of all refund transactions
        assert report_data["netCreditsUsed"] == 10  # 15 - 5

        # Verify breakdown by attributes
        assert report_data["requestsByModel"]["Model A"] == 4
        assert report_data["requestsByModel"]["Model B"] == 2

        assert report_data["requestsBySize"]["1024x1024"] == 2
        assert report_data["requestsBySize"]["1024x1792"] == 2
        assert report_data["requestsBySize"]["512x512"] == 2

        assert report_data["requestsByStyle"]["realistic"] == 1
        assert report_data["requestsByStyle"]["anime"] == 1
        assert report_data["requestsByStyle"]["sketch"] == 1
        assert report_data["requestsByStyle"]["oil painting"] == 1
        assert report_data["requestsByStyle"]["cyberpunk"] == 1
        assert report_data["requestsByStyle"]["watercolor"] == 1

        assert report_data["requestsByColor"]["vibrant"] == 2
        assert report_data["requestsByColor"]["pastel"] == 1
        assert report_data["requestsByColor"]["monochrome"] == 1
        assert report_data["requestsByColor"]["vintage"] == 1
        assert report_data["requestsByColor"]["neon"] == 1

        # Verify credits by size (only completed requests)
        assert report_data["creditsBySize"]["1024x1024"] == 6  # 3 + 3 (req1 + req4)
        assert report_data["creditsBySize"]["1024x1792"] == 4  # only req2 completed

        # Verify timestamps are included
        assert "weekStartDate" in report_data
        assert "weekEndDate" in report_data
        assert "createdAt" in report_data

    def test_generate_weekly_report_no_data(self, mock_db):
        """Test weekly report generation with no data."""
        self.setup_mock_collections(mock_db, [], [])

        report_service = ReportService(db=mock_db)
        report_id = report_service.generate_weekly_report()

        # Should still create a report
        assert report_id == "test_report_id"

        # Get the report data
        mock_report_doc = mock_db._reports_collection.document.return_value
        report_data = mock_report_doc.set.call_args[0][0]

        # Verify empty data metrics
        assert report_data["totalRequests"] == 0
        assert report_data["successfulRequests"] == 0
        assert report_data["failedRequests"] == 0
        assert report_data["successRate"] == 0
        assert report_data["totalCreditsConsumed"] == 0
        assert report_data["totalCreditsRefunded"] == 0
        assert report_data["netCreditsUsed"] == 0

    def test_generate_weekly_report_high_failure_rate_anomaly(
        self, mock_db, sample_transactions_data
    ):
        """Test anomaly detection for high failure rate."""
        # Create requests with high failure rate
        now = datetime.now(timezone.utc)
        high_failure_requests = [
            {
                "id": "req1",
                "data": {
                    "createdAt": now - timedelta(days=1),
                    "status": "failed",
                    "model": "Model A",
                    "size": "1024x1024",
                    "style": "realistic",
                    "color": "vibrant",
                    "creditsCharged": 3,
                },
            },
            {
                "id": "req2",
                "data": {
                    "createdAt": now - timedelta(days=2),
                    "status": "failed",
                    "model": "Model A",
                    "size": "1024x1024",
                    "style": "realistic",
                    "color": "vibrant",
                    "creditsCharged": 3,
                },
            },
            {
                "id": "req3",
                "data": {
                    "createdAt": now - timedelta(days=3),
                    "status": "completed",
                    "model": "Model A",
                    "size": "1024x1024",
                    "style": "realistic",
                    "color": "vibrant",
                    "creditsCharged": 3,
                },
            },
        ]

        mock_report_doc = self.setup_mock_collections(
            mock_db, high_failure_requests, sample_transactions_data
        )

        report_service = ReportService(db=mock_db)
        report_id = report_service.generate_weekly_report()

        # Get the report data
        report_data = mock_report_doc.set.call_args[0][0]

        # Check that high failure rate anomaly was detected
        anomalies = report_data["anomalies"]
        failure_anomaly = next(
            (a for a in anomalies if a["type"] == "high_failure_rate"), None
        )

        assert failure_anomaly is not None
        assert failure_anomaly["failureRate"] > 10  # Should be 66.7%
        assert failure_anomaly["severity"] in ["medium", "high"]

    def test_generate_weekly_report_model_imbalance_anomaly(
        self, mock_db, sample_transactions_data
    ):
        """Test anomaly detection for model imbalance."""
        # Create requests with one model dominating (85% to ensure it triggers > 80%)
        now = datetime.now(timezone.utc)
        imbalanced_requests = []

        # Create 17 Model A requests and 3 Model B requests for 85% imbalance
        for i in range(17):
            imbalanced_requests.append(
                {
                    "id": f"req{i + 1}",
                    "data": {
                        "createdAt": now
                        - timedelta(days=(i % 6) + 1),  # Keep within week
                        "status": "completed",
                        "model": "Model A",
                        "size": "1024x1024",
                        "style": "realistic",
                        "color": "vibrant",
                        "creditsCharged": 3,
                    },
                }
            )

        for i in range(3):
            imbalanced_requests.append(
                {
                    "id": f"req{i + 18}",
                    "data": {
                        "createdAt": now - timedelta(days=(i % 6) + 1),
                        "status": "completed",
                        "model": "Model B",
                        "size": "512x512",
                        "style": "sketch",
                        "color": "monochrome",
                        "creditsCharged": 1,
                    },
                }
            )

        mock_report_doc = self.setup_mock_collections(
            mock_db, imbalanced_requests, sample_transactions_data
        )

        # Mock a previous report to trigger full anomaly detection logic
        previous_week_start = (
            now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        ) - timedelta(days=7)
        mock_previous_report = self.create_mock_doc(
            "prev_report",
            {
                "weekStartDate": previous_week_start.isoformat(),
                "totalRequests": 20,  # Same volume to avoid volume spike detection
            },
        )
        mock_db._reports_collection.where.return_value.limit.return_value.stream.return_value = [
            mock_previous_report
        ]

        report_service = ReportService(db=mock_db)
        report_id = report_service.generate_weekly_report()

        # Get the report data
        report_data = mock_report_doc.set.call_args[0][0]

        # Check that model imbalance anomaly was detected
        anomalies = report_data["anomalies"]
        imbalance_anomaly = next(
            (a for a in anomalies if a["type"] == "model_imbalance"), None
        )

        assert imbalance_anomaly is not None
        assert imbalance_anomaly["model"] == "Model A"
        assert imbalance_anomaly["percentage"] == 85.0  # 17/20 * 100

    def test_get_report_by_date_range_success(self, mock_db):
        """Test getting reports by date range."""
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=14)
        end_date = now

        # Mock reports data
        reports_data = [
            {
                "id": "report1",
                "data": {
                    "weekStartDate": (now - timedelta(days=7)).isoformat(),
                    "weekEndDate": now.isoformat(),
                    "totalRequests": 10,
                    "successRate": 85.0,
                    "createdAt": now,
                },
            },
            {
                "id": "report2",
                "data": {
                    "weekStartDate": (now - timedelta(days=14)).isoformat(),
                    "weekEndDate": (now - timedelta(days=7)).isoformat(),
                    "totalRequests": 8,
                    "successRate": 90.0,
                    "createdAt": now - timedelta(days=7),
                },
            },
        ]

        self.setup_mock_collections(mock_db, reports_data=reports_data)

        report_service = ReportService(db=mock_db)
        reports = report_service.get_report_by_date_range(start_date, end_date)

        # Verify reports were returned
        assert len(reports) == 2
        assert reports[0]["reportId"] == "report1"
        assert reports[1]["reportId"] == "report2"
        assert reports[0]["totalRequests"] == 10
        assert reports[1]["totalRequests"] == 8

    def test_get_report_by_date_range_no_results(self, mock_db):
        """Test getting reports by date range with no results."""
        self.setup_mock_collections(mock_db, reports_data=[])

        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=14)
        end_date = now

        report_service = ReportService(db=mock_db)
        reports = report_service.get_report_by_date_range(start_date, end_date)

        # Should return empty list
        assert reports == []

    def test_generate_weekly_report_error_handling(self, mock_db):
        """Test error handling in weekly report generation."""
        # Mock database error
        mock_db._requests_collection.where.side_effect = Exception("Database error")

        report_service = ReportService(db=mock_db)

        # Should raise exception
        with pytest.raises(Exception, match="Database error"):
            report_service.generate_weekly_report()

    def test_get_report_by_date_range_error_handling(self, mock_db):
        """Test error handling in get_report_by_date_range."""
        # Mock database error
        mock_db._reports_collection.where.side_effect = Exception("Query error")

        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=14)
        end_date = now

        report_service = ReportService(db=mock_db)
        reports = report_service.get_report_by_date_range(start_date, end_date)

        # Should return empty list on error
        assert reports == []

    def test_transaction_breakdown_in_report(
        self, mock_db, sample_requests_data, sample_transactions_data
    ):
        """Test that transaction data is properly processed and categorized in the report."""
        mock_report_doc = self.setup_mock_collections(
            mock_db, sample_requests_data, sample_transactions_data
        )

        report_service = ReportService(db=mock_db)
        report_id = report_service.generate_weekly_report()

        # Get the report data
        report_data = mock_report_doc.set.call_args[0][0]

        # Verify specific transaction processing
        # From sample_transactions_data:
        # - 4 deduction transactions: 3+4+1+3+4 = 15 total credits
        # - 2 refund transactions: 1+4 = 5 total credits
        # - 1 credit transaction: 50 credits (should not count in consumed/refunded)

        assert report_data["totalCreditsConsumed"] == 15
        assert report_data["totalCreditsRefunded"] == 5
        assert report_data["netCreditsUsed"] == 10

    def test_detect_anomalies_with_previous_report(
        self, mock_db, sample_transactions_data
    ):
        """Test anomaly detection with previous week's report for comparison."""
        # Setup current week's requests (low volume)
        now = datetime.now(timezone.utc)
        current_requests = [
            {
                "id": "req1",
                "data": {
                    "createdAt": now - timedelta(days=1),
                    "status": "completed",
                    "model": "Model A",
                    "size": "1024x1024",
                    "style": "realistic",
                    "color": "vibrant",
                    "creditsCharged": 3,
                },
            }
        ]

        # Mock previous week's report (high volume)
        previous_week_start = (
            now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        ) - timedelta(days=7)

        # Setup mock for previous report query
        mock_previous_report = self.create_mock_doc(
            "prev_report",
            {
                "weekStartDate": previous_week_start.isoformat(),
                "totalRequests": 10,  # Much higher than current week's 1 request
            },
        )

        # Setup the mock collections
        mock_report_doc = self.setup_mock_collections(
            mock_db, current_requests, sample_transactions_data
        )

        # Mock the previous report query
        mock_db._reports_collection.where.return_value.limit.return_value.stream.return_value = [
            mock_previous_report
        ]

        report_service = ReportService(db=mock_db)
        report_id = report_service.generate_weekly_report()

        # Get the report data
        report_data = mock_report_doc.set.call_args[0][0]

        # Check for volume spike anomaly
        anomalies = report_data["anomalies"]
        volume_anomaly = next(
            (a for a in anomalies if a["type"] == "request_volume_spike"), None
        )

        # With 1 current vs 10 previous, that's a 90% decrease
        assert volume_anomaly is not None
        assert volume_anomaly["currentValue"] == 1
        assert volume_anomaly["previousValue"] == 10

    def test_report_service_initialization(self, mock_db):
        """Test that ReportService initializes correctly with database collections."""
        report_service = ReportService(db=mock_db)

        # Verify collections are properly initialized
        assert report_service.db == mock_db
        assert hasattr(report_service, "reports_collection")
        assert hasattr(report_service, "requests_collection")
        assert hasattr(report_service, "transactions_collection")

    def test_weekly_report_date_calculations(
        self, mock_db, sample_requests_data, sample_transactions_data
    ):
        """Test that weekly report correctly calculates date ranges."""
        mock_report_doc = self.setup_mock_collections(
            mock_db, sample_requests_data, sample_transactions_data
        )

        report_service = ReportService(db=mock_db)

        # Capture the current time before report generation
        before_generation = datetime.now(timezone.utc)
        report_id = report_service.generate_weekly_report()
        after_generation = datetime.now(timezone.utc)

        # Get the report data
        report_data = mock_report_doc.set.call_args[0][0]

        # Parse the dates from the report
        start_date = datetime.fromisoformat(
            report_data["weekStartDate"].replace("Z", "+00:00")
        )
        end_date = datetime.fromisoformat(
            report_data["weekEndDate"].replace("Z", "+00:00")
        )
        created_at = report_data["createdAt"]

        # Verify date range is exactly 7 days
        assert (end_date - start_date).days == 7

        # Verify end date is recent (within the time of test execution)
        assert before_generation.date() <= end_date.date() <= after_generation.date()

        # Verify created_at is within the test execution window
        assert before_generation <= created_at <= after_generation
