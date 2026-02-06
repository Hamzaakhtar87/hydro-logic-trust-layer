"""
Moltbook Shield API Routes - Production Version
Real-time threat detection with database persistence
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db, User, Agent, Interaction, Threat, ActionType, ThreatSeverity
from backend.api.middleware.auth import get_current_user, get_current_user_optional
from backend.core.attack_detector import get_detector
from backend.core.thought_signature import get_verifier

router = APIRouter(prefix="/api/shield", tags=["Shield"])


# ============ Request/Response Models ============

class VerifyRequest(BaseModel):
    agent_id: str
    message: str
    gemini_response: dict  # Should contain 'content' and 'thought_signature'


class ThreatInfo(BaseModel):
    type: str
    severity: str
    details: str


class VerifyResponse(BaseModel):
    is_safe: bool
    threats_detected: List[ThreatInfo]
    confidence: float
    action: str
    analysis_id: str
    analyzed_at: str


class AgentInfo(BaseModel):
    id: int
    agent_id: str
    name: Optional[str]
    created_at: datetime
    last_seen_at: Optional[datetime]
    baseline_built: bool
    interaction_count: int
    threat_count: int


class StatsResponse(BaseModel):
    agents_protected: int
    threats_blocked: int
    threats_warned: int
    total_interactions: int
    uptime: str


class ThreatRecord(BaseModel):
    id: int
    agent_id: str
    threat_type: str
    severity: str
    details: Optional[str]
    action: str
    detected_at: datetime


# ============ WebSocket for real-time threats ============

active_connections: List[WebSocket] = []


async def broadcast_threat(threat_data: dict):
    """Broadcast threat to all connected clients."""
    for connection in active_connections:
        try:
            await connection.send_json(threat_data)
        except:
            pass


# ============ Endpoints ============

@router.post("/verify", response_model=VerifyResponse)
async def verify_interaction(
    request: VerifyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify an agent interaction for security threats.
    Requires authentication.
    """
    detector = get_detector()
    
    # Get or create agent
    agent = db.query(Agent).filter(
        Agent.user_id == user.id,
        Agent.agent_id == request.agent_id
    ).first()
    
    if not agent:
        agent = Agent(
            user_id=user.id,
            agent_id=request.agent_id,
            baseline_signatures=[],
            baseline_built=False
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
    
    # Update last seen
    agent.last_seen_at = datetime.utcnow()
    
    # Analyze the interaction
    analysis = detector.analyze_interaction(
        agent_id=request.agent_id,
        message=request.message,
        gemini_response=request.gemini_response
    )
    
    # Create interaction record
    interaction = Interaction(
        agent_id=agent.id,
        message=request.message,
        response_content=request.gemini_response.get("content", ""),
        thought_signature=request.gemini_response.get("thought_signature", ""),
        is_safe=analysis["is_safe"],
        confidence=analysis["confidence"],
        action=ActionType(analysis["action"])
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    # Create threat records if any
    threats_info = []
    for threat in analysis.get("threats", []):
        severity_map = {
            "low": ThreatSeverity.LOW,
            "medium": ThreatSeverity.MEDIUM,
            "high": ThreatSeverity.HIGH,
            "critical": ThreatSeverity.CRITICAL
        }
        threat_record = Threat(
            interaction_id=interaction.id,
            threat_type=threat.get("type", "unknown"),
            severity=severity_map.get(threat.get("severity", "low"), ThreatSeverity.LOW),
            details=threat.get("details", "")
        )
        db.add(threat_record)
        threats_info.append(ThreatInfo(
            type=threat.get("type", "unknown"),
            severity=threat.get("severity", "low"),
            details=threat.get("details", "")
        ))
    
    db.commit()
    
    # Broadcast threat if detected
    if not analysis["is_safe"]:
        await broadcast_threat({
            "type": "threat_detected",
            "agent_id": request.agent_id,
            "action": analysis["action"],
            "threat_count": len(threats_info),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return VerifyResponse(
        is_safe=analysis["is_safe"],
        threats_detected=threats_info,
        confidence=analysis["confidence"],
        action=analysis["action"],
        analysis_id=f"analysis_{interaction.id}",
        analyzed_at=datetime.utcnow().isoformat()
    )


@router.post("/baseline/{agent_id}")
async def build_baseline(
    agent_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Build or rebuild behavioral baseline for an agent.
    """
    verifier = get_verifier()
    
    # Get agent
    agent = db.query(Agent).filter(
        Agent.user_id == user.id,
        Agent.agent_id == agent_id
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get recent interactions with signatures
    interactions = db.query(Interaction).filter(
        Interaction.agent_id == agent.id,
        Interaction.thought_signature != None,
        Interaction.thought_signature != ""
    ).order_by(Interaction.timestamp.desc()).limit(100).all()
    
    if len(interactions) < 5:
        raise HTTPException(
            status_code=400, 
            detail=f"Need at least 5 interactions to build baseline. Current: {len(interactions)}"
        )
    
    # Build baseline
    signatures = [i.thought_signature for i in interactions]
    verifier.build_baseline(agent_id, signatures)
    
    # Update agent
    agent.baseline_signatures = signatures[:50]  # Store last 50
    agent.baseline_built = True
    db.commit()
    
    return {
        "message": f"Baseline built for agent {agent_id}",
        "interactions_used": len(signatures),
        "built_at": datetime.utcnow().isoformat()
    }


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Shield statistics for the authenticated user.
    """
    # Count agents
    agent_count = db.query(Agent).filter(Agent.user_id == user.id).count()
    
    # Count interactions
    interaction_count = db.query(Interaction).join(Agent).filter(
        Agent.user_id == user.id
    ).count()
    
    # Count threats by action
    blocked_count = db.query(Interaction).join(Agent).filter(
        Agent.user_id == user.id,
        Interaction.action == ActionType.BLOCK
    ).count()
    
    warned_count = db.query(Interaction).join(Agent).filter(
        Agent.user_id == user.id,
        Interaction.action == ActionType.WARN
    ).count()
    
    return StatsResponse(
        agents_protected=agent_count,
        threats_blocked=blocked_count,
        threats_warned=warned_count,
        total_interactions=interaction_count,
        uptime="99.9%"  # Would come from monitoring in production
    )


@router.get("/threats", response_model=List[ThreatRecord])
async def get_threats(
    limit: int = Query(default=50, le=500),
    agent_id: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent threats for the authenticated user.
    """
    query = db.query(Threat).join(Interaction).join(Agent).filter(
        Agent.user_id == user.id
    )
    
    if agent_id:
        query = query.filter(Agent.agent_id == agent_id)
    
    threats = query.order_by(Threat.detected_at.desc()).limit(limit).all()
    
    result = []
    for threat in threats:
        interaction = threat.interaction
        agent = interaction.agent
        result.append(ThreatRecord(
            id=threat.id,
            agent_id=agent.agent_id,
            threat_type=threat.threat_type,
            severity=threat.severity.value,
            details=threat.details,
            action=interaction.action.value,
            detected_at=threat.detected_at
        ))
    
    return result


@router.get("/agents", response_model=List[AgentInfo])
async def list_agents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all agents for the authenticated user.
    """
    agents = db.query(Agent).filter(Agent.user_id == user.id).all()
    
    result = []
    for agent in agents:
        interaction_count = db.query(Interaction).filter(
            Interaction.agent_id == agent.id
        ).count()
        
        threat_count = db.query(Threat).join(Interaction).filter(
            Interaction.agent_id == agent.id
        ).count()
        
        result.append(AgentInfo(
            id=agent.id,
            agent_id=agent.agent_id,
            name=agent.name,
            created_at=agent.created_at,
            last_seen_at=agent.last_seen_at,
            baseline_built=agent.baseline_built,
            interaction_count=interaction_count,
            threat_count=threat_count
        ))
    
    return result


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an agent and all its data.
    """
    agent = db.query(Agent).filter(
        Agent.user_id == user.id,
        Agent.agent_id == agent_id
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    
    return {"message": f"Agent {agent_id} deleted"}


@router.websocket("/ws/threats")
async def threat_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time threat notifications.
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
