# Shadow SEC: Open-Source Financial Watchdog

**Mission:** To empower the public by providing transparent, AI-driven market surveillance.

[![CI/CD Pipeline](https://github.com/rajiv-rathod/Shadow-SEC/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/rajiv-rathod/Shadow-SEC/actions/workflows/ci-cd.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)

## 🎯 Project Overview

Shadow SEC is a **community-driven, open-source financial watchdog** that uses multi-modal AI to analyze market data, SEC filings, and news to identify potential correlations and market anomalies. Built with transparency and accountability at its core, all code, models, and methodologies are publicly accessible.

### Key Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini API for correlation analysis
- 📊 **Real-Time Data**: Ingests market data, SEC filings, and financial news
- 🔍 **Transparent Methodology**: All analysis methods are open-source
- ⚡ **Interactive Timeline**: Visual timeline of market events with AI analysis
- 🔒 **Privacy-Focused**: No personal data collection, anonymous feedback
- 📱 **Modern Interface**: React-based responsive web application
- 🐳 **Containerized**: Docker support for easy deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rajiv-rathod/Shadow-SEC.git
   cd Shadow-SEC
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Copy environment template
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb shadow_sec_db
   
   # Run database migrations (tables will be created automatically on first run)
   ```

### API Keys Configuration

Add the following API keys to your `.env` file:

```env
# Required for AI analysis
GEMINI_API_KEY=your_gemini_api_key_here

# Required for market data
FINNHUB_API_KEY=your_finnhub_api_key_here

# Required for SEC filings
SEC_API_KEY=your_sec_api_key_here

# Optional: For additional market data
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
```

### Running the Application

1. **Start the backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend**
   ```bash
   cd frontend
   npm start
   ```

3. **Run data ingestion** (optional)
   ```bash
   python data_ingestion/ingest_market_data.py
   python data_ingestion/ingest_sec_filings.py
   python data_ingestion/ingest_news_data.py
   ```

Visit `http://localhost:3000` to access the application.

### Docker Deployment

```bash
docker build -t shadow-sec .
docker run -p 8000:8000 shadow-sec
```

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with time-series optimization
- **Cache**: Redis for session management and job queuing
- **Frontend**: React 18 with Material-UI
- **AI**: Google Gemini API for correlation analysis
- **Data Sources**: Finnhub (market data), SEC API (filings), RSS feeds (news)

### Project Structure

```
shadow-sec/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── routers/        # API route handlers
│   │   ├── models/         # Pydantic models for validation
│   │   ├── schemas/        # Database models
│   │   ├── services/       # Business logic services
│   │   └── core/           # Configuration and utilities
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API communication
│   │   └── utils/          # Utility functions
│   └── package.json        # Node.js dependencies
├── data_ingestion/         # Data ingestion scripts
│   ├── ingest_market_data.py
│   ├── ingest_sec_filings.py
│   └── ingest_news_data.py
├── .github/                # GitHub Actions workflows
└── docs/                   # Documentation
```

## 📊 Tracked Stocks (MVP)

The MVP tracks the following 10 major US stocks:

- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **GOOGL** - Alphabet Inc.
- **AMZN** - Amazon.com Inc.
- **TSLA** - Tesla Inc.
- **META** - Meta Platforms Inc.
- **NVDA** - NVIDIA Corporation
- **BRK.B** - Berkshire Hathaway Inc.
- **JNJ** - Johnson & Johnson
- **V** - Visa Inc.

## 🔬 AI Analysis Features

### Correlation Analysis

The AI system analyzes:

1. **Temporal Correlations**: Time-based relationships between events
2. **Volume Correlations**: Trading volume changes vs. news/filings
3. **Sentiment Correlations**: News sentiment vs. price movements
4. **Filing Impact**: SEC filing timing vs. market reactions

### Analysis Process

1. **Data Gathering**: Collect market data, SEC filings, and news
2. **Preprocessing**: Clean and structure data for AI analysis
3. **AI Generation**: Use Gemini API for correlation identification
4. **Confidence Scoring**: Provide confidence levels for findings
5. **Disclaimer Addition**: Automatic legal disclaimers on all reports

## 🔒 Privacy & Security

### Data Privacy

- **No Personal Data**: Zero collection of user personal information
- **Anonymous Feedback**: User feedback uses random, anonymous IDs
- **Public Data Only**: All analysis uses publicly available data sources
- **Transparent Logging**: All system actions are logged for auditability

### Security Measures

- **API Key Security**: Environment variable management for sensitive keys
- **Input Validation**: Comprehensive validation of all user inputs
- **Rate Limiting**: API rate limiting to prevent abuse
- **Error Handling**: Secure error handling without information leakage

## ⚖️ Legal Compliance

### Important Disclaimers

**⚠️ NOT FINANCIAL ADVICE**: All reports and analysis are for educational purposes only. This is not financial advice. Always consult qualified financial advisors.

**⚠️ CORRELATION ≠ CAUSATION**: Identified correlations do not imply causal relationships.

**⚠️ AI LIMITATIONS**: All analysis is AI-generated and may contain errors or biases.

### Regulatory Compliance

- Full disclosure of AI-generated content
- Mandatory disclaimers on all reports
- Public methodology and source code
- No investment recommendations provided
- Educational and transparency focus

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md).

### Ways to Contribute

- 🐛 **Bug Reports**: Report issues via GitHub Issues
- 💡 **Feature Requests**: Suggest improvements
- 📝 **Documentation**: Improve documentation
- 🧪 **Testing**: Help with testing and quality assurance
- 🔍 **Code Review**: Review pull requests
- 📊 **Data Sources**: Suggest new data sources

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📈 Roadmap

### Phase 1: MVP (Current)
- [x] Basic architecture setup
- [x] 10-stock tracking system
- [x] AI correlation analysis
- [x] Interactive timeline
- [x] Basic data ingestion

### Phase 2: Enhanced Analysis
- [ ] Advanced correlation algorithms
- [ ] Social media sentiment integration
- [ ] Real-time alert system
- [ ] Community peer review system
- [ ] Mobile-responsive improvements

### Phase 3: Scale & Governance
- [ ] Extended stock coverage (S&P 500)
- [ ] DAO governance implementation
- [ ] Reputation-based contribution system
- [ ] Advanced visualization tools
- [ ] API for third-party developers

### Phase 4: Advanced Features
- [ ] Machine learning model training
- [ ] Predictive analysis capabilities
- [ ] Multi-language support
- [ ] Integration with more data sources
- [ ] Professional institutional tools

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check our [docs](docs/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/rajiv-rathod/Shadow-SEC/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/rajiv-rathod/Shadow-SEC/discussions)
- 📧 **Contact**: [Open an issue](https://github.com/rajiv-rathod/Shadow-SEC/issues/new) for questions

## 🙏 Acknowledgments

- Google Gemini AI for correlation analysis capabilities
- Finnhub for real-time market data
- SEC.gov for regulatory filing access
- Open-source community for tools and libraries
- Contributors and testers who help improve the project

---

**Remember**: Shadow SEC is an educational and transparency tool. Always conduct your own research and consult with qualified financial advisors before making investment decisions.
