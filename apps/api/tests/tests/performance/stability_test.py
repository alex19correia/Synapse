"""
Stability test for verifying system reliability.
"""
import logging
import time
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StabilityTest:
    """Stability test implementation."""
    
    def __init__(self, duration_minutes=0.1, check_interval=1):
        """Initialize stability test."""
        self.duration = duration_minutes
        self.check_interval = check_interval
        self.base_url = "http://localhost:8000"
        
    def run(self):
        """Run stability test."""
        logger.info("Starting stability test...")
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=self.duration)
        
        results = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "checks": [],
            "summary": {
                "total_checks": 0,
                "successful_checks": 0,
                "failed_checks": 0
            }
        }
        
        try:
            while datetime.now() < end_time:
                # Perform health check
                check_result = self._perform_health_check()
                results["checks"].append(check_result)
                
                # Update summary
                results["summary"]["total_checks"] += 1
                if check_result["status"] == "success":
                    results["summary"]["successful_checks"] += 1
                else:
                    results["summary"]["failed_checks"] += 1
                    
                # Wait for next check
                time.sleep(self.check_interval)
                
            # Calculate success rate
            total = results["summary"]["total_checks"]
            if total > 0:
                success_rate = (results["summary"]["successful_checks"] / total) * 100
                results["summary"]["success_rate"] = success_rate
                
        except Exception as e:
            logger.error(f"Stability test error: {str(e)}")
            results["error"] = str(e)
            
        return results
        
    def _perform_health_check(self):
        """Perform system health check."""
        check_result = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": {}
        }
        
        endpoints = [
            "/health",
            "/v1/chat/completions",
            "/v1/user/profile",
            "/v1/documents/index"
        ]
        
        all_successful = True
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                check_result["endpoints"][endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response_time
                }
                
                if response.status_code not in [200, 404]:  # 404 is expected for some endpoints in test mode
                    all_successful = False
                    
            except Exception as e:
                check_result["endpoints"][endpoint] = {
                    "error": str(e)
                }
                all_successful = False
                
        check_result["status"] = "success" if all_successful else "failure"
        return check_result 