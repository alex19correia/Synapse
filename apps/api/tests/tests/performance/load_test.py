"""
Load testing scenarios for the Synapse API.
Uses Locust for distributed load testing.
"""
from locust import HttpUser, task, between
from typing import Dict, Any
import json
import random
import time
import logging
import sys

class SynapseUser(HttpUser):
    """Simulates a user interacting with the Synapse API."""
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token: str = None

    def on_start(self):
        """Login before starting tasks."""
        response = self.client.post("/v1/auth/login", json={
            "email": f"test{random.randint(1,1000)}@example.com",
            "password": "Test123!@#"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def basic_chat(self):
        """Basic chat completion task."""
        with self.client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "What is 2+2?"}
            ],
            "model": "deepseek-chat"
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def streaming_chat(self):
        """Streaming chat completion task."""
        with self.client.post(
            "/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Count to 3"}],
                "model": "deepseek-chat",
                "stream": True
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line.decode('utf-8').split('data: ')[1])
                            if data.get('finish_reason') == 'stop':
                                break
                    response.success()
                except Exception as e:
                    response.failure(str(e))
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def rag_chat(self):
        """RAG-enhanced chat completion task."""
        with self.client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "What documents do I have?"}
            ],
            "model": "deepseek-chat",
            "use_rag": True
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def document_management(self):
        """Document indexing and retrieval task."""
        # Index document
        with self.client.post("/v1/documents/index", json={
            "content": f"Test document {random.randint(1,1000)}",
            "metadata": {"source": "load-test"}
        }, catch_response=True) as response:
            if response.status_code == 200:
                doc_id = response.json()["document_id"]
                response.success()
                # Retrieve document
                with self.client.get(f"/v1/documents/{doc_id}", catch_response=True) as get_response:
                    if get_response.status_code == 200:
                        get_response.success()
                    else:
                        get_response.failure(f"Status code: {get_response.status_code}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def user_profile(self):
        """User profile retrieval task."""
        with self.client.get("/v1/user/profile", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

class SynapseLoadTest:
    """Load test configuration and execution."""
    def __init__(self, host: str = "http://localhost:8000"):
        self.host = host
        self.config = {
            "host": host,
            "users": [SynapseUser],
            "spawn_rate": 5,
            "num_users": 10,
            "run_time": "1m"
        }

    def run(self):
        """Run the load test."""
        from locust.env import Environment
        from locust.stats import stats_printer, stats_history
        from locust.log import setup_logging
        import gevent

        logger = logging.getLogger(__name__)
        logger.info("Starting load test...")

        # Setup logging
        setup_logging("INFO", None)

        try:
            # Create environment
            env = Environment(
                user_classes=[SynapseUser],
                host=self.host
            )
            logger.info(f"Created Locust environment with host: {self.host}")

            # Start environment
            env.create_local_runner()
            logger.info("Created local runner")
            
            # Start a greenlet that periodically outputs the current stats
            stats_printer_greenlet = gevent.spawn(stats_printer(env.stats))
            logger.info("Started stats printer")

            # Start the test
            env.runner.start(self.config["spawn_rate"], self.config["num_users"])
            logger.info(f"Started test with {self.config['num_users']} users at rate {self.config['spawn_rate']}/s")
            
            # Run for specified time
            start_time = time.time()
            duration = float(self.config["run_time"].replace("m", "")) * 60  # Convert minutes to seconds
            logger.info(f"Running test for {duration} seconds")
            
            try:
                while time.time() - start_time < duration:
                    gevent.sleep(1)
                    if int(time.time() - start_time) % 10 == 0:  # Log every 10 seconds
                        logger.info(f"Test running for {int(time.time() - start_time)} seconds...")
                        
            except KeyboardInterrupt:
                logger.info("Test interrupted by user")
            finally:
                # Stop the runner
                logger.info("Stopping test...")
                env.runner.quit()
                stats_printer_greenlet.kill()
                logger.info("Test stopped")
            
            # Get final stats
            stats = {
                "total_requests": env.stats.total.num_requests,
                "total_failures": env.stats.total.num_failures,
                "average_response_time": env.stats.total.avg_response_time,
                "requests_per_second": env.stats.total.current_rps,
                "percentiles": {
                    "50": env.stats.total.get_response_time_percentile(0.5),
                    "95": env.stats.total.get_response_time_percentile(0.95),
                    "99": env.stats.total.get_response_time_percentile(0.99)
                }
            }
            logger.info(f"Test completed with stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

if __name__ == "__main__":
    # Run load test
    try:
        test = SynapseLoadTest()
        results = test.run()
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Test failed: {str(e)}")
        sys.exit(1) 