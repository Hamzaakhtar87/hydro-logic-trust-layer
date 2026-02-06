"""
FinOps Gateway API Endpoints
Cost optimization and query routing for Gemini API.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from backend.core.routing_engine import FinOpsRouter, ThinkingLevel, get_router

router = APIRouter(prefix="/api/finops", tags=["finops"])


# Pydantic models
class RouteRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query to classify")
    context: Optional[Dict] = Field(None, description="Optional context")

class RouteResponse(BaseModel):
    thinking_level: str
    token_budget: int
    cost_per_1k_tokens: float
    potential_savings_percent: float
    reasoning: List[str]
    query_stats: Dict

class SavingsResponse(BaseModel):
    timeframe: str
    optimized_cost: float
    naive_cost: float
    savings: float
    savings_percent: float
    queries_processed: int

class BreakdownResponse(BaseModel):
    by_level: Dict[str, Dict]
    total_cost: float
    total_queries: int

class CostHistoryItem(BaseModel):
    date: str
    optimized: float
    naive: float

class AnalyzeRequest(BaseModel):
    queries: List[str] = Field(..., min_items=1, max_items=100)
    tokens_per_query: int = Field(1000, ge=100, le=100000)


@router.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """
    Get optimal thinking_level for a query.
    
    Analyzes the query complexity and returns:
    - Recommended thinking level
    - Token budget
    - Cost estimates
    - Reasoning explanation
    """
    router_engine = get_router()
    
    explanation = router_engine.explain_routing_decision(request.query, request.context)
    
    return RouteResponse(**explanation)


@router.get("/savings", response_model=SavingsResponse)
async def get_savings(
    timeframe: str = Query("today", regex="^(today|week|month|all)$")
):
    """
    Get cost savings statistics.
    
    Timeframes: today, week, month, all
    """
    router_engine = get_router()
    
    summary = router_engine.get_usage_summary(timeframe)
    
    return SavingsResponse(**summary)


@router.get("/breakdown")
async def get_cost_breakdown():
    """
    Get cost breakdown by thinking_level.
    
    Shows how queries are distributed across levels
    and associated costs.
    """
    router_engine = get_router()
    
    summary = router_engine.get_usage_summary("all")
    stats = router_engine.get_total_stats()
    
    return BreakdownResponse(
        by_level={
            level: summary['level_breakdown'].get(level, {'count': 0, 'cost': 0})
            for level in ['minimal', 'low', 'medium', 'high']
        },
        total_cost=stats['total_optimized_cost'],
        total_queries=stats['total_queries']
    )


@router.get("/history")
async def get_cost_history(days: int = Query(7, ge=1, le=30)):
    """
    Get cost history for chart visualization.
    
    Returns daily optimized vs naive costs.
    """
    # Generate sample history for demo
    # In production, this would come from database
    from datetime import timedelta
    
    history = []
    base_date = datetime.utcnow()
    
    # Generate realistic demo data
    import random
    random.seed(42)  # Consistent demo data
    
    for i in range(days, 0, -1):
        date = base_date - timedelta(days=i)
        naive_cost = random.uniform(200, 400)
        # Hydro-Logic provides 40-60% savings
        optimized_cost = naive_cost * random.uniform(0.40, 0.60)
        
        history.append(CostHistoryItem(
            date=date.strftime("%Y-%m-%d"),
            optimized=round(optimized_cost, 2),
            naive=round(naive_cost, 2)
        ))
    
    return history


@router.post("/analyze-batch")
async def analyze_batch(request: AnalyzeRequest):
    """
    Analyze a batch of queries for cost estimation.
    
    Useful for estimating costs before running queries.
    """
    router_engine = get_router()
    
    # Build query list with tokens
    queries = [(q, request.tokens_per_query) for q in request.queries]
    
    result = router_engine.calculate_savings(queries)
    
    # Add per-query breakdown
    per_query = []
    for query in request.queries:
        explanation = router_engine.explain_routing_decision(query)
        per_query.append({
            'query': query[:100] + '...' if len(query) > 100 else query,
            'level': explanation['thinking_level'],
            'reasoning': explanation['reasoning'][0] if explanation['reasoning'] else 'Standard classification'
        })
    
    return {
        **result,
        'queries': per_query
    }


@router.get("/pricing")
async def get_pricing():
    """
    Get current Gemini pricing by thinking level.
    """
    return {
        'pricing': {
            'minimal': {
                'per_million_tokens': 0.075,
                'description': 'Simple facts, greetings, confirmations',
                'token_budget': 1000
            },
            'low': {
                'per_million_tokens': 0.15,
                'description': 'Basic Q&A, straightforward tasks',
                'token_budget': 5000
            },
            'medium': {
                'per_million_tokens': 1.25,
                'description': 'Multi-step reasoning, comparisons',
                'token_budget': 15000
            },
            'high': {
                'per_million_tokens': 2.50,
                'description': 'Complex reasoning, safety-critical tasks',
                'token_budget': 32000
            }
        },
        'note': 'Hydro-Logic typically achieves 40-60% cost savings through intelligent routing'
    }


@router.post("/demo/process-queries")
async def demo_process_queries(count: int = Query(50, ge=10, le=200)):
    """
    Demo endpoint: Process sample queries to generate statistics.
    
    This populates the router with sample data for the dashboard demo.
    """
    router_engine = get_router()
    
    # Sample queries representing different complexity levels
    sample_queries = [
        # MINIMAL
        ("Hi there!", 500),
        ("Thanks!", 200),
        ("Yes", 100),
        ("What time is it?", 300),
        
        # LOW
        ("What is the capital of France?", 800),
        ("How do I reset my password?", 1000),
        ("Summarize this paragraph.", 2000),
        
        # MEDIUM
        ("Compare Python and JavaScript for web development.", 5000),
        ("Explain the pros and cons of microservices architecture.", 4000),
        ("What are the trade-offs between SQL and NoSQL databases?", 3500),
        
        # HIGH
        ("Design a comprehensive security audit system for AI agents.", 15000),
        ("Analyze this code for security vulnerabilities and exploits.", 10000),
        ("Create a detailed architecture for a distributed threat detection system.", 12000),
    ]
    
    processed = []
    import random
    
    for i in range(count):
        query, tokens = random.choice(sample_queries)
        # Add some variation
        tokens = int(tokens * random.uniform(0.8, 1.2))
        
        result = router_engine.calculate_query_cost(query, tokens)
        processed.append(result)
    
    stats = router_engine.get_total_stats()
    
    return {
        "message": f"Processed {count} sample queries",
        "stats": stats,
        "sample_results": processed[:5]
    }
