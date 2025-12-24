from sqlmodel import SQLModel, Field, Relationship, Column, JSON, DateTime
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid


class UserRole(str, Enum):
    VISITOR = "visitor"
    MANAGER = "manager"
    ADMIN = "admin"
    ROOT = "root"


class LicensePlan(str, Enum):
    SOLO = "solo"
    AGENCY = "agency"
    WHITELABEL = "whitelabel"


class BotStatus(str, Enum):
    ACTIVE = "active"
    WARMUP = "warmup"
    BLOCKED = "blocked"
    DEAD = "dead"
    SUSPENDED = "suspended"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    username: Optional[str] = Field(index=True)
    first_name: Optional[str]
    last_name: Optional[str]
    
    role: UserRole = Field(default=UserRole.VISITOR)
    plan: Optional[LicensePlan]
    expiry_date: Optional[datetime]
    
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    organization_name: Optional[str]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime]
    login_count: int = Field(default=0)
    
    settings: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    statistics: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    licenses: List["License"] = Relationship(back_populates="user")
    bots: List["BotSession"] = Relationship(back_populates="owner")
    campaigns: List["Campaign"] = Relationship(back_populates="owner")
    payments: List["Payment"] = Relationship(back_populates="user")


class License(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key_code: str = Field(unique=True, index=True)
    plan_type: LicensePlan
    duration_days: int = Field(default=30)
    
    is_activated: bool = Field(default=False)
    activated_at: Optional[datetime]
    activated_by: Optional[int] = Field(foreign_key="user.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(foreign_key="user.id")
    
    price: float = Field(default=0.0)
    currency: str = Field(default="USD")
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="licenses")


class BotSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(index=True)
    session_string: str
    user_id: Optional[str]
    username: Optional[str]
    
    owner_id: int = Field(foreign_key="user.id")
    status: BotStatus = Field(default=BotStatus.ACTIVE)
    
    proxy_id: Optional[int] = Field(foreign_key="proxy.id")
    device_fingerprint: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    warmup_schedule: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    last_activity: Optional[datetime]
    messages_sent: int = Field(default=0)
    success_rate: float = Field(default=100.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    owner: User = Relationship(back_populates="bots")
    proxy: Optional["Proxy"] = Relationship(back_populates="bots")
    campaigns: List["CampaignBot"] = Relationship(back_populates="bot")


class Proxy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    type: str = Field(default="socks5")
    
    owner_id: int = Field(foreign_key="user.id")
    is_active: bool = Field(default=True)
    success_rate: float = Field(default=100.0)
    response_time: float = Field(default=0.0)
    
    last_check: Optional[datetime]
    failures_count: int = Field(default=0)
    
    geolocation: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    bots: List[BotSession] = Relationship(back_populates="proxy")
    owner: User = Relationship(back_populates="proxies")


class Campaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: str = Field(unique=True, default_factory=lambda: str(uuid.uuid4())[:8])
    
    owner_id: int = Field(foreign_key="user.id")
    name: str
    description: Optional[str]
    
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    type: str = Field(default="pm")
    
    targets_file: Optional[str]
    message_text: str
    media_path: Optional[str]
    buttons: Optional[List[Dict[str, Any]]] = Field(default=[], sa_column=Column(JSON))
    
    delay_min: int = Field(default=30)
    delay_max: int = Field(default=60)
    threads: int = Field(default=5)
    
    total_targets: int = Field(default=0)
    sent_count: int = Field(default=0)
    success_count: int = Field(default=0)
    failed_count: int = Field(default=0)
    
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    estimated_completion: Optional[datetime]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    owner: User = Relationship(back_populates="campaigns")
    campaign_bots: List["CampaignBot"] = Relationship(back_populates="campaign")


class CampaignBot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    bot_id: int = Field(foreign_key="botsession.id")
    
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime]
    
    targets_assigned: int = Field(default=0)
    targets_completed: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    
    # Relationships
    campaign: Campaign = Relationship(back_populates="campaign_bots")
    bot: BotSession = Relationship(back_populates="campaigns")


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
    invoice_id: str = Field(unique=True, index=True)
    amount: float
    currency: str = Field(default="USD")
    
    status: str = Field(default="pending")
    transaction_hash: Optional[str]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime]
    
    # Relationships
    user: User = Relationship(back_populates="payments")


class OSINTData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    
    data_type: str
    data: Dict[str, Any] = Field(sa_column=Column(JSON))
    filename: Optional[str]
    file_path: Optional[str]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime]
