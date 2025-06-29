# Contributing to Options Screener

Thank you for your interest in contributing to Options Screener! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Interactive Brokers account (for testing)
- Git for version control

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/yourusername/options_screener.git
   cd options_screener
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Install development dependencies**
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Keep docstrings concise and informative
- Use meaningful variable and function names

**Format your code:**
```bash
black *.py  # Auto-format code
flake8 *.py  # Check style issues
mypy *.py   # Type checking
```

### Testing

- Write tests for new functionality
- Ensure existing tests pass
- Test with different market conditions (open, closed, extended hours)

**Run tests:**
```bash
pytest                    # Run all tests
pytest -v                # Verbose output
pytest --cov=.           # With coverage report
```

### Commit Messages

Use clear, descriptive commit messages:
```
feat: add call options screening support
fix: handle market data timeout errors
docs: update API reference for new methods
refactor: optimize option chain filtering
test: add tests for extended hours trading
```

## Contributing Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Follow the existing code style

### 3. Test Your Changes

```bash
# Run tests
pytest

# Check code style
black *.py
flake8 *.py

# Test the application
python put_option_test.py --help
python put_option_test.py AAPL --benchmark
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: your descriptive commit message"
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Provide a clear description of your changes
4. Reference any related issues

## Types of Contributions

### Bug Reports

When reporting bugs, include:
- Steps to reproduce the issue
- Expected vs actual behavior
- Python version and OS
- IBKR connection details (without credentials)
- Error messages and stack traces

### Feature Requests

For new features, provide:
- Clear description of the feature
- Use case and benefits
- Proposed implementation approach
- Compatibility considerations

### Code Contributions

We welcome contributions for:

**New Strategy Types**
- Call options screening
- Options spreads (iron condor, butterfly, etc.)
- Portfolio optimization

**Performance Improvements**
- Faster data retrieval methods
- Better caching strategies
- Algorithm optimizations

**Enhanced Features**
- Additional Greeks calculations
- Risk management tools
- Real-time monitoring
- Alternative data sources

**Quality Improvements**
- Better error handling
- More comprehensive tests
- Documentation improvements
- Code refactoring

## Architecture Guidelines

### Extending the Base Class

When adding new option strategies, extend `OptionsScreener`:

```python
from options_base import OptionsScreener

class CallScreener(OptionsScreener):
    def screen_calls(self, ticker: str, target_dte: int, max_delta: float):
        """Screen call options based on delta criteria."""
        # Implementation here
        pass
```

### Adding New Methods

- Keep methods focused and single-purpose
- Use type hints consistently
- Handle errors gracefully
- Log important operations
- Return meaningful data structures

### Performance Considerations

- Minimize API calls to IBKR
- Use parallel processing where appropriate
- Implement intelligent filtering
- Cache results when possible
- Provide progress indicators for long operations

## Review Process

1. **Automated Checks**: All PRs run automated tests
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Changes are tested with real market data
4. **Documentation**: Ensure docs are updated if needed
5. **Merge**: Approved changes are merged to main branch

## Getting Help

- **Issues**: Open an issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Check the README and API docs first

## Code of Conduct

- Be respectful and professional
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different opinions and approaches

## License

By contributing to Options Screener, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🚀 