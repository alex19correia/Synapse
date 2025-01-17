"""
Chaos test for simulating system stress conditions.
"""
import logging
import asyncio
import random
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SynapseStressTest:
    """Chaos test implementation."""
    
    def __init__(self, duration_minutes=1):
        """Initialize chaos test."""
        self.duration = duration_minutes
        self.base_url = "http://localhost:8000"
        
    async def run(self) -> Dict[str, Any]:
        """Run chaos test scenarios."""
        logger.info("Starting chaos test...")
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=self.duration)
        
        results = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "scenarios_run": [],
            "errors": []
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                while datetime.now() < end_time:
                    # Run random chaos scenarios
                    scenario = random.choice([
                        self._high_concurrency,
                        self._large_payloads,
                        self._rapid_requests,
                        self._invalid_requests
                    ])
                    
                    scenario_result = await scenario(session)
                    results["scenarios_run"].append(scenario_result)
                    await asyncio.sleep(0.1)  # Small delay between scenarios
                    
        except Exception as e:
            logger.error(f"Chaos test error: {str(e)}")
            results["errors"].append(str(e))
            
        logger.info("Chaos test completed")
        return results
        
    async def _high_concurrency(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Simulate high concurrency scenario."""
        tasks = []
        for _ in range(10):  # Launch 10 concurrent requests
            tasks.append(self._make_request(
                session,
                "/v1/chat/completions",
                method="POST",
                json={
                    "messages": [{"role": "user", "content": "Test message"}],
                    "model": "test-model",
                    "use_rag": True
                }
            ))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            "name": "high_concurrency",
            "requests": len(results),
            "successes": sum(1 for r in results if not isinstance(r, Exception)),
            "failures": sum(1 for r in results if isinstance(r, Exception))
        }
        
    async def _large_payloads(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Simulate large payload scenario."""
        large_text = "Test " * 1000  # Create a large message
        try:
            result = await self._make_request(
                session,
                "/v1/chat/completions",
                method="POST",
                json={
                    "messages": [{"role": "user", "content": large_text}],
                    "model": "test-model",
                    "use_rag": True
                }
            )
            return {"name": "large_payloads", "status": "success", "size": len(large_text)}
        except Exception as e:
            return {"name": "large_payloads", "status": "error", "error": str(e)}
        
    async def _rapid_requests(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Simulate rapid request scenario."""
        results = []
        for _ in range(5):  # Send 5 quick requests
            try:
                result = await self._make_request(
                    session,
                    "/v1/chat/completions",
                    method="POST",
                    json={
                        "messages": [{"role": "user", "content": "Quick test"}],
                        "model": "test-model",
                        "use_rag": True
                    }
                )
                results.append({"status": "success"})
            except Exception as e:
                results.append({"status": "error", "error": str(e)})
            await asyncio.sleep(0.05)  # Small delay between requests
            
        return {
            "name": "rapid_requests",
            "requests": len(results),
            "successes": sum(1 for r in results if r["status"] == "success"),
            "failures": sum(1 for r in results if r["status"] == "error")
        }
        
    async def _invalid_requests(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Simulate invalid request scenario."""
        scenarios = [
            # Missing required fields
            {"messages": []},
            # Invalid message format
            {"messages": [{"invalid": "format"}], "model": "test-model"},
            # Invalid model name
            {"messages": [{"role": "user", "content": "Test"}], "model": "invalid-model"},
            # Extra invalid fields
            {"messages": [{"role": "user", "content": "Test"}], "model": "test-model", "invalid_field": True}
        ]
        
        results = []
        for scenario in scenarios:
            try:
                await self._make_request(
                    session,
                    "/v1/chat/completions",
                    method="POST",
                    json=scenario
                )
                results.append({"scenario": str(scenario), "status": "unexpected_success"})
            except Exception as e:
                results.append({"scenario": str(scenario), "status": "expected_error", "error": str(e)})
                
        return {
            "name": "invalid_requests",
            "scenarios_tested": len(results),
            "expected_errors": sum(1 for r in results if r["status"] == "expected_error"),
            "unexpected_successes": sum(1 for r in results if r["status"] == "unexpected_success")
        }
        
    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        method: str = "GET",
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request with the given session."""
        url = f"{self.base_url}{endpoint}"
        async with session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json() 