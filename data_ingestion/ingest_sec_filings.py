"""
SEC filings ingestion script for Shadow SEC
Uses SEC API to fetch and process regulatory filings
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, engine
from backend.app.schemas.models import Base, SecFiling, Stock

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecFilingIngester:
    """SEC filings ingestion service"""

    def __init__(self):
        """Initialize the SEC filings ingester"""
        self.db = SessionLocal()

        # SEC API configuration
        self.sec_base_url = "https://api.sec-api.io"
        self.headers = {"User-Agent": "Shadow-SEC/1.0 (opensource-financial-watchdog)"}

        if settings.SEC_API_KEY:
            self.headers["Authorization"] = f"Bearer {settings.SEC_API_KEY}"
            self.enabled = True
            logger.info("SEC API client initialized successfully")
        else:
            logger.warning("SEC API key not configured - using mock data")
            self.enabled = False

    async def ingest_recent_filings(self, days: int = 7):
        """Ingest recent SEC filings for all tracked stocks"""
        try:
            stocks = self.db.query(Stock).all()

            for stock in stocks:
                try:
                    filings = await self._fetch_recent_filings(stock.symbol, days)

                    for filing_data in filings:
                        await self._process_and_save_filing(stock.id, filing_data)

                    logger.info(f"Processed {len(filings)} filings for {stock.symbol}")

                    # Rate limiting
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Failed to process filings for {stock.symbol}: {e}")
                    continue

            logger.info("SEC filings ingestion completed")

        except Exception as e:
            logger.error(f"Failed to ingest SEC filings: {e}")

    async def _fetch_recent_filings(
        self, symbol: str, days: int
    ) -> List[Dict[str, Any]]:
        """Fetch recent filings for a stock symbol"""
        if not self.enabled:
            return self._generate_mock_filings(symbol, days)

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # SEC API query
            query = {
                "query": {
                    "query_string": {
                        "query": f"ticker:{symbol} AND filedAt:[{start_date.strftime('%Y-%m-%d')} TO {end_date.strftime('%Y-%m-%d')}]"
                    }
                },
                "from": "0",
                "size": "50",
                "sort": [{"filedAt": {"order": "desc"}}],
            }

            response = requests.post(
                f"{self.sec_base_url}/v2/filings/search",
                json=query,
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                filings = []

                for filing in data.get("filings", []):
                    filing_info = {
                        "filing_type": filing.get("formType"),
                        "accession_number": filing.get("accessionNo"),
                        "filing_date": datetime.strptime(
                            filing.get("filedAt"), "%Y-%m-%d"
                        ),
                        "period_of_report": filing.get("periodOfReport"),
                        "document_url": filing.get("linkToFilingDetails"),
                        "company_name": filing.get("companyName"),
                        "cik": filing.get("cik"),
                    }
                    filings.append(filing_info)

                return filings
            else:
                logger.error(f"SEC API request failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Failed to fetch SEC filings for {symbol}: {e}")
            return []

    def _generate_mock_filings(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Generate mock SEC filings data"""
        import random

        filing_types = ["10-K", "10-Q", "8-K", "DEF 14A"]
        mock_filings = []

        # Generate 1-3 random filings
        num_filings = random.randint(1, 3)

        for i in range(num_filings):
            filing_date = datetime.now() - timedelta(days=random.randint(1, days))

            mock_filing = {
                "filing_type": random.choice(filing_types),
                "accession_number": f"000{random.randint(100000, 999999)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}",
                "filing_date": filing_date,
                "period_of_report": filing_date - timedelta(days=90),
                "document_url": f"https://www.sec.gov/Archives/edgar/data/mock/{symbol.lower()}-filing-{i}.htm",
                "company_name": f"{symbol} Corporation",
                "cik": f"{random.randint(1000000, 9999999):010d}",
            }
            mock_filings.append(mock_filing)

        return mock_filings

    async def _process_and_save_filing(
        self, stock_id: int, filing_data: Dict[str, Any]
    ):
        """Process and save a SEC filing to the database"""
        try:
            # Check if filing already exists
            existing_filing = (
                self.db.query(SecFiling)
                .filter(SecFiling.accession_number == filing_data["accession_number"])
                .first()
            )

            if existing_filing:
                logger.debug(f"Filing {filing_data['accession_number']} already exists")
                return

            # Extract text content from filing
            text_content = await self._extract_filing_text(
                filing_data.get("document_url")
            )

            # Process and structure the filing data
            processed_data = await self._process_filing_content(
                filing_data, text_content
            )

            # Create filing record
            filing = SecFiling(
                stock_id=stock_id,
                filing_type=filing_data["filing_type"],
                accession_number=filing_data["accession_number"],
                filing_date=filing_data["filing_date"],
                period_of_report=filing_data.get("period_of_report"),
                document_url=filing_data.get("document_url"),
                text_content=(
                    text_content[:10000] if text_content else None
                ),  # Limit size
                processed_data=processed_data,
            )

            self.db.add(filing)
            self.db.commit()

            logger.info(f"Saved filing {filing_data['accession_number']}")

        except Exception as e:
            logger.error(
                f"Failed to process filing {filing_data.get('accession_number', 'unknown')}: {e}"
            )
            self.db.rollback()

    async def _extract_filing_text(self, document_url: str) -> str:
        """Extract text content from SEC filing document"""
        if not document_url or not self.enabled:
            return self._generate_mock_filing_text()

        try:
            response = requests.get(document_url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                content_type = response.headers.get("content-type", "").lower()

                if "html" in content_type:
                    # Parse HTML filing
                    soup = BeautifulSoup(response.content, "html.parser")

                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    # Extract text
                    text = soup.get_text()

                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (
                        phrase.strip() for line in lines for phrase in line.split("  ")
                    )
                    text = " ".join(chunk for chunk in chunks if chunk)

                    return text

                elif "pdf" in content_type:
                    # Parse PDF filing (simplified - would need more robust PDF handling)
                    return "PDF content extraction not implemented in MVP"

                else:
                    # Plain text or other format
                    return response.text

            else:
                logger.warning(
                    f"Failed to fetch filing content: {response.status_code}"
                )
                return ""

        except Exception as e:
            logger.error(f"Failed to extract filing text: {e}")
            return ""

    def _generate_mock_filing_text(self) -> str:
        """Generate mock filing text content"""
        return """
        FORM 10-K
        UNITED STATES SECURITIES AND EXCHANGE COMMISSION
        Washington, D.C. 20549
        
        ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934
        
        For the fiscal year ended December 31, 2023
        
        BUSINESS OVERVIEW
        
        The Company operates in the technology sector, providing innovative solutions to enterprise customers.
        During the fiscal year 2023, the Company achieved record revenues and expanded its market presence.
        
        RISK FACTORS
        
        The Company faces various risks including market competition, regulatory changes, and economic uncertainty.
        These factors could materially affect the Company's business, financial condition, and results of operations.
        
        FINANCIAL STATEMENTS
        
        [Mock financial data would be included here in a real filing]
        
        This is a mock SEC filing generated for testing purposes only.
        """

    async def _process_filing_content(
        self, filing_data: Dict[str, Any], text_content: str
    ) -> Dict[str, Any]:
        """Process and structure filing content for analysis"""
        try:
            processed_data = {
                "filing_type": filing_data["filing_type"],
                "company_name": filing_data.get("company_name"),
                "cik": filing_data.get("cik"),
                "word_count": len(text_content.split()) if text_content else 0,
                "sections_identified": [],
                "key_topics": [],
                "risk_factors_mentioned": False,
                "financial_data_present": False,
            }

            if text_content:
                text_lower = text_content.lower()

                # Identify common sections
                sections = [
                    "business",
                    "risk factors",
                    "financial statements",
                    "management discussion",
                    "controls and procedures",
                ]

                for section in sections:
                    if section in text_lower:
                        processed_data["sections_identified"].append(section)

                # Check for risk factors
                risk_keywords = [
                    "risk",
                    "uncertainty",
                    "competition",
                    "regulatory",
                    "market volatility",
                ]
                if any(keyword in text_lower for keyword in risk_keywords):
                    processed_data["risk_factors_mentioned"] = True

                # Check for financial data
                financial_keywords = [
                    "revenue",
                    "earnings",
                    "profit",
                    "cash flow",
                    "balance sheet",
                ]
                if any(keyword in text_lower for keyword in financial_keywords):
                    processed_data["financial_data_present"] = True

                # Extract key topics (simplified)
                if "acquisition" in text_lower or "merger" in text_lower:
                    processed_data["key_topics"].append("M&A Activity")

                if "investigation" in text_lower or "lawsuit" in text_lower:
                    processed_data["key_topics"].append("Legal Issues")

                if "restructuring" in text_lower or "layoffs" in text_lower:
                    processed_data["key_topics"].append("Corporate Restructuring")

            return processed_data

        except Exception as e:
            logger.error(f"Failed to process filing content: {e}")
            return {"error": str(e)}

    def close(self):
        """Close database connection"""
        self.db.close()


async def main():
    """Main function to run SEC filings ingestion"""
    logger.info("Starting SEC filings ingestion...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    ingester = SecFilingIngester()

    try:
        # Ingest recent filings (last 7 days)
        await ingester.ingest_recent_filings(days=7)

        logger.info("SEC filings ingestion completed successfully")

    except Exception as e:
        logger.error(f"SEC filings ingestion failed: {e}")
    finally:
        ingester.close()


if __name__ == "__main__":
    asyncio.run(main())
