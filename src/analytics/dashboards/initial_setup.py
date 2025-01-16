from posthog import Posthog

def setup_initial_dashboard(posthog_client):
    """Configura dashboard inicial do Synapse"""
    
    # 1. User Engagement Dashboard
    engagement_metrics = {
        "title": "User Engagement",
        "metrics": [
            "Daily Active Users",
            "Messages Sent",
            "Features Used"
        ]
    }
    
    # 2. System Health Dashboard
    system_metrics = {
        "title": "System Health",
        "metrics": [
            "Error Rate",
            "Response Latency",
            "Memory Usage"
        ]
    }
    
    # 3. LLM Performance Dashboard
    llm_metrics = {
        "title": "LLM Performance",
        "metrics": [
            "Token Usage",
            "Response Time",
            "Cache Hit Rate"
        ]
    }

    return {
        "engagement": engagement_metrics,
        "system": system_metrics,
        "llm": llm_metrics
    } 