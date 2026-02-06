# System Architecture

## Overview

Hydro-Logic Trust Layer is a three-product platform built on top of Gemini 3's advanced capabilities.

```
                                    ┌─────────────────┐
                                    │   AI Agents     │
                                    │   (Moltbook)    │
                                    └────────┬────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                     HYDRO-LOGIC TRUST LAYER                        │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                      API GATEWAY                            │   │
│  │                    (FastAPI + CORS)                         │   │
│  └────────────────────────────────────────────────────────────┘   │
│         │                    │                    │                │
│         ▼                    ▼                    ▼                │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐   │
│  │   SHIELD     │   │   FINOPS     │   │    COMPLIANCE        │   │
│  │   MODULE     │   │   MODULE     │   │      MODULE          │   │
│  │              │   │              │   │                      │   │
│  │ attack_      │   │ routing_     │   │ compliance_          │   │
│  │ detector.py  │   │ engine.py    │   │ generator.py         │   │
│  │              │   │              │   │                      │   │
│  │ thought_     │   │              │   │                      │   │
│  │ signature.py │   │              │   │                      │   │
│  └──────────────┘   └──────────────┘   └──────────────────────┘   │
│         │                    │                    │                │
│         └────────────────────┴────────────────────┘                │
│                              │                                     │
│                              ▼                                     │
│                    ┌──────────────────┐                           │
│                    │  GEMINI CLIENT   │                           │
│                    │                  │                           │
│                    │ gemini_client.py │                           │
│                    └────────┬─────────┘                           │
│                              │                                     │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   GEMINI 3 API   │
                    │                  │
                    │ • Thinking Model │
                    │ • Flash Model    │
                    │ • Signatures     │
                    └──────────────────┘
```

## Component Details

### 1. Gemini Client (`backend/core/gemini_client.py`)

Central interface to Gemini API:
- Manages API authentication
- Extracts Thought Signatures from responses
- Supports both thinking and standard models
- Tracks token usage for billing

### 2. Thought Signature Verifier (`backend/core/thought_signature.py`)

Behavioral fingerprinting system:
- Builds baselines from historical signatures
- Compares new signatures against baseline
- Uses multiple similarity metrics
- Adaptive threshold for false positive reduction

### 3. Attack Detector (`backend/core/attack_detector.py`)

Multi-layer threat detection:
- Layer 1: Signature verification
- Layer 2: Pattern matching (regex)
- Layer 3: Keyword detection
- Layer 4: Behavioral analysis
- Layer 5: Response anomaly detection

### 4. FinOps Router (`backend/core/routing_engine.py`)

Query classification and routing:
- Analyzes query complexity
- Maps to optimal thinking level
- Tracks cost savings
- Provides routing explanations

### 5. Compliance Generator (`backend/services/compliance_generator.py`)

EU AI Act reporting:
- Calculates environmental impact
- Generates PDF reports
- Tracks compliance status
- Provides audit trail

## Data Flow

### Shield Verification Flow

```
1. Agent receives user message
2. Agent calls Gemini API
3. Agent sends (message, response) to Shield
4. Shield extracts Thought Signature
5. Shield compares to agent's baseline
6. Shield runs attack pattern checks
7. Shield returns verdict (allow/warn/block)
8. Agent proceeds or blocks based on verdict
```

### FinOps Routing Flow

```
1. Application receives query
2. Query sent to FinOps for classification
3. FinOps analyzes complexity
4. FinOps returns optimal thinking_level
5. Application calls Gemini with recommended settings
6. Cost savings tracked and reported
```

### Compliance Report Flow

```
1. Admin requests compliance report
2. Engine aggregates usage data
3. Engine calculates environmental impact
4. Engine generates PDF with:
   - Company information
   - Environmental metrics
   - Compliance checklist
   - Audit trail
5. PDF returned for download
```

## Security Considerations

1. **API Key Protection**: Keys stored in environment, never in code
2. **CORS Configuration**: Restrict origins in production
3. **Rate Limiting**: Prevent abuse of verification endpoints
4. **Audit Logging**: All security events logged
5. **Signature Integrity**: Hashes verify data hasn't been tampered

## Scalability

- **Stateless API**: Can scale horizontally
- **In-Memory Baselines**: Fast but requires sticky sessions or shared cache for production
- **Database Ready**: Architecture supports database for persistence
- **WebSocket**: Real-time updates scale with connection pooling

## Production Recommendations

1. Add Redis for shared baseline storage
2. Implement proper database (PostgreSQL)
3. Add API authentication (JWT/OAuth)
4. Configure production CORS
5. Set up monitoring (Prometheus/Grafana)
6. Enable TLS for all endpoints
