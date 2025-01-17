"""
Performance test runner for the Synapse API.
"""
import os
import sys
import asyncio

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import logging
import json
from datetime import datetime
from tests.performance.load_test import SynapseLoadTest
from tests.performance.chaos_test import SynapseStressTest
from tests.performance.memory_test import MemoryTest
from tests.performance.stability_test import StabilityTest

# Configure logging
os.makedirs('logs/performance', exist_ok=True)
log_file = f'logs/performance/performance_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s/%(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

async def run_test(test_name: str, test_instance) -> dict:
    """Run a single test and return results."""
    logger.info(f"Starting {test_name}...")
    try:
        if asyncio.iscoroutinefunction(test_instance.run):
            results = await test_instance.run()
        else:
            results = test_instance.run()
        logger.info(f"{test_name} completed successfully")
        return results
    except Exception as e:
        logger.error(f"{test_name} failed: {str(e)}")
        return {"error": str(e)}

async def main():
    """Run all performance tests."""
    logger.info("Starting performance test suite")
    
    try:
        # Set test environment
        os.environ["ENV"] = "test"
        all_results = {}
        
        # Define test configurations
        tests = [
            ("Load Tests", SynapseLoadTest()),
            ("Chaos Tests", SynapseStressTest()),
            ("Memory Tests", MemoryTest()),
            ("Stability Tests", StabilityTest())
        ]
        
        # Run each test type
        for test_name, test_instance in tests:
            all_results[test_name] = await run_test(test_name, test_instance)
            
        # Log final results
        logger.info("All test results:")
        logger.info(json.dumps(all_results, indent=2))
        
        # Save results to separate file
        results_file = log_file.replace('.log', '_results.json')
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        logger.info(f"Results saved to {results_file}")
        
        return all_results
        
    except Exception as e:
        logger.error(f"Performance tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        sys.exit(1) 