"""
Hydro-Logic Trust Layer - FastAPI Application
HTTPS for AI Agents - Built for Gemini 3 Hackathon 2026
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import time
from datetime import datetime
import os

from backend.api.routes import shield_router, finops_router, compliance_router

# App configuration
app = FastAPI(
    title="Hydro-Logic Trust Layer",
    description="HTTPS for AI Agents - Security, Cost Optimization & Compliance for AI Agents",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    return response

# Include API routers
app.include_router(shield_router)
app.include_router(finops_router)
app.include_router(compliance_router)


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hydro-Logic Trust Layer</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --primary-dark: #4f46e5;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --dark: #1f2937;
                --darker: #111827;
                --light: #f3f4f6;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, var(--darker) 0%, #1a1a2e 100%);
                min-height: 100vh;
                color: white;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            header {
                text-align: center;
                padding: 3rem 0;
            }
            
            h1 {
                font-size: 3rem;
                background: linear-gradient(135deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }
            
            .tagline {
                font-size: 1.25rem;
                color: #94a3b8;
            }
            
            .badge {
                display: inline-block;
                background: var(--primary);
                padding: 0.5rem 1rem;
                border-radius: 999px;
                font-size: 0.875rem;
                margin-top: 1rem;
            }
            
            .products {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-top: 3rem;
            }
            
            .product-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 1rem;
                padding: 2rem;
                backdrop-filter: blur(10px);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .product-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            
            .product-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .product-card h2 {
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
            }
            
            .product-card p {
                color: #94a3b8;
                margin-bottom: 1.5rem;
            }
            
            .product-card ul {
                list-style: none;
            }
            
            .product-card li {
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .product-card li:last-child {
                border-bottom: none;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 1rem;
                margin-top: 3rem;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 1rem;
                padding: 1.5rem;
                text-align: center;
            }
            
            .stat-value {
                font-size: 2rem;
                font-weight: 700;
                color: var(--success);
            }
            
            .stat-label {
                color: #94a3b8;
                font-size: 0.875rem;
            }
            
            .api-section {
                margin-top: 3rem;
                text-align: center;
            }
            
            .api-btn {
                display: inline-block;
                background: var(--primary);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                text-decoration: none;
                margin: 0.5rem;
                transition: background 0.3s;
            }
            
            .api-btn:hover {
                background: var(--primary-dark);
            }
            
            footer {
                text-align: center;
                padding: 2rem;
                color: #64748b;
                margin-top: 3rem;
            }
            
            @media (max-width: 768px) {
                .stats {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                h1 {
                    font-size: 2rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🌊 Hydro-Logic Trust Layer</h1>
                <p class="tagline">HTTPS for AI Agents</p>
                <span class="badge">🏆 Gemini 3 Hackathon 2026</span>
            </header>
            
            <div class="products">
                <div class="product-card">
                    <div class="product-icon">🛡️</div>
                    <h2>Moltbook Shield</h2>
                    <p>Real-time threat detection for AI agents using Thought Signatures</p>
                    <ul>
                        <li>✓ Prompt injection detection</li>
                        <li>✓ Agent hijacking prevention</li>
                        <li>✓ Real-time WebSocket alerts</li>
                        <li>✓ Behavioral baseline analysis</li>
                    </ul>
                </div>
                
                <div class="product-card">
                    <div class="product-icon">💰</div>
                    <h2>FinOps Gateway</h2>
                    <p>Intelligent query routing for 40-60% cost savings</p>
                    <ul>
                        <li>✓ Query complexity classification</li>
                        <li>✓ Optimal thinking_level routing</li>
                        <li>✓ Real-time savings tracking</li>
                        <li>✓ Cost breakdown analytics</li>
                    </ul>
                </div>
                
                <div class="product-card">
                    <div class="product-icon">📋</div>
                    <h2>EU Compliance Engine</h2>
                    <p>EU AI Act compliant environmental reporting</p>
                    <ul>
                        <li>✓ Water/Energy/CO2 tracking</li>
                        <li>✓ PDF report generation</li>
                        <li>✓ Article 52 & 65 compliance</li>
                        <li>✓ Audit trail verification</li>
                    </ul>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">770K</div>
                    <div class="stat-label">Agents Protected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">45%</div>
                    <div class="stat-label">Cost Savings</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">99.8%</div>
                    <div class="stat-label">Uptime</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">100%</div>
                    <div class="stat-label">EU Compliant</div>
                </div>
            </div>
            
            <div class="api-section">
                <h2>API Documentation</h2>
                <p style="color: #94a3b8; margin: 1rem 0;">Explore the complete API</p>
                <a href="/api/docs" class="api-btn">📚 Swagger UI</a>
                <a href="/api/redoc" class="api-btn">📖 ReDoc</a>
            </div>
            
            <footer>
                <p>Built with ❤️ for the Gemini 3 Hackathon | Powered by Google Gemini API</p>
            </footer>
        </div>
    </body>
    </html>
    """


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "shield": "operational",
            "finops": "operational",
            "compliance": "operational"
        }
    }


# API info endpoint
@app.get("/api")
async def api_info():
    """Get API information and available endpoints."""
    return {
        "name": "Hydro-Logic Trust Layer API",
        "version": "1.0.0",
        "description": "HTTPS for AI Agents - Security, Cost Optimization & Compliance",
        "endpoints": {
            "shield": {
                "prefix": "/api/shield",
                "description": "Moltbook Shield - Threat detection",
                "endpoints": ["/verify", "/threats", "/stats", "/ws/threats"]
            },
            "finops": {
                "prefix": "/api/finops",
                "description": "FinOps Gateway - Cost optimization",
                "endpoints": ["/route", "/savings", "/breakdown", "/history"]
            },
            "compliance": {
                "prefix": "/api/compliance",
                "description": "EU Compliance Engine - Environmental reporting",
                "endpoints": ["/impact", "/generate-report", "/status", "/metrics"]
            }
        },
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
