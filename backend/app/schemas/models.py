"""
Database models for Shadow SEC application
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.core.database import Base


class Stock(Base):
    """Stock symbol and metadata"""

    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    market_data = relationship("MarketData", back_populates="stock")
    sec_filings = relationship("SecFiling", back_populates="stock")
    reports = relationship("Report", back_populates="stock")


class MarketData(Base):
    """Real-time market data for stocks"""

    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    price_change = Column(Float)
    price_change_percent = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    stock = relationship("Stock", back_populates="market_data")


class SecFiling(Base):
    """SEC filings data"""

    __tablename__ = "sec_filings"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    filing_type = Column(String(20), nullable=False)  # 10-K, 10-Q, 8-K, etc.
    accession_number = Column(String(50), unique=True, nullable=False)
    filing_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_of_report = Column(DateTime(timezone=True))
    document_url = Column(String(500))
    text_content = Column(Text)
    processed_data = Column(JSON)  # Structured data extracted from filing
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    stock = relationship("Stock", back_populates="sec_filings")


class NewsArticle(Base):
    """News articles related to stocks"""

    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000), unique=True)
    source = Column(String(100))
    author = Column(String(200))
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    sentiment_score = Column(Float)  # -1 to 1, negative to positive
    relevance_score = Column(Float)  # 0 to 1, how relevant to tracked stocks
    mentioned_stocks = Column(JSON)  # List of stock symbols mentioned
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    """AI-generated correlation reports"""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    report_type = Column(String(50), default="correlation_analysis")
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    confidence_score = Column(Float)  # 0 to 1
    correlations_found = Column(JSON)  # Structured correlation data
    data_sources = Column(JSON)  # References to source data used
    ai_model_version = Column(String(50))
    status = Column(String(20), default="draft")  # draft, under_review, published
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True))

    # Relationships
    stock = relationship("Stock", back_populates="reports")
    reviews = relationship("ReportReview", back_populates="report")


class ReportReview(Base):
    """Community reviews of AI reports"""

    __tablename__ = "report_reviews"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    reviewer_id = Column(String(50))  # Anonymous reviewer ID
    accuracy_rating = Column(Integer)  # 1-5 scale
    usefulness_rating = Column(Integer)  # 1-5 scale
    comments = Column(Text)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    report = relationship("Report", back_populates="reviews")


class EventTimeline(Base):
    """Timeline events for correlation analysis"""

    __tablename__ = "event_timeline"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # market_data, sec_filing, news
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    stock_symbols = Column(JSON)  # List of affected stock symbols
    title = Column(String(500))
    description = Column(Text)
    source_id = Column(
        Integer
    )  # ID of the source record (market_data, sec_filing, etc.)
    source_table = Column(String(50))  # Name of the source table
    event_metadata = Column(JSON)  # Additional event metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
