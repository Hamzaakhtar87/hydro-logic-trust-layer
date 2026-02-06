# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-deployment-url.run.app`

## Authentication

Currently open for hackathon demo. Production should add JWT/API key authentication.

---

## Shield API

### POST /api/shield/verify

Verify an agent interaction for security threats.

**Request:**
```json
{
  "agent_id": "agent_123",
  "message": "User message to analyze",
  "gemini_response": {
    "content": "Agent's response",
    "thought_signature": "abc123..."
  }
}
```

**Response:**
```json
{
  "is_safe": true,
  "threats_detected": [],
  "confidence": 0.95,
  "action": "allow",
  "analysis_id": "analysis_20260206120000_1",
  "analyzed_at": "2026-02-06T12:00:00Z"
}
```

### GET /api/shield/threats

Get list of detected threats.

**Query Parameters:**
- `agent_id` (optional): Filter by agent
- `limit` (optional, default=100): Max results

**Response:**
```json
{
  "threats": [
    {
      "id": "threat_1",
      "agent_id": "agent_123",
      "threats": [{"type": "injection_pattern", "severity": "high"}],
      "action": "block",
      "timestamp": "2026-02-06T12:00:00Z"
    }
  ],
  "total": 42,
  "blocked": 15,
  "warned": 27
}
```

### GET /api/shield/stats

Get Shield statistics.

**Response:**
```json
{
  "agents_protected": 127,
  "threats_blocked": 42,
  "uptime": "99.8%",
  "last_24h": {
    "interactions": 1547,
    "threats": 12,
    "blocked": 5
  }
}
```

### WebSocket /api/shield/ws/threats

Real-time threat notifications.

**Incoming messages:**
- `ping`: Send to keep connection alive

**Outgoing messages:**
```json
{
  "type": "threat_detected",
  "threat": {...},
  "agent_id": "agent_123",
  "timestamp": "2026-02-06T12:00:00Z"
}
```

---

## FinOps API

### POST /api/finops/route

Get optimal thinking level for a query.

**Request:**
```json
{
  "query": "Compare Python and JavaScript for web development",
  "context": {"priority": "normal"}
}
```

**Response:**
```json
{
  "thinking_level": "medium",
  "token_budget": 15000,
  "cost_per_1k_tokens": 0.00125,
  "potential_savings_percent": 50.0,
  "reasoning": ["Multiple questions detected", "Reasoning keywords found"],
  "query_stats": {
    "word_count": 8,
    "question_count": 0,
    "character_count": 52
  }
}
```

### GET /api/finops/savings

Get cost savings statistics.

**Query Parameters:**
- `timeframe`: "today", "week", "month", or "all"

**Response:**
```json
{
  "timeframe": "today",
  "optimized_cost": 142.37,
  "naive_cost": 237.92,
  "savings": 95.55,
  "savings_percent": 40.2,
  "queries_processed": 1547
}
```

### GET /api/finops/breakdown

Get cost breakdown by thinking level.

**Response:**
```json
{
  "by_level": {
    "minimal": {"count": 847, "cost": 12.37},
    "low": {"count": 523, "cost": 45.21},
    "medium": {"count": 142, "cost": 67.43},
    "high": {"count": 35, "cost": 17.36}
  },
  "total_cost": 142.37,
  "total_queries": 1547
}
```

### GET /api/finops/history

Get cost history for charts.

**Query Parameters:**
- `days` (default=7): Number of days

**Response:**
```json
[
  {"date": "2026-02-01", "optimized": 135.20, "naive": 284.50},
  {"date": "2026-02-02", "optimized": 142.80, "naive": 298.20},
  ...
]
```

---

## Compliance API

### POST /api/compliance/impact

Calculate environmental impact.

**Request:**
```json
{
  "usage_data": [
    {"level": "minimal", "tokens": 1000000},
    {"level": "high", "tokens": 500000}
  ]
}
```

**Response:**
```json
{
  "total_water_liters": 1.847,
  "total_energy_kwh": 0.234,
  "total_co2_kg": 0.142,
  "inference_events": 1500
}
```

### POST /api/compliance/generate-report

Generate PDF compliance report.

**Request:**
```json
{
  "company_name": "Acme Corp",
  "start_date": "2026-01-01",
  "end_date": "2026-02-01",
  "usage_data": [...]  // Optional
}
```

**Response:** PDF file download

### GET /api/compliance/status

Get compliance status.

**Response:**
```json
{
  "status": "COMPLIANT",
  "eu_ai_act_compliant": true,
  "last_report_date": "2026-02-06T10:00:00Z",
  "environmental_rating": "A",
  "transparency_score": 0.98
}
```

### GET /api/compliance/metrics

Get environmental metrics.

**Query Parameters:**
- `timeframe`: "week", "month", "quarter", "year"

**Response:**
```json
{
  "timeframe": "month",
  "water": {"value": 125.5, "unit": "liters", "trend": "-3.1%"},
  "energy": {"value": 15.2, "unit": "kWh", "trend": "-5.2%"},
  "co2": {"value": 8.4, "unit": "kg", "trend": "-4.8%"},
  "optimization_impact": "43% reduction vs unoptimized",
  "carbon_offset_equivalent": "420 trees/year"
}
```

### GET /api/compliance/eu-ai-act-requirements

Get EU AI Act requirements and compliance status.

**Response:**
```json
{
  "requirements": [
    {
      "article": "Article 52",
      "requirement": "Transparency obligations",
      "description": "...",
      "our_compliance": "✓ All agent interactions logged",
      "status": "compliant"
    }
  ],
  "overall_status": "fully_compliant",
  "certification_ready": true
}
```

---

## Health & Utility

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-06T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "shield": "operational",
    "finops": "operational",
    "compliance": "operational"
  }
}
```

### GET /api

API information.

**Response:**
```json
{
  "name": "Hydro-Logic Trust Layer API",
  "version": "1.0.0",
  "description": "...",
  "endpoints": {...},
  "documentation": {
    "swagger": "/api/docs",
    "redoc": "/api/redoc"
  }
}
```
