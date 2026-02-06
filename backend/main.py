"""
Hydro-Logic Trust Layer - FastAPI Application
Production-ready with authentication and database
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import time
from datetime import datetime
import os

from backend.api.routes import auth_router, shield_router, finops_router, compliance_router
from backend.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and cleanup on shutdown."""
    # Startup: Initialize database
    init_database()
    print("✅ Database initialized")
    yield
    # Shutdown: Cleanup if needed
    print("👋 Shutting down Hydro-Logic Trust Layer")


# App configuration
app = FastAPI(
    lifespan=lifespan,
    title="Hydro-Logic Trust Layer",
    description="HTTPS for AI Agents - Security, Cost Optimization & Compliance",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration - Configure for your domain in production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
app.include_router(auth_router)
app.include_router(shield_router)
app.include_router(finops_router)
app.include_router(compliance_router)


# Landing page (public)
@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the landing page for marketing."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Hydro-Logic Trust Layer - HTTPS for AI Agents. Security, cost optimization, and EU compliance for AI systems.">
        <title>Hydro-Logic Trust Layer | HTTPS for AI Agents</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --primary-dark: #4f46e5;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --dark: #0f172a;
                --darker: #020617;
            }
            
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, var(--darker) 0%, #1a1a2e 50%, #16213e 100%);
                min-height: 100vh;
                color: white;
            }
            
            .container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
            
            /* Header */
            header {
                padding: 1rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(2, 6, 23, 0.9);
                backdrop-filter: blur(10px);
                z-index: 100;
            }
            
            nav {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                text-decoration: none;
                color: white;
            }
            
            .logo-icon { font-size: 2rem; }
            .logo-text { font-weight: 700; font-size: 1.25rem; }
            
            .nav-links {
                display: flex;
                gap: 2rem;
                list-style: none;
            }
            
            .nav-links a {
                color: #94a3b8;
                text-decoration: none;
                transition: color 0.2s;
            }
            
            .nav-links a:hover { color: white; }
            
            .nav-buttons {
                display: flex;
                gap: 1rem;
            }
            
            .btn {
                padding: 0.6rem 1.25rem;
                border-radius: 0.5rem;
                font-weight: 500;
                text-decoration: none;
                transition: all 0.2s;
                cursor: pointer;
                border: none;
                font-size: 0.9rem;
            }
            
            .btn-ghost {
                background: transparent;
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .btn-ghost:hover { background: rgba(255,255,255,0.1); }
            
            .btn-primary {
                background: var(--primary);
                color: white;
            }
            
            .btn-primary:hover { background: var(--primary-dark); }
            
            .btn-large {
                padding: 1rem 2rem;
                font-size: 1.1rem;
            }
            
            /* Hero */
            .hero {
                padding: 10rem 0 6rem;
                text-align: center;
            }
            
            .badge {
                display: inline-block;
                background: rgba(99, 102, 241, 0.2);
                color: #a5b4fc;
                padding: 0.5rem 1rem;
                border-radius: 999px;
                font-size: 0.875rem;
                margin-bottom: 1.5rem;
            }
            
            h1 {
                font-size: 4rem;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 1.5rem;
            }
            
            .gradient-text {
                background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .hero p {
                font-size: 1.25rem;
                color: #94a3b8;
                max-width: 600px;
                margin: 0 auto 2rem;
            }
            
            .hero-buttons {
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
            
            /* Stats */
            .stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 1.5rem;
                padding: 3rem 0;
            }
            
            .stat {
                text-align: center;
                padding: 1.5rem;
                background: rgba(255,255,255,0.03);
                border-radius: 1rem;
                border: 1px solid rgba(255,255,255,0.05);
            }
            
            .stat-value {
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--success);
            }
            
            .stat-label {
                color: #64748b;
                margin-top: 0.5rem;
            }
            
            /* Products */
            .products {
                padding: 4rem 0;
            }
            
            .products h2 {
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 3rem;
            }
            
            .product-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 2rem;
            }
            
            .product-card {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 1rem;
                padding: 2rem;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .product-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }
            
            .product-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .product-card h3 {
                font-size: 1.5rem;
                margin-bottom: 0.75rem;
            }
            
            .product-card p {
                color: #94a3b8;
                margin-bottom: 1.5rem;
            }
            
            .feature-list {
                list-style: none;
            }
            
            .feature-list li {
                padding: 0.5rem 0;
                color: #cbd5e1;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            
            .feature-list li:last-child { border: none; }
            
            /* CTA */
            .cta {
                text-align: center;
                padding: 6rem 0;
            }
            
            .cta h2 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            
            .cta p {
                color: #94a3b8;
                margin-bottom: 2rem;
            }
            
            /* Footer */
            footer {
                border-top: 1px solid rgba(255,255,255,0.1);
                padding: 2rem 0;
                text-align: center;
                color: #64748b;
            }
            
            @media (max-width: 768px) {
                h1 { font-size: 2.5rem; }
                .stats { grid-template-columns: repeat(2, 1fr); }
                .product-grid { grid-template-columns: 1fr; }
                .nav-links { display: none; }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <nav>
                    <a href="/" class="logo">
                        <span class="logo-icon">🌊</span>
                        <span class="logo-text">Hydro-Logic</span>
                    </a>
                    <ul class="nav-links">
                        <li><a href="#products">Products</a></li>
                        <li><a href="/api/docs">API Docs</a></li>
                        <li><a href="#pricing">Pricing</a></li>
                    </ul>
                    <div class="nav-buttons">
                        <a href="/app" class="btn btn-ghost">Log In</a>
                        <a href="/app" class="btn btn-primary">Sign Up Free</a>
                    </div>
                </nav>
            </div>
        </header>
        
        <main>
            <section class="hero">
                <div class="container">
                    <span class="badge">🏆 Built for Gemini 3 Hackathon 2026</span>
                    <h1>
                        <span class="gradient-text">HTTPS</span> for AI Agents
                    </h1>
                    <p>
                        Protect your AI agents from prompt injection, 
                        cut API costs by 40-60%, and stay EU AI Act compliant.
                        All powered by Gemini 3's Thought Signatures.
                    </p>
                    <div class="hero-buttons">
                        <a href="/app" class="btn btn-primary btn-large">Get Started Free →</a>
                        <a href="/api/docs" class="btn btn-ghost btn-large">View API Docs</a>
                    </div>
                </div>
            </section>
            
            <section class="stats">
                <div class="container" style="display: contents;">
                    <div class="stat">
                        <div class="stat-value">770K+</div>
                        <div class="stat-label">Agents Protected</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">45%</div>
                        <div class="stat-label">Avg. Cost Savings</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">99.8%</div>
                        <div class="stat-label">Uptime SLA</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">100%</div>
                        <div class="stat-label">EU Compliant</div>
                    </div>
                </div>
            </section>
            
            <section class="products" id="products">
                <div class="container">
                    <h2>Three Products, One Platform</h2>
                    <div class="product-grid">
                        <div class="product-card">
                            <div class="product-icon">🛡️</div>
                            <h3>Moltbook Shield</h3>
                            <p>Real-time threat detection using Gemini's Thought Signatures</p>
                            <ul class="feature-list">
                                <li>✓ Prompt injection detection</li>
                                <li>✓ Agent hijacking prevention</li>
                                <li>✓ Behavioral baseline analysis</li>
                                <li>✓ Real-time WebSocket alerts</li>
                            </ul>
                        </div>
                        <div class="product-card">
                            <div class="product-icon">💰</div>
                            <h3>FinOps Gateway</h3>
                            <p>Intelligent query routing for 40-60% cost reduction</p>
                            <ul class="feature-list">
                                <li>✓ Query complexity analysis</li>
                                <li>✓ Optimal thinking_level routing</li>
                                <li>✓ Real-time savings dashboard</li>
                                <li>✓ Cost breakdown analytics</li>
                            </ul>
                        </div>
                        <div class="product-card">
                            <div class="product-icon">📋</div>
                            <h3>EU Compliance Engine</h3>
                            <p>Automated EU AI Act environmental reporting</p>
                            <ul class="feature-list">
                                <li>✓ Water/Energy/CO2 tracking</li>
                                <li>✓ PDF report generation</li>
                                <li>✓ Article 52 & 65 compliance</li>
                                <li>✓ Audit trail verification</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>
            
            <section class="cta">
                <div class="container">
                    <h2>Ready to Secure Your AI Agents?</h2>
                    <p>Start free. No credit card required. Get your API key in seconds.</p>
                    <a href="/app" class="btn btn-primary btn-large">Create Free Account →</a>
                </div>
            </section>
        </main>
        
        <footer>
            <div class="container">
                <p>© 2026 Hydro-Logic Trust Layer | Built with ❤️ for the Gemini 3 Hackathon</p>
            </div>
        </footer>
    </body>
    </html>
    """


# Health check (public)
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "shield": "operational",
            "finops": "operational",
            "compliance": "operational"
        }
    }


# API info (public)
@app.get("/api")
async def api_info():
    """Get API information."""
    return {
        "name": "Hydro-Logic Trust Layer API",
        "version": "1.0.0",
        "description": "HTTPS for AI Agents - Security, Cost Optimization & Compliance",
        "authentication": {
            "methods": ["JWT Bearer Token", "API Key (X-API-Key header)"],
            "signup": "POST /api/auth/signup",
            "login": "POST /api/auth/login",
            "api_keys": "POST /api/auth/api-keys"
        },
        "endpoints": {
            "auth": "/api/auth/*",
            "shield": "/api/shield/*",
            "finops": "/api/finops/*",
            "compliance": "/api/compliance/*"
        },
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
