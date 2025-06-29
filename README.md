# Options Screener

A modular Python library for screening options using Interactive Brokers API. Specializes in cash-secured put strategies with optimized performance and comprehensive market data handling.

## Features

- **Modular Design**: Extensible base class for different option strategies
- **Put Options Screening**: Find qualifying cash-secured puts based on risk criteria
- **Performance Optimized**: 5x faster screening with intelligent filtering
- **Market Data Handling**: Multiple fallback methods for price/Greeks data
- **Trading Session Aware**: Handles regular hours, extended hours, and market closed
- **Black-Scholes Integration**: Theoretical calculations when live data unavailable

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/options_screener.git
cd options_screener

# Install dependencies
pip install -r requirements.txt
```

### Prerequisites

- Interactive Brokers account with TWS or Gateway running
- API enabled in TWS/Gateway settings
- Python 3.7+

### Basic Usage

```bash
# Interactive mode
python put_option_test.py

# Command line usage
python put_option_test.py AAPL --dte 45 --risk 20

# Fast optimized screening (default)
python put_option_test.py MSFT --dte 30 --risk 15

# Performance benchmark
python put_option_test.py AAPL --benchmark
```

## Library Usage

### Using the Modular Library

```python
from put_screener import PutScreener

# Initialize screener
screener = PutScreener()
screener.connect()

# Screen for puts with <20% assignment risk
result = screener.screen_puts('AAPL', target_dte=45, max_pitm=0.20)

if result:
    print(f"Found: ${result['strike']} Put")
    print(f"Premium: ${result['premium']:.2f}")
    print(f"Assignment Risk: {result['pitm']:.1%}")
    print(f"Annualized Return: {result['annualized_return']:.1f}%")

screener.disconnect()
```

### Extending for Other Strategies

```python
from options_base import OptionsScreener

class CallScreener(OptionsScreener):
    def screen_calls(self, ticker, target_dte, max_delta):
        # Implement call screening logic
        pass

class SpreadScreener(OptionsScreener):
    def screen_spreads(self, ticker, target_dte, spread_type):
        # Implement spread screening logic
        pass
```

## Project Structure

```
options_screener/
├── options_base.py          # Core IBKR functionality
├── put_screener.py          # Put-specific screening logic
├── put_option_screener.py   # Main application with CLI
├── put_option_test.py       # Simple wrapper (original interface)
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## API Reference

### OptionsScreener (Base Class)

Core functionality for all option screening strategies:

- `connect()` / `disconnect()` - IBKR connection management
- `get_stock_price(ticker)` - Multi-fallback price retrieval
- `get_option_chain(ticker, dte, type)` - Basic option chain
- `get_option_chain_optimized()` - Performance-optimized chain
- `get_option_market_data()` - Single option data
- `get_option_market_data_fast()` - Parallel batch processing
- `estimate_option_delta()` - Black-Scholes delta calculation
- `estimate_option_premium()` - Black-Scholes pricing
- `get_trading_session()` - Session detection
- `calculate_annualized_return()` - Strategy return calculation

### PutScreener

Extends OptionsScreener for put-specific functionality:

- `screen_puts(ticker, dte, max_pitm)` - Main screening method
- `get_best_premium_data()` - Trading-focused data prioritization

## Performance

The optimized screening method provides significant performance improvements:

- **5.2x faster** than standard method
- **80% efficiency gain** 
- **73% fewer API calls**
- Smart strike filtering (70-95% of stock price)
- Delta pre-screening with Black-Scholes
- Parallel market data requests
- Early exit on first qualifying option

## Configuration

### IBKR Connection Settings

Default connection settings:
- Host: `127.0.0.1`
- Port: `4001` (Gateway), `7497` (TWS Paper), `7496` (TWS Live)
- Client ID: `1`

### Command Line Options

```bash
python put_option_test.py [-h] [--dte DTE] [--risk RISK] [--interactive] 
                          [--fast] [--slow] [--benchmark] [ticker]

Options:
  ticker              Stock symbol (e.g., AAPL, MSFT)
  --dte DTE           Days to expiration (default: 45)
  --risk RISK         Max assignment risk % (default: 20.0)
  --interactive, -i   Interactive mode
  --fast              Optimized fast mode (default)
  --slow              Standard slower method
  --benchmark         Performance comparison
```

## Examples

### Find AAPL Puts with Low Risk

```bash
python put_option_test.py AAPL --dte 45 --risk 15
```

Output:
```
🎯 QUALIFYING PUT OPTION FOUND
📊 Current Stock Price:    $201.08
💰 Strike Price:           $185.00
📅 Expiration Date:        2025-08-15
⏰ Days to Expiration:     47 days
📉 Probability ITM (PITM): 14.79%
💵 Premium:                $2.50
📈 Annualized Return:      12.0%
```

### Performance Benchmark

```bash
python put_option_test.py AAPL --benchmark
```

Output:
```
🐌 Standard Method Time:   17.3s
⚡ Optimized Method Time:  3.3s
🚀 Speed Improvement:      5.2x faster
📈 Efficiency Gain:       80.8%
```

## Requirements

- Python 3.7+
- ib-insync
- pandas
- numpy

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Disclaimer

This software is for educational and research purposes. Options trading involves substantial risk. Always verify results and consult with financial professionals before making trading decisions. 