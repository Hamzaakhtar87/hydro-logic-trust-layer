"""
Database models for Hydro-Logic Trust Layer
Production-ready SQLAlchemy models
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import enum
import os

Base = declarative_base()


# Enums
class ThinkingLevel(enum.Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ThreatSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(enum.Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


# User & Auth Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(64), unique=True, index=True, nullable=False)
    key_prefix = Column(String(12), nullable=False)  # For display: "hl_abc123..."
    name = Column(String(100), nullable=False, default="Default Key")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    @staticmethod
    def generate_key() -> tuple[str, str, str]:
        """Generate a new API key. Returns (full_key, key_hash, key_prefix)."""
        full_key = f"hl_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        key_prefix = full_key[:12]
        return full_key, key_hash, key_prefix
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for comparison."""
        return hashlib.sha256(key.encode()).hexdigest()


# Agent Models
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(String(100), index=True, nullable=False)  # External agent ID
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Baseline data for Shield
    baseline_signatures = Column(JSON, default=list)
    baseline_built = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    interactions = relationship("Interaction", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent {self.agent_id}>"


# Shield Models
class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    message = Column(Text, nullable=False)
    response_content = Column(Text, nullable=True)
    thought_signature = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Analysis results
    is_safe = Column(Boolean, default=True)
    confidence = Column(Float, default=1.0)
    action = Column(SQLEnum(ActionType), default=ActionType.ALLOW)
    
    # Relationships
    agent = relationship("Agent", back_populates="interactions")
    threats = relationship("Threat", back_populates="interaction", cascade="all, delete-orphan")


class Threat(Base):
    __tablename__ = "threats"
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    threat_type = Column(String(100), nullable=False)
    severity = Column(SQLEnum(ThreatSeverity), nullable=False)
    details = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interaction = relationship("Interaction", back_populates="threats")


# FinOps Models
class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    thinking_level = Column(SQLEnum(ThinkingLevel), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    optimized_cost = Column(Float, nullable=False)
    naive_cost = Column(Float, nullable=False)  # What it would have cost at HIGH level
    savings = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="usage_records")


# Compliance Models
class ComplianceReport(Base):
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Environmental metrics
    total_water_liters = Column(Float, default=0.0)
    total_energy_kwh = Column(Float, default=0.0)
    total_co2_kg = Column(Float, default=0.0)
    inference_events = Column(Integer, default=0)
    
    # Report file
    report_hash = Column(String(64), nullable=True)  # For verification


# Database setup
def get_database_url() -> str:
    """Get database URL from environment or use default SQLite."""
    return os.getenv("DATABASE_URL", "sqlite:///./hydro_logic.db")


def create_db_engine():
    """Create database engine."""
    url = get_database_url()
    # Handle SQLite
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


def init_db():
    """Initialize database tables."""
    engine = create_db_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def get_session_maker():
    """Get session maker for database."""
    engine = create_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
