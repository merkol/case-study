"""
Report Service - Generates weekly usage and analytics reports
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Tuple
from firebase_admin import firestore
from collections import defaultdict

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating weekly usage reports"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.reports_collection = db.collection("weekly_reports")
        self.requests_collection = db.collection("generation_requests")
        self.transactions_collection = db.collection("credit_transactions")
    
    def generate_weekly_report(self) -> str:
        """
        Generate a comprehensive weekly usage report
        
        Returns:
            Report ID
        """
        try:
            # Calculate date range (last 7 days)
            end_date = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            start_date = end_date - timedelta(days=7)
            
            logger.info(f"Generating report for {start_date} to {end_date}")
            
            # Fetch generation requests for the week
            requests_query = (
                self.requests_collection
                .where("createdAt", ">=", start_date)
                .where("createdAt", "<", end_date)
            )
            
            # Initialize counters
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            requests_by_model = defaultdict(int)
            requests_by_size = defaultdict(int)
            requests_by_style = defaultdict(int)
            requests_by_color = defaultdict(int)
            credits_by_size = defaultdict(int)
            
            # Process each request
            for doc in requests_query.stream():
                request_data = doc.to_dict()
                total_requests += 1
                
                # Count by status
                status = request_data.get("status", "pending")
                if status == "completed":
                    successful_requests += 1
                elif status == "failed":
                    failed_requests += 1
                
                # Count by attributes
                model = request_data.get("model", "Unknown")
                size = request_data.get("size", "Unknown")
                style = request_data.get("style", "Unknown")
                color = request_data.get("color", "Unknown")
                credits = request_data.get("creditsCharged", 0)
                
                requests_by_model[model] += 1
                requests_by_size[size] += 1
                requests_by_style[style] += 1
                requests_by_color[color] += 1
                
                if status == "completed":
                    credits_by_size[size] += credits
            
            # Fetch credit transactions for the week
            transactions_query = (
                self.transactions_collection
                .where("timestamp", ">=", start_date)
                .where("timestamp", "<", end_date)
            )
            
            total_credits_consumed = 0
            total_credits_refunded = 0
            
            for doc in transactions_query.stream():
                transaction_data = doc.to_dict()
                transaction_type = transaction_data.get("type")
                credits = transaction_data.get("credits", 0)
                
                if transaction_type == "deduction":
                    total_credits_consumed += credits
                elif transaction_type == "refund":
                    total_credits_refunded += credits
            
            # Detect anomalies
            anomalies = self._detect_anomalies(
                total_requests,
                failed_requests,
                requests_by_model,
                start_date
            )
            
            # Calculate success rate
            success_rate = (
                (successful_requests / total_requests * 100) 
                if total_requests > 0 else 0
            )
            
            # Create report document
            report_data = {
                "weekStartDate": start_date.isoformat(),
                "weekEndDate": end_date.isoformat(),
                "totalRequests": total_requests,
                "successfulRequests": successful_requests,
                "failedRequests": failed_requests,
                "successRate": round(success_rate, 2),
                "totalCreditsConsumed": total_credits_consumed,
                "totalCreditsRefunded": total_credits_refunded,
                "netCreditsUsed": total_credits_consumed - total_credits_refunded,
                "requestsByModel": dict(requests_by_model),
                "requestsBySize": dict(requests_by_size),
                "requestsByStyle": dict(requests_by_style),
                "requestsByColor": dict(requests_by_color),
                "creditsBySize": dict(credits_by_size),
                "anomalies": anomalies,
                "createdAt": datetime.now(timezone.utc)
            }
            
            # Save report
            report_ref = self.reports_collection.document()
            report_ref.set(report_data)
            
            logger.info(f"Weekly report generated successfully: {report_ref.id}")
            return report_ref.id
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}")
            raise
    
    def _detect_anomalies(
        self,
        total_requests: int,
        failed_requests: int,
        requests_by_model: Dict[str, int],
        start_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in usage patterns
        
        Args:
            total_requests: Total number of requests
            failed_requests: Number of failed requests
            requests_by_model: Request count by model
            start_date: Week start date
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            # Get previous week's report for comparison
            previous_week_start = start_date - timedelta(days=7)
            previous_report_query = (
                self.reports_collection
                .where("weekStartDate", "==", previous_week_start.isoformat())
                .limit(1)
            )
            
            previous_report = None
            for doc in previous_report_query.stream():
                previous_report = doc.to_dict()
                break
            
            if previous_report:
                # Check for significant request volume changes (>50% change)
                prev_total = previous_report.get("totalRequests", 0)
                if prev_total > 0:
                    change_percent = ((total_requests - prev_total) / prev_total) * 100
                    if abs(change_percent) > 50:
                        anomalies.append({
                            "type": "request_volume_spike",
                            "description": f"Request volume changed by {change_percent:.1f}%",
                            "severity": "high" if abs(change_percent) > 100 else "medium",
                            "currentValue": total_requests,
                            "previousValue": prev_total
                        })
                
                # Check for high failure rate (>10%)
                if total_requests > 0:
                    failure_rate = (failed_requests / total_requests) * 100
                    if failure_rate > 10:
                        anomalies.append({
                            "type": "high_failure_rate",
                            "description": f"Failure rate is {failure_rate:.1f}%",
                            "severity": "high" if failure_rate > 20 else "medium",
                            "failureRate": failure_rate
                        })
                
                # Check for model imbalance (one model >80% of requests)
                for model, count in requests_by_model.items():
                    if total_requests > 0:
                        model_percent = (count / total_requests) * 100
                        if model_percent > 80:
                            anomalies.append({
                                "type": "model_imbalance",
                                "description": f"{model} accounts for {model_percent:.1f}% of requests",
                                "severity": "low",
                                "model": model,
                                "percentage": model_percent
                            })
            
            # Always check absolute failure rate even without previous data
            elif total_requests > 0:
                failure_rate = (failed_requests / total_requests) * 100
                if failure_rate > 10:
                    anomalies.append({
                        "type": "high_failure_rate",
                        "description": f"Failure rate is {failure_rate:.1f}%",
                        "severity": "high" if failure_rate > 20 else "medium",
                        "failureRate": failure_rate
                    })
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
        
        return anomalies
    
    def get_report_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get reports within a date range
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of report documents
        """
        try:
            query = (
                self.reports_collection
                .where("weekStartDate", ">=", start_date.isoformat())
                .where("weekStartDate", "<=", end_date.isoformat())
                .order_by("weekStartDate", direction=firestore.Query.DESCENDING)
            )
            
            reports = []
            for doc in query.stream():
                report_data = doc.to_dict()
                report_data["reportId"] = doc.id
                reports.append(report_data)
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting reports: {str(e)}")
            return []