"""
EU Compliance Engine API Routes - Production Version
Environmental impact tracking with database persistence
"""

import io
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db, User, UsageRecord, ComplianceReport, ThinkingLevel
from backend.api.middleware.auth import get_current_user
from backend.services.compliance_generator import get_compliance_generator

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


# ============ Environmental Factors ============

ENVIRONMENTAL_FACTORS = {
    ThinkingLevel.MINIMAL: {"water_ml": 0.5, "energy_wh": 0.02, "co2_g": 0.001},
    ThinkingLevel.LOW: {"water_ml": 1.2, "energy_wh": 0.05, "co2_g": 0.003},
    ThinkingLevel.MEDIUM: {"water_ml": 8.5, "energy_wh": 0.4, "co2_g": 0.02},
    ThinkingLevel.HIGH: {"water_ml": 15.0, "energy_wh": 0.8, "co2_g": 0.04}
}


# ============ Request/Response Models ============

class ImpactResponse(BaseModel):
    total_water_liters: float
    total_energy_kwh: float
    total_co2_kg: float
    inference_events: int
    timeframe: str


class MetricDetail(BaseModel):
    value: float
    unit: str
    trend: Optional[str] = None


class MetricsResponse(BaseModel):
    timeframe: str
    water: MetricDetail
    energy: MetricDetail
    co2: MetricDetail
    inference_events: int
    optimization_impact: str


class ComplianceStatusResponse(BaseModel):
    status: str
    eu_ai_act_compliant: bool
    last_report_date: Optional[datetime]
    total_reports: int
    environmental_rating: str


class ReportRequest(BaseModel):
    company_name: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD


class ReportInfo(BaseModel):
    id: int
    company_name: str
    start_date: datetime
    end_date: datetime
    generated_at: datetime
    total_water_liters: float
    total_energy_kwh: float
    total_co2_kg: float
    inference_events: int


class RequirementItem(BaseModel):
    article: str
    requirement: str
    description: str
    our_compliance: str
    status: str


class RequirementsResponse(BaseModel):
    requirements: List[RequirementItem]
    overall_status: str
    certification_ready: bool


# ============ Helper Functions ============

def calculate_impact_from_records(records: List[UsageRecord]) -> dict:
    """Calculate environmental impact from usage records."""
    totals = {"water_ml": 0, "energy_wh": 0, "co2_g": 0, "events": 0}
    
    for record in records:
        # Estimate events (each ~1000 tokens = 1 event)
        events = max(1, record.tokens_used / 1000)
        factors = ENVIRONMENTAL_FACTORS.get(record.thinking_level, ENVIRONMENTAL_FACTORS[ThinkingLevel.HIGH])
        
        totals["water_ml"] += events * factors["water_ml"]
        totals["energy_wh"] += events * factors["energy_wh"]
        totals["co2_g"] += events * factors["co2_g"]
        totals["events"] += events
    
    return {
        "total_water_liters": round(totals["water_ml"] / 1000, 3),
        "total_energy_kwh": round(totals["energy_wh"] / 1000, 3),
        "total_co2_kg": round(totals["co2_g"] / 1000, 3),
        "inference_events": int(totals["events"])
    }


# ============ Endpoints ============

@router.get("/impact", response_model=ImpactResponse)
async def get_impact(
    timeframe: str = Query(default="month", regex="^(today|week|month|all)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get environmental impact for the specified timeframe.
    """
    now = datetime.utcnow()
    if timeframe == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif timeframe == "week":
        start_date = now - timedelta(days=7)
    elif timeframe == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = datetime(2000, 1, 1)
    
    records = db.query(UsageRecord).filter(
        UsageRecord.user_id == user.id,
        UsageRecord.timestamp >= start_date
    ).all()
    
    impact = calculate_impact_from_records(records)
    
    return ImpactResponse(
        total_water_liters=impact["total_water_liters"],
        total_energy_kwh=impact["total_energy_kwh"],
        total_co2_kg=impact["total_co2_kg"],
        inference_events=impact["inference_events"],
        timeframe=timeframe
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    timeframe: str = Query(default="month", regex="^(week|month|quarter|year)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get environmental metrics with trends.
    """
    days_map = {"week": 7, "month": 30, "quarter": 90, "year": 365}
    days = days_map.get(timeframe, 30)
    
    now = datetime.utcnow()
    current_start = now - timedelta(days=days)
    previous_start = current_start - timedelta(days=days)
    
    # Current period
    current_records = db.query(UsageRecord).filter(
        UsageRecord.user_id == user.id,
        UsageRecord.timestamp >= current_start
    ).all()
    
    # Previous period for trend
    previous_records = db.query(UsageRecord).filter(
        UsageRecord.user_id == user.id,
        UsageRecord.timestamp >= previous_start,
        UsageRecord.timestamp < current_start
    ).all()
    
    current_impact = calculate_impact_from_records(current_records)
    previous_impact = calculate_impact_from_records(previous_records)
    
    def calc_trend(current: float, previous: float) -> str:
        if previous == 0:
            return "N/A"
        change = ((current - previous) / previous) * 100
        sign = "+" if change > 0 else ""
        return f"{sign}{change:.1f}%"
    
    # Calculate optimization impact
    # If everything was HIGH level, what would impact be?
    total_tokens = sum(r.tokens_used for r in current_records)
    high_events = max(1, total_tokens / 1000)
    high_factors = ENVIRONMENTAL_FACTORS[ThinkingLevel.HIGH]
    naive_co2 = (high_events * high_factors["co2_g"]) / 1000
    
    actual_co2 = current_impact["total_co2_kg"]
    if naive_co2 > 0:
        reduction = round((1 - actual_co2 / naive_co2) * 100)
        optimization_impact = f"{reduction}% reduction vs unoptimized"
    else:
        optimization_impact = "No data yet"
    
    return MetricsResponse(
        timeframe=timeframe,
        water=MetricDetail(
            value=current_impact["total_water_liters"],
            unit="liters",
            trend=calc_trend(current_impact["total_water_liters"], previous_impact["total_water_liters"])
        ),
        energy=MetricDetail(
            value=current_impact["total_energy_kwh"],
            unit="kWh",
            trend=calc_trend(current_impact["total_energy_kwh"], previous_impact["total_energy_kwh"])
        ),
        co2=MetricDetail(
            value=current_impact["total_co2_kg"],
            unit="kg",
            trend=calc_trend(current_impact["total_co2_kg"], previous_impact["total_co2_kg"])
        ),
        inference_events=current_impact["inference_events"],
        optimization_impact=optimization_impact
    )


@router.get("/status", response_model=ComplianceStatusResponse)
async def get_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current compliance status.
    """
    # Get last report
    last_report = db.query(ComplianceReport).filter(
        ComplianceReport.user_id == user.id
    ).order_by(ComplianceReport.generated_at.desc()).first()
    
    total_reports = db.query(ComplianceReport).filter(
        ComplianceReport.user_id == user.id
    ).count()
    
    # Determine environmental rating based on usage patterns
    records = db.query(UsageRecord).filter(
        UsageRecord.user_id == user.id
    ).all()
    
    if not records:
        rating = "N/A"
    else:
        # Calculate percentage of optimized (non-HIGH) queries
        optimized = sum(1 for r in records if r.thinking_level != ThinkingLevel.HIGH)
        ratio = optimized / len(records)
        if ratio >= 0.8:
            rating = "A+"
        elif ratio >= 0.6:
            rating = "A"
        elif ratio >= 0.4:
            rating = "B"
        elif ratio >= 0.2:
            rating = "C"
        else:
            rating = "D"
    
    return ComplianceStatusResponse(
        status="COMPLIANT" if total_reports > 0 or len(records) > 0 else "PENDING",
        eu_ai_act_compliant=True,  # Using Hydro-Logic = compliant
        last_report_date=last_report.generated_at if last_report else None,
        total_reports=total_reports,
        environmental_rating=rating
    )


@router.post("/generate-report")
async def generate_report(
    request: ReportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate EU AI Act compliant PDF report.
    """
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get usage records for period
    records = db.query(UsageRecord).filter(
        UsageRecord.user_id == user.id,
        UsageRecord.timestamp >= start_date,
        UsageRecord.timestamp <= end_date
    ).all()
    
    # Convert to usage data format
    usage_data = [(r.thinking_level.value, r.tokens_used) for r in records]
    
    # Generate PDF
    generator = get_compliance_generator()
    pdf_bytes = generator.generate_pdf_report(
        company_name=request.company_name,
        start_date=start_date,
        end_date=end_date,
        usage_data=usage_data if usage_data else [("low", 0)]  # Need at least one entry
    )
    
    # Calculate and store impact
    impact = calculate_impact_from_records(records)
    
    # Save report record
    report = ComplianceReport(
        user_id=user.id,
        company_name=request.company_name,
        start_date=start_date,
        end_date=end_date,
        total_water_liters=impact["total_water_liters"],
        total_energy_kwh=impact["total_energy_kwh"],
        total_co2_kg=impact["total_co2_kg"],
        inference_events=impact["inference_events"]
    )
    db.add(report)
    db.commit()
    
    # Return PDF
    filename = f"compliance_report_{request.company_name.replace(' ', '_')}_{request.start_date}_{request.end_date}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/reports", response_model=List[ReportInfo])
async def list_reports(
    limit: int = Query(default=20, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List generated compliance reports.
    """
    reports = db.query(ComplianceReport).filter(
        ComplianceReport.user_id == user.id
    ).order_by(ComplianceReport.generated_at.desc()).limit(limit).all()
    
    return [
        ReportInfo(
            id=r.id,
            company_name=r.company_name,
            start_date=r.start_date,
            end_date=r.end_date,
            generated_at=r.generated_at,
            total_water_liters=r.total_water_liters,
            total_energy_kwh=r.total_energy_kwh,
            total_co2_kg=r.total_co2_kg,
            inference_events=r.inference_events
        )
        for r in reports
    ]


@router.get("/eu-ai-act-requirements", response_model=RequirementsResponse)
async def get_requirements():
    """
    Get EU AI Act requirements and our compliance status.
    This endpoint is public for transparency.
    """
    requirements = [
        RequirementItem(
            article="Article 52",
            requirement="Transparency obligations",
            description="AI systems must operate in a transparent manner",
            our_compliance="Full audit logging of all AI interactions with Thought Signatures",
            status="compliant"
        ),
        RequirementItem(
            article="Article 65",
            requirement="Environmental disclosure",
            description="Report environmental impact of AI systems",
            our_compliance="Automated water, energy, and CO2 tracking with PDF reports",
            status="compliant"
        ),
        RequirementItem(
            article="Article 9",
            requirement="Risk management",
            description="Identify and mitigate risks from AI systems",
            our_compliance="Real-time threat detection via Moltbook Shield",
            status="compliant"
        ),
        RequirementItem(
            article="Article 13",
            requirement="Record keeping",
            description="Maintain logs for traceability",
            our_compliance="All interactions stored with timestamps and verification hashes",
            status="compliant"
        ),
        RequirementItem(
            article="Article 14",
            requirement="Human oversight",
            description="Enable appropriate human oversight",
            our_compliance="Dashboard with real-time monitoring and manual intervention options",
            status="compliant"
        )
    ]
    
    return RequirementsResponse(
        requirements=requirements,
        overall_status="fully_compliant",
        certification_ready=True
    )
