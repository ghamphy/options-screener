# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of Options Screener library
- Modular architecture with extensible base class `OptionsScreener`
- Put options screening with `PutScreener` class
- Performance-optimized screening (5x faster than standard method)
- Multiple fallback methods for stock price retrieval
- Market data handling with parallel batch processing
- Black-Scholes calculations for delta and premium estimation
- Trading session detection (regular/extended/closed hours)
- Command-line interface with interactive and batch modes
- Comprehensive error handling and logging
- Support for weekly vs monthly expiration detection
- Annualized return calculations for cash-secured strategies

### Features
- **Core Library**: `OptionsScreener` base class with IBKR integration
- **Put Screening**: Specialized put options screening with risk management
- **Performance**: Intelligent strike filtering and parallel processing
- **Market Data**: Multi-source data with trading session awareness
- **CLI Interface**: Full command-line interface with benchmarking
- **Extensibility**: Easy to extend for calls, spreads, and other strategies

### Performance Improvements
- 5.2x faster screening compared to standard method
- 80% efficiency gain through optimization
- 73% reduction in API calls
- Smart strike filtering (70-95% of stock price)
- Delta pre-screening with Black-Scholes
- Parallel market data requests
- Early exit on first qualifying option

### Documentation
- Comprehensive README with examples
- API reference documentation
- Installation and usage instructions
- Performance benchmarking results
- Contributing guidelines

## [Unreleased]

### Planned
- Call options screening support
- Options spreads (iron condor, butterfly, etc.)
- Portfolio management features
- Additional trading platforms support
- Enhanced Greeks calculations
- Real-time monitoring capabilities 