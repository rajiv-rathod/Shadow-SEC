"""
Market data ingestion script for Shadow SEC
Uses Finnhub API to fetch real-time stock data for tracked symbols
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

import finnhub

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, engine
from backend.app.schemas.models import Base, MarketData, Stock

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarketDataIngester:
    """Market data ingestion service"""

    def __init__(self):
        """Initialize the market data ingester"""
        self.db = SessionLocal()

        # Initialize Finnhub client if API key is available
        if settings.FINNHUB_API_KEY:
            self.finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)
            self.enabled = True
            logger.info("Finnhub client initialized successfully")
        else:
            logger.warning("Finnhub API key not configured - using mock data")
            self.enabled = False

    async def initialize_stocks(self):
        """Initialize tracked stocks in the database"""
        try:
            for symbol in settings.TRACKED_STOCKS:
                existing_stock = (
                    self.db.query(Stock).filter(Stock.symbol == symbol).first()
                )

                if not existing_stock:
                    # Create new stock entry
                    stock_info = await self._get_stock_info(symbol)

                    stock = Stock(
                        symbol=symbol,
                        name=stock_info.get("name", symbol),
                        sector=stock_info.get("sector"),
                        industry=stock_info.get("industry"),
                        market_cap=stock_info.get("market_cap"),
                    )

                    self.db.add(stock)
                    logger.info(f"Added new stock: {symbol}")

            self.db.commit()
            logger.info("Stock initialization completed")

        except Exception as e:
            logger.error(f"Failed to initialize stocks: {e}")
            self.db.rollback()

    async def _get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get stock company information"""
        if not self.enabled:
            return {
                "name": f"{symbol} Company",
                "sector": "Technology",
                "industry": "Software",
            }

        try:
            profile = self.finnhub_client.company_profile2(symbol=symbol)
            return {
                "name": profile.get("name", symbol),
                "sector": profile.get("gics_sector"),
                "industry": profile.get("gics_sub_industry"),
                "market_cap": profile.get("market_capitalization", 0)
                * 1000000,  # Convert to actual value
            }
        except Exception as e:
            logger.error(f"Failed to get stock info for {symbol}: {e}")
            return {"name": f"{symbol} Company"}

    async def ingest_real_time_data(self):
        """Ingest real-time market data for all tracked stocks"""
        try:
            stocks = self.db.query(Stock).all()

            for stock in stocks:
                try:
                    market_data = await self._fetch_market_data(stock.symbol)
                    if market_data:
                        await self._save_market_data(stock.id, market_data)
                        logger.info(f"Ingested market data for {stock.symbol}")

                    # Add small delay to respect rate limits
                    await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"Failed to ingest data for {stock.symbol}: {e}")
                    continue

            logger.info("Real-time data ingestion completed")

        except Exception as e:
            logger.error(f"Failed to ingest real-time data: {e}")

    async def _fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch current market data for a symbol"""
        if not self.enabled:
            return self._generate_mock_data(symbol)

        try:
            # Get current price
            quote = self.finnhub_client.quote(symbol)

            # Get previous close for change calculation
            current_price = quote.get("c", 0)  # Current price
            previous_close = quote.get("pc", 0)  # Previous close
            change = current_price - previous_close
            change_percent = (
                (change / previous_close * 100) if previous_close > 0 else 0
            )

            return {
                "timestamp": datetime.now(),
                "open_price": quote.get("o"),  # Open price
                "high_price": quote.get("h"),  # High price
                "low_price": quote.get("l"),  # Low price
                "close_price": current_price,  # Current price
                "price_change": change,
                "price_change_percent": change_percent,
                "volume": None,  # Volume not available in real-time quote
            }

        except Exception as e:
            logger.error(f"Failed to fetch market data for {symbol}: {e}")
            return None

    def _generate_mock_data(self, symbol: str) -> Dict[str, Any]:
        """Generate mock market data when API is not available"""
        import random

        base_price = 100 + random.uniform(-50, 200)  # Random base price
        change_percent = random.uniform(-5, 5)  # Random change ±5%
        change = base_price * (change_percent / 100)

        return {
            "timestamp": datetime.now(),
            "open_price": round(base_price - random.uniform(-2, 2), 2),
            "high_price": round(base_price + random.uniform(0, 3), 2),
            "low_price": round(base_price - random.uniform(0, 3), 2),
            "close_price": round(base_price, 2),
            "price_change": round(change, 2),
            "price_change_percent": round(change_percent, 2),
            "volume": random.randint(1000000, 50000000),
        }

    async def _save_market_data(self, stock_id: int, data: Dict[str, Any]):
        """Save market data to database"""
        try:
            market_data = MarketData(
                stock_id=stock_id,
                timestamp=data["timestamp"],
                open_price=data.get("open_price"),
                high_price=data.get("high_price"),
                low_price=data.get("low_price"),
                close_price=data.get("close_price"),
                volume=data.get("volume"),
                price_change=data.get("price_change"),
                price_change_percent=data.get("price_change_percent"),
            )

            self.db.add(market_data)
            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to save market data: {e}")
            self.db.rollback()

    async def ingest_historical_data(self, days: int = 30):
        """Ingest historical market data for all tracked stocks"""
        try:
            stocks = self.db.query(Stock).all()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            for stock in stocks:
                try:
                    historical_data = await self._fetch_historical_data(
                        stock.symbol, start_date, end_date
                    )

                    for data_point in historical_data:
                        await self._save_market_data(stock.id, data_point)

                    logger.info(
                        f"Ingested {len(historical_data)} historical data points for {stock.symbol}"
                    )

                    # Add delay to respect rate limits
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(
                        f"Failed to ingest historical data for {stock.symbol}: {e}"
                    )
                    continue

            logger.info("Historical data ingestion completed")

        except Exception as e:
            logger.error(f"Failed to ingest historical data: {e}")

    async def _fetch_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch historical market data"""
        if not self.enabled:
            return self._generate_mock_historical_data(symbol, start_date, end_date)

        try:
            # Convert to Unix timestamps
            from_ts = int(start_date.timestamp())
            to_ts = int(end_date.timestamp())

            # Get stock candles (OHLCV data)
            candles = self.finnhub_client.stock_candles(symbol, "D", from_ts, to_ts)

            if candles["s"] != "ok":
                logger.warning(f"No historical data available for {symbol}")
                return []

            historical_data = []
            for i in range(len(candles["t"])):
                timestamp = datetime.fromtimestamp(candles["t"][i])
                open_price = candles["o"][i]
                high_price = candles["h"][i]
                low_price = candles["l"][i]
                close_price = candles["c"][i]
                volume = candles["v"][i]

                # Calculate price change (compared to previous close)
                price_change = 0
                price_change_percent = 0
                if i > 0:
                    previous_close = candles["c"][i - 1]
                    price_change = close_price - previous_close
                    price_change_percent = (
                        (price_change / previous_close * 100)
                        if previous_close > 0
                        else 0
                    )

                historical_data.append(
                    {
                        "timestamp": timestamp,
                        "open_price": open_price,
                        "high_price": high_price,
                        "low_price": low_price,
                        "close_price": close_price,
                        "volume": volume,
                        "price_change": price_change,
                        "price_change_percent": price_change_percent,
                    }
                )

            return historical_data

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            return []

    def _generate_mock_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate mock historical data"""
        import random

        historical_data = []
        current_date = start_date
        base_price = 100 + random.uniform(-50, 200)

        while current_date <= end_date:
            # Simulate price movement
            daily_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            base_price *= 1 + daily_change

            open_price = base_price + random.uniform(-2, 2)
            high_price = max(open_price, base_price + random.uniform(0, 3))
            low_price = min(open_price, base_price - random.uniform(0, 3))
            close_price = base_price

            historical_data.append(
                {
                    "timestamp": current_date,
                    "open_price": round(open_price, 2),
                    "high_price": round(high_price, 2),
                    "low_price": round(low_price, 2),
                    "close_price": round(close_price, 2),
                    "volume": random.randint(1000000, 50000000),
                    "price_change": round(close_price - open_price, 2),
                    "price_change_percent": round(
                        (close_price - open_price) / open_price * 100, 2
                    ),
                }
            )

            current_date += timedelta(days=1)

        return historical_data

    def close(self):
        """Close database connection"""
        self.db.close()


async def main():
    """Main function to run market data ingestion"""
    logger.info("Starting market data ingestion...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    ingester = MarketDataIngester()

    try:
        # Initialize stocks
        await ingester.initialize_stocks()

        # Ingest historical data (last 30 days)
        await ingester.ingest_historical_data(days=30)

        # Ingest current real-time data
        await ingester.ingest_real_time_data()

        logger.info("Market data ingestion completed successfully")

    except Exception as e:
        logger.error(f"Market data ingestion failed: {e}")
    finally:
        ingester.close()


if __name__ == "__main__":
    asyncio.run(main())
