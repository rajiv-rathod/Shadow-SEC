"""
News data ingestion script for Shadow SEC
Fetches financial news from various sources and processes sentiment
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

import feedparser
import requests
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, engine
from backend.app.schemas.models import Base, NewsArticle

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NewsIngester:
    """News data ingestion service"""

    def __init__(self):
        """Initialize the news ingester"""
        self.db = SessionLocal()

        # News sources configuration
        self.news_sources = {
            "reuters_business": "http://feeds.reuters.com/reuters/businessNews",
            "reuters_markets": "http://feeds.reuters.com/reuters/marketsNews",
            "yahoo_finance": "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "marketwatch": "http://feeds.marketwatch.com/marketwatch/marketpulse/",
            "seeking_alpha": "https://seekingalpha.com/rss/all_articles.xml",
        }

        self.headers = {"User-Agent": "Shadow-SEC/1.0 (opensource-financial-watchdog)"}

        logger.info("News ingester initialized")

    async def ingest_recent_news(self, hours: int = 24):
        """Ingest recent news articles from all sources"""
        try:
            all_articles = []

            for source_name, feed_url in self.news_sources.items():
                try:
                    articles = await self._fetch_news_from_source(
                        source_name, feed_url, hours
                    )
                    all_articles.extend(articles)

                    logger.info(f"Fetched {len(articles)} articles from {source_name}")

                    # Rate limiting between sources
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Failed to fetch from {source_name}: {e}")
                    continue

            # Process and save articles
            saved_count = 0
            for article_data in all_articles:
                try:
                    if await self._process_and_save_article(article_data):
                        saved_count += 1
                except Exception as e:
                    logger.error(f"Failed to save article: {e}")
                    continue

            logger.info(f"News ingestion completed: {saved_count} articles saved")

        except Exception as e:
            logger.error(f"Failed to ingest news: {e}")

    async def _fetch_news_from_source(
        self, source_name: str, feed_url: str, hours: int
    ) -> List[Dict[str, Any]]:
        """Fetch news articles from a RSS feed source"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"RSS feed parsing issues for {source_name}")

            articles = []
            cutoff_time = datetime.now() - timedelta(hours=hours)

            for entry in feed.entries:
                try:
                    # Parse publication date
                    published_at = self._parse_publish_date(entry)

                    # Skip old articles
                    if published_at and published_at < cutoff_time:
                        continue

                    # Extract article data
                    article_data = {
                        "title": entry.get("title", "").strip(),
                        "url": entry.get("link", ""),
                        "source": source_name,
                        "author": entry.get("author", ""),
                        "published_at": published_at or datetime.now(),
                        "summary": entry.get("summary", ""),
                        "content": (
                            entry.get("content", [{}])[0].get("value", "")
                            if entry.get("content")
                            else ""
                        ),
                    }

                    # Extract full content if not available in feed
                    if not article_data["content"] and article_data["url"]:
                        article_data["content"] = await self._extract_article_content(
                            article_data["url"]
                        )

                    articles.append(article_data)

                except Exception as e:
                    logger.error(f"Error processing article from {source_name}: {e}")
                    continue

            return articles

        except Exception as e:
            logger.error(f"Failed to fetch from {source_name}: {e}")
            return []

    def _parse_publish_date(self, entry) -> datetime:
        """Parse publication date from RSS entry"""
        try:
            # Try different date fields
            date_fields = ["published_parsed", "updated_parsed"]

            for field in date_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6])

            # Try string parsing
            date_strings = [entry.get("published", ""), entry.get("updated", "")]

            for date_str in date_strings:
                if date_str:
                    try:
                        import dateutil.parser

                        return dateutil.parser.parse(date_str)
                    except Exception:
                        continue

            return None

        except Exception as e:
            logger.error(f"Failed to parse date: {e}")
            return None

    async def _extract_article_content(self, url: str) -> str:
        """Extract full article content from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "aside"]):
                    script.decompose()

                # Try to find article content
                content_selectors = [
                    "article",
                    ".article-content",
                    ".story-content",
                    ".post-content",
                    ".entry-content",
                    "main",
                ]

                content = ""
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(strip=True)
                        break

                if not content:
                    # Fallback: get all paragraph text
                    paragraphs = soup.find_all("p")
                    content = " ".join([p.get_text(strip=True) for p in paragraphs])

                return content[:5000]  # Limit content length

            return ""

        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return ""

    async def _process_and_save_article(self, article_data: Dict[str, Any]) -> bool:
        """Process article data and save to database"""
        try:
            # Check if article already exists
            existing_article = (
                self.db.query(NewsArticle)
                .filter(NewsArticle.url == article_data["url"])
                .first()
            )

            if existing_article:
                logger.debug(f"Article already exists: {article_data['title'][:50]}")
                return False

            # Analyze content for stock mentions and sentiment
            analysis = await self._analyze_article_content(article_data)

            # Create article record
            article = NewsArticle(
                title=article_data["title"][:500],  # Ensure title fits in database
                content=article_data.get("content") or article_data.get("summary"),
                url=article_data["url"],
                source=article_data["source"],
                author=article_data.get("author"),
                published_at=article_data["published_at"],
                sentiment_score=analysis.get("sentiment_score"),
                relevance_score=analysis.get("relevance_score"),
                mentioned_stocks=analysis.get("mentioned_stocks", []),
            )

            self.db.add(article)
            self.db.commit()

            logger.debug(f"Saved article: {article_data['title'][:50]}")
            return True

        except Exception as e:
            logger.error(f"Failed to save article: {e}")
            self.db.rollback()
            return False

    async def _analyze_article_content(
        self, article_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze article content for sentiment and stock mentions"""
        try:
            content = (
                article_data.get("content", "") + " " + article_data.get("summary", "")
            )
            title = article_data.get("title", "")
            full_text = (title + " " + content).lower()

            analysis = {
                "sentiment_score": 0.0,
                "relevance_score": 0.0,
                "mentioned_stocks": [],
            }

            # Check for mentions of tracked stocks
            mentioned_stocks = []
            for stock_symbol in settings.TRACKED_STOCKS:
                # Look for stock symbol mentions
                if stock_symbol.lower() in full_text:
                    mentioned_stocks.append(stock_symbol)

                # Also check for company name patterns (simplified)
                company_patterns = {
                    "AAPL": ["apple", "iphone", "mac", "ipad"],
                    "MSFT": ["microsoft", "windows", "azure", "office"],
                    "GOOGL": ["google", "alphabet", "youtube", "android"],
                    "AMZN": ["amazon", "aws", "prime", "alexa"],
                    "TSLA": ["tesla", "elon musk", "electric vehicle"],
                    "META": ["meta", "facebook", "instagram", "whatsapp"],
                    "NVDA": ["nvidia", "gpu", "chip", "semiconductor"],
                    "V": ["visa", "payment"],
                    "JNJ": ["johnson", "pharmaceutical"],
                }

                patterns = company_patterns.get(stock_symbol, [])
                for pattern in patterns:
                    if pattern in full_text:
                        if stock_symbol not in mentioned_stocks:
                            mentioned_stocks.append(stock_symbol)
                        break

            analysis["mentioned_stocks"] = mentioned_stocks

            # Calculate relevance score based on stock mentions
            if mentioned_stocks:
                analysis["relevance_score"] = min(len(mentioned_stocks) * 0.3, 1.0)

            # Simple sentiment analysis
            analysis["sentiment_score"] = self._calculate_sentiment(full_text)

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze article content: {e}")
            return {
                "sentiment_score": 0.0,
                "relevance_score": 0.0,
                "mentioned_stocks": [],
            }

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate simple sentiment score for text"""
        try:
            # Simple keyword-based sentiment analysis
            positive_words = [
                "growth",
                "profit",
                "gain",
                "increase",
                "strong",
                "positive",
                "success",
                "beat",
                "exceed",
                "bullish",
                "upgrade",
                "buy",
            ]

            negative_words = [
                "loss",
                "decline",
                "decrease",
                "weak",
                "negative",
                "fail",
                "miss",
                "bearish",
                "downgrade",
                "sell",
                "risk",
                "concern",
            ]

            words = text.lower().split()

            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)

            total_sentiment_words = positive_count + negative_count

            if total_sentiment_words == 0:
                return 0.0

            # Calculate sentiment score (-1 to 1)
            sentiment_score = (positive_count - negative_count) / total_sentiment_words

            # Normalize to [-1, 1] range
            return max(-1.0, min(1.0, sentiment_score))

        except Exception as e:
            logger.error(f"Failed to calculate sentiment: {e}")
            return 0.0

    async def generate_mock_news(self, count: int = 10):
        """Generate mock news articles for testing"""
        try:
            import random

            mock_titles = [
                "{} Reports Strong Q4 Earnings, Beats Expectations",
                "{} Announces New Product Launch, Stock Rises",
                "{} Faces Regulatory Scrutiny Over Market Practices",
                "{} CEO Steps Down Amid Company Restructuring",
                "{} Invests $1B in AI Technology Development",
                "Analysts Upgrade {} Rating on Positive Outlook",
                "{} Stock Volatile Following Mixed Earnings Report",
                "{} Partners with Major Tech Company for Innovation",
                "{} Reports Disappointing Revenue, Shares Fall",
                "Market Rally Boosts {} and Other Tech Stocks",
            ]

            sources = ["reuters_business", "yahoo_finance", "marketwatch"]

            for i in range(count):
                stock_symbol = random.choice(settings.TRACKED_STOCKS)
                title_template = random.choice(mock_titles)
                title = title_template.format(stock_symbol)

                # Generate mock content
                content = f"""
                {title}
                
                In a recent development, {stock_symbol} has shown significant movement in the market.
                The company's latest financial results have drawn attention from analysts and investors alike.
                
                Market analysts are closely watching the stock for further developments.
                The company's management has expressed confidence in their strategic direction.
                
                This article is generated for testing purposes and contains mock financial data.
                """

                article_data = {
                    "title": title,
                    "content": content,
                    "url": f"https://mock-news.com/article-{i}",
                    "source": random.choice(sources),
                    "author": "Mock Reporter",
                    "published_at": datetime.now()
                    - timedelta(hours=random.randint(1, 48)),
                }

                await self._process_and_save_article(article_data)

            logger.info(f"Generated {count} mock news articles")

        except Exception as e:
            logger.error(f"Failed to generate mock news: {e}")

    def close(self):
        """Close database connection"""
        self.db.close()


async def main():
    """Main function to run news ingestion"""
    logger.info("Starting news data ingestion...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    ingester = NewsIngester()

    try:
        # Ingest recent news (last 24 hours)
        await ingester.ingest_recent_news(hours=24)

        # Generate some mock news for testing
        await ingester.generate_mock_news(count=5)

        logger.info("News data ingestion completed successfully")

    except Exception as e:
        logger.error(f"News data ingestion failed: {e}")
    finally:
        ingester.close()


if __name__ == "__main__":
    asyncio.run(main())
