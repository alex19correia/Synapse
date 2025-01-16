from typing import Dict, Any, Optional
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge

from src.utils.logger import get_logger

logger = get_logger("core_analytics")

# Métricas
RECOMMENDATIONS = Counter(
    'synapse_recommendations_total',
    'Total number of recommendations made',
    ['type', 'status']
)

RECOMMENDATION_LATENCY = Histogram(
    'synapse_recommendation_duration_seconds',
    'Time spent generating recommendations',
    ['type']
)

RECOMMENDATION_QUALITY = Gauge(
    'synapse_recommendation_quality',
    'Quality score of recommendations',
    ['type']
)

def track_recommendation(
    rec_type: str,
    status: str = 'success',
    duration: Optional[float] = None,
    quality_score: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Registra uma recomendação feita pelo sistema.
    
    Args:
        rec_type: Tipo da recomendação
        status: Status da recomendação (success/error)
        duration: Duração da geração da recomendação em segundos
        quality_score: Score de qualidade da recomendação (0-1)
        metadata: Metadados adicionais
    """
    try:
        # Incrementa contador
        RECOMMENDATIONS.labels(
            type=rec_type,
            status=status
        ).inc()
        
        # Registra latência se fornecida
        if duration is not None:
            RECOMMENDATION_LATENCY.labels(
                type=rec_type
            ).observe(duration)
            
        # Registra qualidade se fornecida
        if quality_score is not None:
            RECOMMENDATION_QUALITY.labels(
                type=rec_type
            ).set(quality_score)
            
        # Log com metadados
        log_data = {
            'type': rec_type,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        if duration is not None:
            log_data['duration'] = duration
            
        if quality_score is not None:
            log_data['quality_score'] = quality_score
            
        logger.info(f"Recommendation tracked: {log_data}")
        
    except Exception as e:
        logger.error(f"Error tracking recommendation: {str(e)}")
        # Re-raise para não silenciar erros inesperados
        raise 