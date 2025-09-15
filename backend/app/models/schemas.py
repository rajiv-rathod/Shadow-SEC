"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Types of events in the timeline"""
    MARKET_DATA = "market_data"
    SEC_FILING = "sec_filing"
    NEWS = "news"


class ReportStatus(str, Enum):
    """Status of AI-generated reports"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    PUBLISHED = "published"


class FilingType(str, Enum):
    """Types of SEC filings"""
    FORM_10K = "10-K"
    FORM_10Q = "10-Q"
    FORM_8K = "8-K"
    FORM_DEF14A = "DEF 14A"


# Base models
class StockBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=255)
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None


class StockCreate(StockBase):
    pass


class Stock(StockBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Market Data models
class MarketDataBase(BaseModel):
    timestamp: datetime
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[int] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None


class MarketDataCreate(MarketDataBase):
    stock_id: int


class MarketData(MarketDataBase):
    id: int
    stock_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# SEC Filing models
class SecFilingBase(BaseModel):
    filing_type: FilingType
    accession_number: str = Field(..., min_length=1, max_length=50)
    filing_date: datetime
    period_of_report: Optional[datetime] = None
    document_url: Optional[str] = None
    text_content: Optional[str] = None
    processed_data: Optional[Dict[str, Any]] = None


class SecFilingCreate(SecFilingBase):
    stock_id: int


class SecFiling(SecFilingBase):
    id: int
    stock_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# News Article models
class NewsArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    mentioned_stocks: Optional[List[str]] = None


class NewsArticleCreate(NewsArticleBase):
    pass


class NewsArticle(NewsArticleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Report models
class ReportRequest(BaseModel):
    """Request to generate an AI report"""
    stock_symbol: str = Field(..., min_length=1, max_length=10)
    event_date: Optional[datetime] = None
    analysis_type: str = "correlation_analysis"
    include_sources: List[EventType] = [EventType.MARKET_DATA, EventType.SEC_FILING, EventType.NEWS]


class ReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    correlations_found: Optional[Dict[str, Any]] = None
    data_sources: Optional[Dict[str, Any]] = None
    ai_model_version: Optional[str] = None
    status: ReportStatus = ReportStatus.DRAFT


class ReportCreate(ReportBase):
    stock_id: int


class Report(ReportBase):
    id: int
    stock_id: int
    generated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportJob(BaseModel):
    """Response for async report generation"""
    job_id: str
    status: str
    message: str
    estimated_completion: Optional[datetime] = None


class ReportJobStatus(BaseModel):
    """Status check for report generation job"""
    job_id: str
    status: str  # pending, in_progress, completed, failed
    progress: int = Field(0, ge=0, le=100)
    result: Optional[Report] = None
    error_message: Optional[str] = None


# Review models
class ReportReviewBase(BaseModel):
    accuracy_rating: int = Field(..., ge=1, le=5)
    usefulness_rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    is_approved: bool = False


class ReportReviewCreate(ReportReviewBase):
    report_id: int
    reviewer_id: str = Field(..., min_length=1, max_length=50)


class ReportReview(ReportReviewBase):
    id: int
    report_id: int
    reviewer_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Timeline models
class TimelineEventBase(BaseModel):
    event_type: EventType
    event_date: datetime
    stock_symbols: List[str]
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TimelineEventCreate(TimelineEventBase):
    source_id: int
    source_table: str


class TimelineEvent(TimelineEventBase):
    id: int
    source_id: int
    source_table: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Response models
class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    database: str
    redis: str
    services: Dict[str, str]


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)