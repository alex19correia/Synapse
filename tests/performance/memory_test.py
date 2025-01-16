"""Memory usage tests for the application."""
import tracemalloc
import time
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MemoryTest:
    def __init__(self, duration_minutes: float = 1, sample_interval: float = 1.0):
        self.duration = duration_minutes * 60  # Convert to seconds
        self.sample_interval = sample_interval
        self.process = psutil.Process()
        
    def run(self) -> Dict[str, Any]:
        """Run memory usage test."""
        logger.info("Starting memory test...")
        
        # Enable tracemalloc
        tracemalloc.start()
        
        try:
            start_time = time.time()
            samples = []
            
            while time.time() - start_time < self.duration:
                # Get memory snapshot
                current, peak = tracemalloc.get_traced_memory()
                memory_info = self.process.memory_info()
                
                sample = {
                    "timestamp": time.time(),
                    "rss": memory_info.rss / 1024 / 1024,  # Convert to MB
                    "vms": memory_info.vms / 1024 / 1024,  # Convert to MB
                    "traced_current": current / 1024 / 1024,  # Convert to MB
                    "traced_peak": peak / 1024 / 1024  # Convert to MB
                }
                samples.append(sample)
                time.sleep(self.sample_interval)
            
            # Calculate summary statistics
            summary = {
                "duration": self.duration,
                "samples": len(samples),
                "avg_rss": sum(s["rss"] for s in samples) / len(samples),
                "max_rss": max(s["rss"] for s in samples),
                "avg_vms": sum(s["vms"] for s in samples) / len(samples),
                "max_vms": max(s["vms"] for s in samples),
                "peak_traced_memory": max(s["traced_peak"] for s in samples)
            }
            
            logger.info(f"Memory test completed: {summary}")
            return summary
            
        finally:
            tracemalloc.stop()
            logger.info("Memory test stopped") 