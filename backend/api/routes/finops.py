"""
FinOps Gateway API Routes - Production Version
Cost optimization with database persistence
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db, User, UsageRecord, ThinkingLevel
from backend.api.middleware.auth import get_current_user
from backend.core.routing_engine import get_router, ThinkingLevel as CoreThinkingLevel
from backend.core.gemini_client import get_gemini_client

router = APIRouter(prefix="/api/finops", tags=["FinOps"])


# ============ Pricing Constants ============

PRICING = {
    "minimal": 0.075,   # $/1K tokens
    "low": 0.15,
    "medium": 1.25,
    "high": 2.50
}


# ============ Request/Response Models ============

class RouteRequest(BaseModel):
    query: str
    context: Optional[dict] = None


class QueryStats(BaseModel):
    word_count: int
    question_count: int
    character_count: int


class RouteResponse(BaseModel):
    thinking_level: str
    cost_multiplier: float
    cost_per_1k_tokens: float
    potential_savings_percent: float
    reasoning: List[str]
    query_stats: QueryStats


class RecordUsageRequest(BaseModel):
    query: str
    thinking_level: str
    tokens_used: int


class UsageRecordResponse(BaseModel):
    id: int
    query: str
    thinking_level: str
    tokens_used: int
    optimized_cost: float
    naive_cost: float
    savings: float
    timestamp: datetime


class SavingsResponse(BaseModel):
    timeframe: str
    optimized_cost: float
    naive_cost: float
    savings: float
    savings_percent: float
    queries_processed: int


class BreakdownItem(BaseModel):
    level: str
    count: int
    tokens: int
    cost: float


class BreakdownResponse(BaseModel):
    by_level: List[BreakdownItem]
    total_cost: float
    total_queries: int
    total_tokens: int


class HistoryItem(BaseModel):
    date: str
    optimized: float
    naive: float
    queries: int


# ============ Endpoints ============

@router.post("/route", response_model=RouteResponse)
async def route_query(
    request: RouteRequest,
    user: User = Depends(get_current_user)
):
    """
    Get optimal thinking level for a query.
    Does not record usage - use /record after completing the actual API call.
    """
    router_engine = get_router()
    
    # Get routing decision
    result = router_engine.explain_routing_decision(request.query, request.context)
    
    return RouteResponse(
        thinking_level=result["thinking_level"],
        cost_multiplier=result["cost_multiplier"],
        cost_per_1k_tokens=result["cost_per_1k_tokens"],
        potential_savings_percent=result["potential_savings_percent"],
        reasoning=result["reasoning"],
        query_stats=QueryStats(
            word_count=result["query_stats"]["word_count"],
            question_count=result["query_stats"]["question_count"],
            character_count=result["query_stats"]["character_count"]
        )
    )


@router.post("/record", response_model=UsageRecordResponse)
async def record_usage(
    request: RecordUsageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record actual API usage for tracking and savings calculation.
    Call this after making the actual Gemini API call.
    """
    level = request.thinking_level.lower()
    if level not in PRICING:
        level = "high"
    
    optimized_cost = (request.tokens_used / 1000) * PRICING[level]
    naive_cost = (request.tokens_used / 1000) * PRICING["high"]
    savings = naive_cost - optimized_cost
    
    # Map to enum
    level_map = {
        "minimal": ThinkingLevel.MINIMAL,
        "low": ThinkingLevel.LOW,
        "medium": ThinkingLevel.MEDIUM,
        "high": ThinkingLevel.HIGH
    }
    
    record = UsageRecord(
        user_id=user.id,
        query=request.query[:500],  # Truncate for storage
        thinking_level=level_map.get(level, ThinkingLevel.HIGH),
        tokens_used=request.tokens_used,
        optimized_cost=optimized_cost,
        naive_cost=naive_cost,
        savings=savings
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return UsageRecordResponse(
        id=record.id,
        query=record.query,
        thinking_level=record.thinking_level.value,
        tokens_used=record.tokens_used,
        optimized_cost=record.optimized_cost,
        naive_cost=record.naive_cost,
        savings=record.savings,
        timestamp=record.timestamp
    )


@router.get("/savings", response_model=SavingsResponse)
async def get_savings(
    timeframe: str = Query(default="month", regex="^(today|week|month|all)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cost savings statistics for the specified timeframe.
    """
    # Calculate date range
    now = datetime.utcnow()
    if timeframe == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif timeframe == "week":
        start_date = now - timedelta(days=7)
    elif timeframe == "month":
        start_date = now - timedelta(days=30)
    else:  # all
        start_date = datetime(2000, 1, 1)
    
    # Query aggregates
    result = db.query(
        func.sum(UsageRecord.optimized_cost).label("optimized"),
        func.sum(UsageRecord.naive_cost).label("naive"),
        func.sum(UsageRecord.savings).label("savings"),
        func.count(UsageRecord.id).label("count")
    ).filter(
        UsageRecord.user_id == user.id,
        UsageRecord.timestamp >= start_date
    ).first()
    
    optimized = result.optimized or 0
    naive = result.naive or 0
    savings = result.savings or 0
    count = result.count or 0
    
    savings_percent = (savings / naive * 100) if naive > 0 else 0
    
    return SavingsResponse(
        timeframe=timeframe,
        optimized_cost=round(optimized, 2),
        naive_cost=round(naive, 2),
        savings=round(savings, 2),
        savings_percent=round(savings_percent, 1),
        queries_processed=count
    )


@router.get("/breakdown", response_model=BreakdownResponse)
async def get_breakdown(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cost breakdown by thinking level.
    """
    # Query by level
    results = db.query(
        UsageRecord.thinking_level,
        func.count(UsageRecord.id).label("count"),
        func.sum(UsageRecord.tokens_used).label("tokens"),
        func.sum(UsageRecord.optimized_cost).label("cost")
    ).filter(
        UsageRecord.user_id == user.id
    ).group_by(UsageRecord.thinking_level).all()
    
    breakdown = []
    total_cost = 0
    total_queries = 0
    total_tokens = 0
    
    for row in results:
        count = row.count or 0
        tokens = row.tokens or 0
        cost = row.cost or 0
        
        breakdown.append(BreakdownItem(
            level=row.thinking_level.value,
            count=count,
            tokens=tokens,
            cost=round(cost, 2)
        ))
        
        total_cost += cost
        total_queries += count
        total_tokens += tokens
    
    return BreakdownResponse(
        by_level=breakdown,
        total_cost=round(total_cost, 2),
        total_queries=total_queries,
        total_tokens=total_tokens
    )


@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    days: int = Query(default=7, ge=1, le=90),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily cost history for charts.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query daily aggregates
    results = db.query(
        func.date(UsageRecord.timestamp).label("date"),
        func.sum(UsageRecord.optimized_cost).label("optimized"),
        func.sum(UsageRecord.naive_cost).label("naive"),
        func.count(UsageRecord.id).label("queries")
    ).filter(
        UsageRecord.user_id == user.id,
        UsageRecord.timestamp >= start_date
    ).group_by(func.date(UsageRecord.timestamp)).order_by("date").all()
    
    history = []
    for row in results:
        history.append(HistoryItem(
            date=str(row.date),
            optimized=round(row.optimized or 0, 2),
            naive=round(row.naive or 0, 2),
            queries=row.queries or 0
        ))
    
    return history


@router.get("/pricing")
async def get_pricing():
    """
    Get current pricing information.
    This endpoint is public (no auth required for transparency).
    """
    return {
        "pricing": {
            "minimal": {"cost_per_1k_tokens": 0.075, "cost_multiplier": 0.03},
            "low": {"cost_per_1k_tokens": 0.15, "cost_multiplier": 0.06},
            "medium": {"cost_per_1k_tokens": 1.25, "cost_multiplier": 0.50},
            "high": {"cost_per_1k_tokens": 2.50, "cost_multiplier": 1.00}
        },
        "note": "Gemini 3 uses thinking_level (minimal/low/medium/high). Prices are estimates."
    }


class GenerateRequest(BaseModel):
    """Request for the integrated route + generate endpoint."""
    query: str
    context: Optional[dict] = None
    force_level: Optional[str] = None  # Override automatic routing


class GenerateResponse(BaseModel):
    """Response from the integrated route + generate endpoint."""
    # The actual AI response
    content: str
    # Routing information
    thinking_level: str
    recommended_level: str
    # Cost information
    tokens_used: int
    optimized_cost: float
    naive_cost: float
    savings: float
    savings_percent: float
    # Metadata
    thought_signature: str
    thinking_tokens: int
    output_tokens: int
    reasoning: List[str]


@router.post("/generate", response_model=GenerateResponse)
async def generate_with_routing(
    request: GenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🚀 REAL GEMINI INTEGRATION: Route query to optimal level AND call Gemini.
    
    This endpoint combines routing + generation in one step:
    1. Analyzes query complexity
    2. Determines optimal thinking_level
    3. Calls Gemini with that level
    4. Records usage and calculates savings
    5. Returns response with cost data
    
    This is the core FinOps integration that actually saves money.
    """
    router_engine = get_router()
    
    # Step 1: Determine optimal thinking level
    routing_decision = router_engine.explain_routing_decision(
        request.query, 
        request.context
    )
    
    # Allow override if specified
    if request.force_level and request.force_level in ['minimal', 'low', 'medium', 'high']:
        thinking_level = request.force_level
    else:
        thinking_level = routing_decision['thinking_level']
    
    # Step 2: Call Gemini with the optimal level
    try:
        gemini = get_gemini_client()
        
        gemini_result = gemini.generate_with_thinking(
            prompt=request.query,
            thinking_level=thinking_level,
            context=request.context
        )
        
        if gemini_result.get('error'):
            raise Exception(gemini_result['error'])
        
    except Exception as e:
        return GenerateResponse(
            content=f"[Gemini API Error: {str(e)}]",
            thinking_level="error",
            recommended_level=routing_decision['thinking_level'],
            tokens_used=0,
            optimized_cost=0.0,
            naive_cost=0.0,
            savings=0.0,
            savings_percent=0.0,
            thought_signature="error",
            thinking_tokens=0,
            output_tokens=0,
            reasoning=["Error calling Gemini API"]
        )
    
    # Step 3: Calculate costs
    thinking_tokens = gemini_result.get('thinking_tokens', 0)
    output_tokens = gemini_result.get('output_tokens', 0)
    total_tokens = thinking_tokens + output_tokens
    
    optimized_cost = (total_tokens / 1000) * PRICING.get(thinking_level, PRICING['high'])
    naive_cost = (total_tokens / 1000) * PRICING['high']
    savings = naive_cost - optimized_cost
    savings_percent = (savings / naive_cost * 100) if naive_cost > 0 else 0
    
    # Step 4: Record usage
    level_map = {
        "minimal": ThinkingLevel.MINIMAL,
        "low": ThinkingLevel.LOW,
        "medium": ThinkingLevel.MEDIUM,
        "high": ThinkingLevel.HIGH
    }
    
    record = UsageRecord(
        user_id=user.id,
        query=request.query[:500],
        thinking_level=level_map.get(thinking_level, ThinkingLevel.HIGH),
        tokens_used=total_tokens,
        optimized_cost=optimized_cost,
        naive_cost=naive_cost,
        savings=savings
    )
    db.add(record)
    db.commit()
    
    return GenerateResponse(
        content=gemini_result.get('content', ''),
        thinking_level=thinking_level,
        recommended_level=routing_decision['thinking_level'],
        tokens_used=total_tokens,
        optimized_cost=round(optimized_cost, 6),
        naive_cost=round(naive_cost, 6),
        savings=round(savings, 6),
        savings_percent=round(savings_percent, 1),
        thought_signature=gemini_result.get('thought_signature', ''),
        thinking_tokens=thinking_tokens,
        output_tokens=output_tokens,
        reasoning=routing_decision.get('reasoning', [])
    )


@router.post("/demo-savings")
async def demo_cost_savings(
    user: User = Depends(get_current_user)
):
    """
    🎯 DEMO: Demonstrate cost savings for hackathon presentation.
    
    Shows how different query types get routed to different thinking levels.
    """
    router_engine = get_router()
    
    demo_queries = [
        {"query": "Hello!", "expected_level": "minimal"},
        {"query": "What is the capital of France?", "expected_level": "low"},
        {"query": "Compare and contrast machine learning and deep learning approaches for image classification", "expected_level": "medium"},
        {"query": "Design a comprehensive security architecture for a multi-tenant AI platform that handles sensitive healthcare data while ensuring HIPAA compliance, implementing zero-trust principles, and providing audit trails", "expected_level": "high"},
        {"query": "Thanks!", "expected_level": "minimal"},
        {"query": "Explain quantum computing", "expected_level": "low"},
        {"query": "What are the pros and cons of microservices vs monolithic architecture? Also discuss when to use each approach.", "expected_level": "medium"},
        {"query": "Analyze the security vulnerabilities in this authentication flow and design a threat model", "expected_level": "high"},
    ]
    
    results = []
    total_optimized = 0.0
    total_naive = 0.0
    
    for demo in demo_queries:
        routing = router_engine.explain_routing_decision(demo["query"])
        
        # Simulate 1000 tokens per query
        tokens = 1000
        optimized_cost = (tokens / 1000) * PRICING.get(routing['thinking_level'], PRICING['high'])
        naive_cost = (tokens / 1000) * PRICING['high']
        
        total_optimized += optimized_cost
        total_naive += naive_cost
        
        results.append({
            "query": demo["query"][:60] + "..." if len(demo["query"]) > 60 else demo["query"],
            "expected_level": demo["expected_level"],
            "actual_level": routing['thinking_level'],
            "matched": routing['thinking_level'] == demo["expected_level"],
            "reasoning": routing['reasoning'],
            "optimized_cost": f"${optimized_cost:.4f}",
            "naive_cost": f"${naive_cost:.4f}",
            "savings_percent": f"{routing['potential_savings_percent']:.0f}%"
        })
    
    total_savings = total_naive - total_optimized
    
    return {
        "demo_results": results,
        "summary": {
            "total_queries": len(results),
            "correct_routing": sum(1 for r in results if r["matched"]),
            "total_optimized_cost": f"${total_optimized:.4f}",
            "total_naive_cost": f"${total_naive:.4f}",
            "total_savings": f"${total_savings:.4f}",
            "savings_percent": f"{(total_savings / total_naive * 100):.1f}%" if total_naive > 0 else "0%"
        }
    }

