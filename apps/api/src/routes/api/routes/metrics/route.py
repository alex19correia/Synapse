from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Dict, Any, Union, List
from analytics.metrics import MetricsCollector
from .schemas import (
    LLMMetric, CacheMetric, UserMetric, ErrorMetric,
    LogMetric, ApiMetric, DurationMetric, MemoryMetric
)
from .rate_limit import MetricsRateLimiter
from redis import Redis
from fastapi import Request

router = APIRouter()

# Configuração do Redis
redis = Redis.from_url("redis://localhost:6379")
rate_limiter = MetricsRateLimiter(redis)

MetricType = Union[
    LLMMetric, CacheMetric, UserMetric, ErrorMetric,
    LogMetric, ApiMetric, DurationMetric, MemoryMetric
]

async def check_rate_limit_single(request: Request, metric_type: str):
    """Rate limit para métricas individuais"""
    await rate_limiter.check_rate_limit(metric_type, False, None)

async def check_rate_limit_batch(request: Request, batch_size: int):
    """Rate limit para batches"""
    await rate_limiter.check_rate_limit(None, True, batch_size)

async def process_metric(metric_type: str, data: Dict[str, Any]) -> None:
    """Processa uma única métrica"""
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
                await MetricsCollector.track_log(data)
            
            case "api":
                metric = ApiMetric(**data)
                await MetricsCollector.track_api_request(data)
            
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
                raise ValueError("Invalid metric type")
    except Exception as e:
        raise ValueError(f"Failed to process metric: {str(e)}")

@router.post("/metrics/{metric_type}")
async def track_metric(
    request: Request,
    metric_type: str,
    data: MetricType,
    rate_check: None = Depends(check_rate_limit_single)
):
    try:
        await process_metric(metric_type, data.dict())
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, f"Invalid data format: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to track metric: {str(e)}")

@router.post("/metrics/batch")
async def track_metric_batch(
    request: Request,
    metrics: List[Dict[str, Any]],
    x_batch_size: int = Header(..., alias="X-Batch-Size"),
    rate_check: None = Depends(check_rate_limit_batch)
):
    """Processa um batch de métricas"""
    if len(metrics) != x_batch_size:
        raise HTTPException(400, "Batch size mismatch")

    errors = []
    for metric in metrics:
        try:
            await process_metric(metric["type"], metric["data"])
        except Exception as e:
            errors.append({
                "metric": metric,
                "error": str(e)
            })

    if errors:
        return {
            "success": False,
            "processed": len(metrics) - len(errors),
            "failed": len(errors),
            "errors": errors
        }

    return {
        "success": True,
        "processed": len(metrics)
    } 