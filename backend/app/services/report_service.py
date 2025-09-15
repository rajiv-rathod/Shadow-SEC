"""
Report service for managing AI report generation and data gathering
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.schemas import ReportCreate
from backend.app.schemas.models import MarketData, NewsArticle
from backend.app.schemas.models import Report as ReportModel
from backend.app.schemas.models import SecFiling
from backend.app.schemas.models import Stock as StockModel

logger = logging.getLogger(__name__)


class ReportService:
    """Service for managing report generation and data aggregation"""

    def __init__(self, db: Session):
        self.db = db

    async def gather_analysis_data(
        self,
        stock_id: int,
        event_date: Optional[datetime] = None,
        include_sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Gather all relevant data for AI analysis

        Args:
            stock_id: Database ID of the stock
            event_date: Specific date to analyze (defaults to recent data)
            include_sources: List of data sources to include

        Returns:
            Dictionary containing all gathered data for analysis
        """
        try:
            # Get stock information
            stock = self.db.query(StockModel).filter(StockModel.id == stock_id).first()
            if not stock:
                raise ValueError(f"Stock with ID {stock_id} not found")

            # Set date range for analysis
            if event_date:
                start_date = event_date - timedelta(days=7)  # 7 days before event
                end_date = event_date + timedelta(days=1)  # 1 day after event
            else:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)  # Last 30 days

            data = {
                "stock_symbol": stock.symbol,
                "stock_name": stock.name,
                "analysis_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

            # Gather market data
            if not include_sources or "market_data" in include_sources:
                data["market_data"] = await self._gather_market_data(
                    stock_id, start_date, end_date
                )

            # Gather SEC filings
            if not include_sources or "sec_filing" in include_sources:
                data["sec_filings"] = await self._gather_sec_filings(
                    stock_id, start_date, end_date
                )

            # Gather news data
            if not include_sources or "news" in include_sources:
                data["news"] = await self._gather_news_data(
                    stock.symbol, start_date, end_date
                )

            logger.info(
                f"Gathered analysis data for {stock.symbol}: "
                f"market_data={len(data.get('market_data', []))}, "
                f"sec_filings={len(data.get('sec_filings', []))}, "
                f"news={len(data.get('news', []))}"
            )

            return data

        except Exception as e:
            logger.error(f"Failed to gather analysis data: {e}")
            raise

    async def _gather_market_data(
        self, stock_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Gather market data for the specified period"""
        try:
            market_data = (
                self.db.query(MarketData)
                .filter(
                    MarketData.stock_id == stock_id,
                    MarketData.timestamp >= start_date,
                    MarketData.timestamp <= end_date,
                )
                .order_by(MarketData.timestamp.desc())
                .all()
            )

            return [
                {
                    "timestamp": data.timestamp.isoformat(),
                    "open_price": data.open_price,
                    "high_price": data.high_price,
                    "low_price": data.low_price,
                    "close_price": data.close_price,
                    "volume": data.volume,
                    "price_change": data.price_change,
                    "price_change_percent": data.price_change_percent,
                }
                for data in market_data
            ]

        except Exception as e:
            logger.error(f"Failed to gather market data: {e}")
            return []

    async def _gather_sec_filings(
        self, stock_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Gather SEC filings for the specified period"""
        try:
            sec_filings = (
                self.db.query(SecFiling)
                .filter(
                    SecFiling.stock_id == stock_id,
                    SecFiling.filing_date >= start_date,
                    SecFiling.filing_date <= end_date,
                )
                .order_by(SecFiling.filing_date.desc())
                .all()
            )

            return [
                {
                    "filing_type": filing.filing_type,
                    "accession_number": filing.accession_number,
                    "filing_date": filing.filing_date.isoformat(),
                    "period_of_report": (
                        filing.period_of_report.isoformat()
                        if filing.period_of_report
                        else None
                    ),
                    "document_url": filing.document_url,
                    "text_content": (
                        filing.text_content[:2000] if filing.text_content else None
                    ),  # Limit content
                    "processed_data": filing.processed_data,
                }
                for filing in sec_filings
            ]

        except Exception as e:
            logger.error(f"Failed to gather SEC filings: {e}")
            return []

    async def _gather_news_data(
        self, stock_symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Gather news articles mentioning the stock"""
        try:
            # Query news articles that mention the stock symbol
            news_articles = (
                self.db.query(NewsArticle)
                .filter(
                    NewsArticle.mentioned_stocks.contains([stock_symbol]),
                    NewsArticle.published_at >= start_date,
                    NewsArticle.published_at <= end_date,
                )
                .order_by(NewsArticle.published_at.desc())
                .limit(50)
                .all()
            )

            return [
                {
                    "title": article.title,
                    "content": (
                        article.content[:1000] if article.content else None
                    ),  # Limit content
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_at": article.published_at.isoformat(),
                    "sentiment_score": article.sentiment_score,
                    "relevance_score": article.relevance_score,
                    "mentioned_stocks": article.mentioned_stocks,
                }
                for article in news_articles
            ]

        except Exception as e:
            logger.error(f"Failed to gather news data: {e}")
            return []

    async def create_report(self, report_data: ReportCreate) -> ReportModel:
        """Create a new report in the database"""
        try:
            report = ReportModel(**report_data.dict())
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)

            logger.info(f"Created new report with ID {report.id}")
            return report

        except Exception as e:
            logger.error(f"Failed to create report: {e}")
            self.db.rollback()
            raise

    async def get_recent_reports(
        self, stock_id: Optional[int] = None, limit: int = 10
    ) -> List[ReportModel]:
        """Get recent reports, optionally filtered by stock"""
        try:
            query = self.db.query(ReportModel)

            if stock_id:
                query = query.filter(ReportModel.stock_id == stock_id)

            reports = query.order_by(ReportModel.generated_at.desc()).limit(limit).all()

            return reports

        except Exception as e:
            logger.error(f"Failed to get recent reports: {e}")
            return []

    async def update_report_status(self, report_id: int, status: str) -> bool:
        """Update the status of a report"""
        try:
            report = (
                self.db.query(ReportModel).filter(ReportModel.id == report_id).first()
            )
            if not report:
                return False

            report.status = status
            if status == "published":
                report.published_at = datetime.now()

            self.db.commit()
            logger.info(f"Updated report {report_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Failed to update report status: {e}")
            self.db.rollback()
            return False
