"""
AI Service for Gemini API integration and report generation
"""

import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered correlation analysis using Gemini API"""
    
    def __init__(self):
        """Initialize the AI service with Gemini API"""
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured - AI features will be disabled")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
            logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI service: {e}")
            self.enabled = False
    
    async def generate_correlation_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a correlation analysis report using Gemini AI
        
        Args:
            data: Dictionary containing market data, SEC filings, and news
            
        Returns:
            Dictionary containing the AI-generated report
        """
        if not self.enabled:
            return self._generate_mock_report(data)
        
        try:
            prompt = self._build_analysis_prompt(data)
            
            # Generate content using Gemini
            response = await self._generate_with_gemini(prompt)
            
            # Parse and structure the response
            structured_response = self._parse_ai_response(response)
            
            logger.info("Successfully generated AI correlation report")
            return structured_response
            
        except Exception as e:
            logger.error(f"Failed to generate AI report: {e}")
            # Fallback to mock report
            return self._generate_mock_report(data)
    
    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build a structured prompt for Gemini analysis
        
        Args:
            data: Analysis data including market, SEC, and news information
            
        Returns:
            Formatted prompt string for AI analysis
        """
        prompt = """
You are an impartial financial analyst for Shadow SEC, an open-source financial watchdog. 
Your role is to analyze market data, SEC filings, and news to identify potential correlations 
and anomalies. You must remain neutral and factual.

IMPORTANT DISCLAIMERS TO INCLUDE:
- This analysis is AI-generated and not financial advice
- Correlations do not imply causation
- All findings should be independently verified
- This is for educational and transparency purposes only

ANALYSIS INSTRUCTIONS:
1. Analyze the provided data for temporal correlations
2. Identify any notable patterns or anomalies
3. Provide confidence scores (0-1) for each finding
4. Present facts only, no speculation or recommendations
5. Include data sources for each correlation

DATA TO ANALYZE:
"""
        
        # Add market data
        if "market_data" in data:
            prompt += f"\nMARKET DATA:\n{self._format_market_data(data['market_data'])}\n"
        
        # Add SEC filings
        if "sec_filings" in data:
            prompt += f"\nSEC FILINGS:\n{self._format_sec_data(data['sec_filings'])}\n"
        
        # Add news data
        if "news" in data:
            prompt += f"\nNEWS DATA:\n{self._format_news_data(data['news'])}\n"
        
        prompt += """
REQUIRED OUTPUT FORMAT:
Please provide your analysis in the following JSON structure:
{
    "title": "Brief descriptive title",
    "summary": "2-3 sentence executive summary",
    "correlations": [
        {
            "description": "What correlation was found",
            "confidence": 0.85,
            "data_sources": ["market_data", "news"],
            "time_correlation": "description of timing",
            "significance": "high|medium|low"
        }
    ],
    "anomalies": [
        {
            "description": "Description of anomaly",
            "severity": "high|medium|low",
            "confidence": 0.75
        }
    ],
    "key_findings": ["bullet point findings"],
    "data_quality": "assessment of data completeness",
    "disclaimers": ["required legal disclaimers"]
}

Remember: Be factual, neutral, and always include appropriate disclaimers.
"""
        
        return prompt
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """
        Generate content using Gemini API with error handling
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse and validate AI response
        """
        try:
            import json
            # Try to extract JSON from the response
            # This is a simplified parser - production would need more robust parsing
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                # Add metadata
                parsed_response["model_version"] = "gemini-pro"
                parsed_response["generated_at"] = "2024-01-01T00:00:00Z"  # Would use actual timestamp
                
                return parsed_response
            else:
                # Fallback if JSON parsing fails
                return {
                    "title": "Analysis Report",
                    "content": response_text,
                    "confidence_score": 0.5,
                    "model_version": "gemini-pro",
                    "correlations": {},
                    "sources": {}
                }
                
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return {
                "title": "Analysis Report",
                "content": response_text,
                "confidence_score": 0.3,
                "model_version": "gemini-pro",
                "error": "Failed to parse structured response"
            }
    
    def _format_market_data(self, market_data: List[Dict]) -> str:
        """Format market data for AI analysis"""
        if not market_data:
            return "No market data available"
        
        formatted = "Recent Price Movements:\n"
        for data_point in market_data[-10:]:  # Last 10 data points
            formatted += f"- {data_point.get('timestamp', 'N/A')}: "
            formatted += f"Close: ${data_point.get('close_price', 'N/A')}, "
            formatted += f"Change: {data_point.get('price_change_percent', 'N/A')}%, "
            formatted += f"Volume: {data_point.get('volume', 'N/A')}\n"
        
        return formatted
    
    def _format_sec_data(self, sec_data: List[Dict]) -> str:
        """Format SEC filing data for AI analysis"""
        if not sec_data:
            return "No SEC filings available"
        
        formatted = "Recent SEC Filings:\n"
        for filing in sec_data[-5:]:  # Last 5 filings
            formatted += f"- {filing.get('filing_type', 'N/A')} "
            formatted += f"filed on {filing.get('filing_date', 'N/A')}\n"
            if filing.get('text_content'):
                # Include first 500 characters of content
                content = filing['text_content'][:500] + "..." if len(filing['text_content']) > 500 else filing['text_content']
                formatted += f"  Content preview: {content}\n"
        
        return formatted
    
    def _format_news_data(self, news_data: List[Dict]) -> str:
        """Format news data for AI analysis"""
        if not news_data:
            return "No news data available"
        
        formatted = "Recent News Articles:\n"
        for article in news_data[-10:]:  # Last 10 articles
            formatted += f"- {article.get('title', 'N/A')} "
            formatted += f"({article.get('source', 'Unknown source')}, "
            formatted += f"{article.get('published_at', 'N/A')})\n"
            if article.get('sentiment_score'):
                formatted += f"  Sentiment: {article['sentiment_score']}\n"
        
        return formatted
    
    def _generate_mock_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a mock report when AI service is not available
        """
        stock_symbol = data.get('stock_symbol', 'UNKNOWN')
        
        return {
            "title": f"Mock Analysis Report for {stock_symbol}",
            "content": f"""
DISCLAIMER: This is a mock report generated when AI services are unavailable.

Analysis Summary for {stock_symbol}:
- Market data points analyzed: {len(data.get('market_data', []))}
- SEC filings reviewed: {len(data.get('sec_filings', []))}
- News articles processed: {len(data.get('news', []))}

This mock report indicates that the system is operational but AI analysis 
is currently unavailable. Please configure the Gemini API key to enable 
full AI-powered correlation analysis.

IMPORTANT: This is not financial advice and should not be used for investment decisions.
            """,
            "confidence_score": 0.1,
            "correlations": {
                "mock_correlation": "Mock correlation data - AI service unavailable"
            },
            "sources": {
                "market_data": len(data.get('market_data', [])),
                "sec_filings": len(data.get('sec_filings', [])),
                "news": len(data.get('news', []))
            },
            "model_version": "mock-service-v1.0"
        }