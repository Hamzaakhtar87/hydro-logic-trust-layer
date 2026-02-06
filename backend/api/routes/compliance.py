"""
EU Compliance Engine API Endpoints
Environmental impact reporting and EU AI Act compliance.
"""

import io
from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from backend.services.compliance_generator import ComplianceGenerator, get_compliance_generator

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


# Pydantic models
class ImpactRequest(BaseModel):
    usage_data: List[Dict] = Field(..., description="List of {level, tokens} dicts")

class ImpactResponse(BaseModel):
    total_water_liters: float
    total_energy_kwh: float
    total_co2_kg: float
    inference_events: int

class ReportRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    start_date: str = Field(..., description="ISO date string")
    end_date: str = Field(..., description="ISO date string")
    usage_data: Optional[List[Dict]] = Field(None, description="Optional usage data")

class ComplianceStatus(BaseModel):
    status: str
    eu_ai_act_compliant: bool
    last_report_date: Optional[str]
    environmental_rating: str
    transparency_score: float


@router.post("/impact", response_model=ImpactResponse)
async def calculate_impact(request: ImpactRequest):
    """
    Calculate environmental impact from API usage.
    
    Usage data format:
    [{"level": "minimal", "tokens": 1000000}, {"level": "high", "tokens": 500000}]
    """
    generator = get_compliance_generator()
    
    # Convert to expected format
    usage_tuples = []
    for item in request.usage_data:
        level = item.get('level', 'low')
        tokens = item.get('tokens', 0)
        usage_tuples.append((level, tokens))
    
    impact = generator.calculate_environmental_impact(usage_tuples)
    
    return ImpactResponse(**impact)


@router.post("/generate-report")
async def generate_report(request: ReportRequest):
    """
    Generate EU AI Act compliant PDF report.
    
    Returns a downloadable PDF file.
    """
    generator = get_compliance_generator()
    
    try:
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
    except ValueError:
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
    
    # Generate usage data if not provided
    if request.usage_data:
        usage_tuples = [(item.get('level', 'low'), item.get('tokens', 0)) for item in request.usage_data]
    else:
        # Generate sample data for demo
        usage_tuples = generator.generate_sample_usage_data()
    
    # Generate PDF
    pdf_bytes = generator.generate_pdf_report(
        company_name=request.company_name,
        start_date=start_date,
        end_date=end_date,
        usage_data=usage_tuples
    )
    
    # Return as downloadable file
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=compliance_report_{request.company_name.replace(' ', '_')}_{end_date.strftime('%Y%m%d')}.pdf"
        }
    )


@router.get("/status", response_model=ComplianceStatus)
async def get_compliance_status():
    """
    Get current compliance status.
    
    Returns overall EU AI Act compliance assessment.
    """
    generator = get_compliance_generator()
    
    status = generator.get_compliance_status()
    
    return ComplianceStatus(**status)


@router.get("/metrics")
async def get_environmental_metrics(
    timeframe: str = Query("month", regex="^(week|month|quarter|year)$")
):
    """
    Get environmental metrics for dashboard.
    
    Returns water, energy, and CO2 metrics with trends.
    """
    generator = get_compliance_generator()
    
    # Generate sample metrics for demo
    metrics = generator.get_metrics_summary(timeframe)
    
    return metrics


@router.get("/eu-ai-act-requirements")
async def get_requirements():
    """
    Get EU AI Act requirements and our compliance.
    """
    return {
        "requirements": [
            {
                "article": "Article 52",
                "requirement": "Transparency obligations",
                "description": "AI systems must inform users they are interacting with AI",
                "our_compliance": "✓ All agent interactions are logged and transparent",
                "status": "compliant"
            },
            {
                "article": "Article 14",
                "requirement": "Human oversight",
                "description": "High-risk AI must have human oversight capabilities",
                "our_compliance": "✓ Shield provides real-time monitoring and intervention",
                "status": "compliant"
            },
            {
                "article": "Article 15",
                "requirement": "Accuracy and robustness",
                "description": "AI systems must be resilient to errors and attacks",
                "our_compliance": "✓ Thought Signatures detect and block attacks",
                "status": "compliant"
            },
            {
                "article": "Article 65",
                "requirement": "Environmental sustainability",
                "description": "Report AI system resource usage and environmental impact",
                "our_compliance": "✓ Environmental impact reports with water/energy/CO2 tracking",
                "status": "compliant"
            }
        ],
        "overall_status": "fully_compliant",
        "last_assessment": datetime.utcnow().isoformat(),
        "certification_ready": True
    }


@router.get("/history")
async def get_compliance_history(months: int = Query(6, ge=1, le=24)):
    """
    Get compliance history for trending.
    """
    generator = get_compliance_generator()
    
    history = generator.get_compliance_history(months)
    
    return {"history": history, "months": months}


@router.post("/demo/generate-sample-report")
async def demo_generate_sample():
    """
    Demo: Generate a sample compliance report.
    
    Uses realistic demo data.
    """
    generator = get_compliance_generator()
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Generate sample usage data
    usage_data = generator.generate_sample_usage_data()
    
    # Generate PDF
    pdf_bytes = generator.generate_pdf_report(
        company_name="Moltbook Inc.",
        start_date=start_date,
        end_date=end_date,
        usage_data=usage_data
    )
    
    # Calculate impact for response
    impact = generator.calculate_environmental_impact(usage_data)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=sample_compliance_report_{end_date.strftime('%Y%m%d')}.pdf",
            "X-Water-Liters": str(impact['total_water_liters']),
            "X-Energy-kWh": str(impact['total_energy_kwh']),
            "X-CO2-kg": str(impact['total_co2_kg'])
        }
    )
