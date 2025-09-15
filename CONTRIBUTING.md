# Contributing to Shadow SEC

Thank you for your interest in contributing to Shadow SEC! This document provides guidelines and information for contributors.

## 🎯 Project Mission

Shadow SEC is an open-source financial watchdog that provides transparent, AI-driven market surveillance. We're building a community-driven platform that empowers the public with unbiased financial market analysis.

## 🤝 Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory language
- Public or private harassment
- Publishing others' private information without permission
- Any conduct that could reasonably be considered inappropriate

## 🚀 Getting Started

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Shadow-SEC.git
   cd Shadow-SEC
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Configure your .env file
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup**
   ```bash
   # Install PostgreSQL and create database
   createdb shadow_sec_dev
   ```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests  
cd frontend
npm test

# Linting
flake8 backend/ data_ingestion/
cd frontend && npm run lint
```

## 📋 How to Contribute

### 1. Issues and Bug Reports

- Check existing issues before creating new ones
- Use the provided issue templates
- Include detailed reproduction steps
- Provide system information and logs when relevant

### 2. Feature Requests

- Describe the problem you're trying to solve
- Explain how the feature aligns with project goals
- Consider implementation complexity and maintenance burden
- Discuss with maintainers before starting large features

### 3. Code Contributions

#### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

#### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   cd backend && python -m pytest
   cd frontend && npm test
   
   # Check linting
   flake8 backend/ data_ingestion/
   cd frontend && npm run lint
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature
   
   - Implement feature X
   - Add tests for feature X
   - Update documentation"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/amazing-feature
   ```

#### Pull Request Requirements

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch
- [ ] Security implications considered
- [ ] Legal compliance maintained (disclaimers, etc.)

## 💻 Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8
- **Formatting**: Use `black` for code formatting
- **Imports**: Use `isort` for import sorting
- **Linting**: Use `flake8` for linting
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

```python
def analyze_correlation(
    market_data: List[Dict[str, Any]], 
    sec_filings: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Analyze correlations between market data and SEC filings.
    
    Args:
        market_data: List of market data points
        sec_filings: List of SEC filing data
        
    Returns:
        Dictionary containing correlation scores
        
    Raises:
        ValueError: If input data is invalid
    """
    pass
```

### JavaScript/React (Frontend)

- **Style**: Use ESLint configuration
- **Formatting**: Use Prettier for formatting
- **Components**: Use functional components with hooks
- **Naming**: Use PascalCase for components, camelCase for functions/variables
- **Props**: Use PropTypes or TypeScript for prop validation

```javascript
const CorrelationChart = ({ data, onAnalyze }) => {
  const [loading, setLoading] = useState(false);
  
  const handleAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      await onAnalyze(data);
    } finally {
      setLoading(false);
    }
  }, [data, onAnalyze]);
  
  return (
    <Chart data={data} loading={loading} onAnalyze={handleAnalysis} />
  );
};
```

### Database

- **Migrations**: Use Alembic for database migrations
- **Naming**: Use snake_case for table and column names
- **Indexes**: Add appropriate indexes for query performance
- **Constraints**: Use proper foreign key constraints

## 🔒 Security Guidelines

### API Keys and Secrets

- Never commit API keys or secrets to the repository
- Use environment variables for sensitive configuration
- Rotate keys regularly
- Use minimal required permissions

### Input Validation

- Validate all user inputs
- Sanitize data before database operations
- Use parameterized queries to prevent SQL injection
- Implement rate limiting for API endpoints

### Data Privacy

- No collection of personal user data
- Anonymous feedback mechanisms only
- Transparent data handling practices
- Compliance with relevant privacy regulations

## 📊 Data Sources and AI

### Adding New Data Sources

When contributing new data sources:

1. **Legal Compliance**: Ensure data source allows programmatic access
2. **Rate Limiting**: Implement appropriate rate limiting
3. **Error Handling**: Robust error handling and fallbacks
4. **Documentation**: Document data source integration
5. **Testing**: Include tests with mock data

### AI Model Integration

For AI-related contributions:

1. **Transparency**: Document model behavior and limitations
2. **Bias Considerations**: Consider potential biases in training data
3. **Disclaimers**: Ensure appropriate disclaimers are included
4. **Confidence Scores**: Provide confidence/uncertainty measures
5. **Reproducibility**: Make analysis reproducible where possible

## 🧪 Testing Guidelines

### Backend Testing

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database interactions
- **Mock External APIs**: Use mocks for external API calls
- **Test Coverage**: Aim for >80% test coverage

```python
import pytest
from unittest.mock import patch
from app.services.ai_service import AIService

class TestAIService:
    @patch('google.generativeai.GenerativeModel')
    def test_generate_report(self, mock_model):
        # Setup mock
        mock_model.return_value.generate_content.return_value.text = "Mock report"
        
        # Test
        service = AIService()
        result = service.generate_correlation_report({})
        
        # Assert
        assert "Mock report" in result["content"]
```

### Frontend Testing

- **Component Tests**: Test React component behavior
- **User Interaction Tests**: Test user flows
- **API Integration Tests**: Test API communication
- **Accessibility Tests**: Ensure accessibility compliance

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import ReportDialog from '../components/ReportDialog';

test('generates report when analysis is started', async () => {
  const mockEvent = { title: 'Test Event', stockSymbols: ['AAPL'] };
  
  render(<ReportDialog open={true} event={mockEvent} />);
  
  const startButton = screen.getByText('Start Analysis');
  fireEvent.click(startButton);
  
  expect(screen.getByText('AI Analysis in Progress')).toBeInTheDocument();
});
```

## 📚 Documentation

### Code Documentation

- **README Updates**: Update README for significant changes
- **API Documentation**: Document all API endpoints
- **Code Comments**: Comment complex business logic
- **Architecture Decisions**: Document significant architectural choices

### User Documentation

- **Setup Guides**: Clear installation and setup instructions
- **Usage Examples**: Provide usage examples and tutorials
- **Troubleshooting**: Common issues and solutions
- **FAQ**: Frequently asked questions

## 🔄 Release Process

### Version Numbering

We use Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version numbers bumped
- [ ] Security review completed
- [ ] Performance impact assessed

## 🏆 Recognition

Contributors will be recognized in:
- README acknowledgments
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Future DAO reputation system (planned)

## 📞 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check existing documentation first
- **Code Review**: Request review from maintainers

## 🎖️ Contribution Types

We value all types of contributions:

- **Code**: New features, bug fixes, performance improvements
- **Documentation**: Guides, tutorials, API documentation
- **Testing**: Test cases, bug reports, quality assurance
- **Design**: UI/UX improvements, accessibility enhancements
- **Community**: Answering questions, helping other contributors
- **Data**: New data sources, data quality improvements
- **Security**: Security audits, vulnerability reports

## 📜 Legal Considerations

### Intellectual Property

- Your contributions will be licensed under GPL v3.0
- Ensure you have rights to contribute any code/content
- Do not include proprietary or copyrighted material without permission

### Financial Disclaimers

When contributing to analysis features:
- Include appropriate disclaimers about AI-generated content
- Emphasize educational purpose, not financial advice
- Maintain neutral, factual tone in all analysis

## 🚀 Future Contribution Opportunities

Areas where we especially welcome contributions:

1. **AI Model Improvements**: Better correlation algorithms
2. **Data Quality**: Enhanced data validation and cleaning
3. **Performance**: Optimization of backend and frontend
4. **Accessibility**: Making the platform more accessible
5. **Mobile Support**: Mobile-responsive improvements
6. **Internationalization**: Multi-language support
7. **Security**: Security audits and improvements
8. **Documentation**: User guides and developer documentation

Thank you for contributing to Shadow SEC! Together, we're building a more transparent and accountable financial system. 🚀