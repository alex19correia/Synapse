from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Union
from analytics.metrics import MetricsCollector
from api.routes.metrics.schemas import (
    LLMMetric, CacheMetric, UserMetric, ErrorMetric,
    LogMetric, ApiMetric, DurationMetric, MemoryMetric
)

router = APIRouter()

MetricType = Union[
    LLMMetric, CacheMetric, UserMetric, ErrorMetric,
    LogMetric, ApiMetric, DurationMetric, MemoryMetric
]

@router.post("/metrics/{metric_type}")
async def track_metric(metric_type: str, data: MetricType):
    try:
        match metric_type:
            case "llm":
                metric = LLMMetric(**data)
                await MetricsCollector.track_llm_request(
                    metric.model,
                    metric.duration,
                    metric.tokens,
                    metric.success
                )
            
            case "cache":
                metric = CacheMetric(**data)
                await MetricsCollector.track_cache_operation(
                    metric.operation_type,
                    metric.hit
                )
            
            case "user":
                metric = UserMetric(**data)
                await MetricsCollector.track_user_activity(
                    metric.user_id,
                    metric.session_duration
                )
            
            case "error":
                metric = ErrorMetric(**data)
                await MetricsCollector.track_error(
                    metric.error_type,
                    metric.component
                )
            
            case "log":
                metric = LogMetric(**data)
                await MetricsCollector.track_log(data.dict())
            
            case "api":
                metric = ApiMetric(**data)
                await MetricsCollector.track_api_request(data.dict())
            
            case "duration":
                metric = DurationMetric(**data)
                await MetricsCollector.track_duration(
                    metric.component,
                    metric.duration
                )
            
            case "memory":
                metric = MemoryMetric(**data)
                await MetricsCollector.update_memory_usage(
                    metric.component,
                    metric.usage
                )
            
            case _:
                raise HTTPException(400, "Invalid metric type")

        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, f"Invalid data format: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to track metric: {str(e)}") 