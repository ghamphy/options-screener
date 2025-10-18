# Enhanced Option Quote Programs

This directory contains several programs to get bid and ask prices for specific options from Interactive Brokers, with support for custom expiration dates.

## Files

### 1. `specific_option_quote.py` - Enhanced command-line option quote program ⭐ **UPDATED**
- **Purpose**: Get detailed bid/ask quotes for any specific option with full command-line support
- **Features**: 
  - Command-line arguments for ticker, strike, expiration, option type
  - List available expiration dates for any ticker
  - Auto-expiration selection or specific expiration dates
  - Support for both puts and calls
  - Comprehensive market data, Greeks, volume, error handling
- **Usage**: 
  ```bash
  # Basic usage with defaults (AVGO $325 put, auto-expiration)
  python specific_option_quote.py
  
  # Specific expiration date
  python specific_option_quote.py --ticker AVGO --strike 325 --expiration 20251121
  
  # Call option instead of put
  python specific_option_quote.py --ticker AAPL --strike 150 --call
  
  # List available expiration dates
  python specific_option_quote.py --list-expirations AVGO
  
  # Show all options
  python specific_option_quote.py --help
  ```

### 2. `quick_option_quote.py` - Simple utility function  
- **Purpose**: Simple one-function utility for quick quotes
- **Features**: Minimal code, can be imported as a module
- **Usage**: Import the `get_option_quote()` function or run directly

### 3. `avgo_option_examples.py` - Multiple examples and demos
- **Purpose**: Comprehensive examples showing different use cases
- **Features**: Multiple strikes, multiple expirations, connection testing
- **Usage**: Run to see various examples in action

### 4. `option_quote_examples.py` - Enhanced program examples ⭐ **NEW**
- **Purpose**: Demonstrates the new expiration date functionality
- **Features**: Shows command-line examples and interactive testing
- **Usage**: Run to see examples of the enhanced program

## Quick Start

### Prerequisites
1. **IBKR Gateway or TWS must be running**
   - Gateway: Usually port 4001
   - TWS Paper: Usually port 7497  
   - TWS Live: Usually port 7496

2. **Market data permissions** for options

3. **Required packages** (already in requirements.txt):
   ```
   ib-insync==0.9.86
   pandas>=2.1.4
   numpy>=1.26.0
   ```

### Method 1: Use the enhanced command-line program (RECOMMENDED)

#### Get AVGO $32 put with specific expiration:
```bash
# First, see what expirations are available
python specific_option_quote.py --list-expirations AVGO

# Then get quote with specific expiration
python specific_option_quote.py --ticker AVGO --strike 32 --expiration 20251121
```

#### More examples:
```bash
# AVGO $325 put (current default)
python specific_option_quote.py

# AAPL $150 call with specific expiration  
python specific_option_quote.py --ticker AAPL --strike 150 --expiration 20251024 --call

# MSFT $400 put with auto-selected expiration
python specific_option_quote.py --ticker MSFT --strike 400

# Show help for all options
python specific_option_quote.py --help
```

### Method 2: Use the quick utility function
```python
from quick_option_quote import get_option_quote

# Get AVGO $32 put quote with specific expiration
quote = get_option_quote('AVGO', 32.0, 'P', expiration='20251121')
if quote.get('success'):
    print(f"Bid: ${quote['bid']:.2f}, Ask: ${quote['ask']:.2f}")
else:
    print(f"Error: {quote['error']}")
```

### Method 3: Run the comprehensive examples
```bash
python avgo_option_examples.py              # Original examples
python option_quote_examples.py             # Enhanced program examples
```

## Command Line Options

The enhanced `specific_option_quote.py` supports these options:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--ticker` | `-t` | Stock symbol | AVGO |
| `--strike` | `-s` | Strike price | 325.0 |
| `--expiration` | `-e` | Expiration date (YYYYMMDD) | Auto-select nearest |
| `--call` | | Get call instead of put | Put option |
| `--list-expirations` | | List available expirations | |
| `--port` | | IBKR port | 4001 |
| `--host` | | IBKR host | 127.0.0.1 |
| `--help` | `-h` | Show help message | |

## Expiration Date Format

**Format**: YYYYMMDD (e.g., 20251121 for November 21, 2025)

**Examples**:
- `20251024` = October 24, 2025
- `20251115` = November 15, 2025  
- `20251219` = December 19, 2025

## Expected Output

### Successful Quote:
```
======================================================================
AVGO $32.0 Put Option Quote Retriever
Specific Expiration: 20251121 (2025-11-21 - 34 DTE)
======================================================================

✅ Connected to IBKR successfully

💰 BID: $0.85
💰 ASK: $0.95
📊 SPREAD: $0.10
📊 MID: $0.90

Last Trade: $0.88
Volume: 1,250
Delta: -0.234
Implied Vol: 28.5%
```

### List Expirations:
```
✅ Found 20 available expirations for AVGO:
--------------------------------------------------
 1. 20251024 → 2025-10-24 (Fri) (  6 DTE)
 2. 20251031 → 2025-10-31 (Fri) ( 13 DTE)
 3. 20251107 → 2025-11-07 (Fri) ( 20 DTE)
 4. 20251114 → 2025-11-14 (Fri) ( 27 DTE)
 ...
```

## Troubleshooting

### Common Issues:

1. **"Failed to connect to IBKR"**
   - Make sure Gateway/TWS is running
   - Check the port number (4001 for Gateway, 7497 for TWS Paper)
   - Verify API is enabled in settings

2. **"No market data received"**
   - Market might be closed (options trade 9:30 AM - 4:00 PM ET)
   - Option might not be actively traded  
   - Check if you have options market data permissions
   - Strike/expiration combination might not exist

3. **"Expiration 20251199 not available"**
   - Use `--list-expirations TICKER` to see valid dates
   - Ensure date format is YYYYMMDD
   - Check that the expiration date exists

4. **"Could not qualify option contract"**
   - Strike price might not be available for that expiration
   - Symbol might be incorrect
   - Use `--list-expirations` to verify available dates first

### Market Hours
- Options markets typically trade 9:30 AM - 4:00 PM ET
- Some options have extended hours but with limited liquidity
- Historical/close prices may be available outside market hours

## Advanced Usage

### Batch Processing Multiple Options
```bash
# Check multiple expirations for same strike
python specific_option_quote.py -t AVGO -s 32 -e 20251024
python specific_option_quote.py -t AVGO -s 32 -e 20251121  
python specific_option_quote.py -t AVGO -s 32 -e 20251219

# Check multiple strikes for same expiration
python specific_option_quote.py -t AVGO -s 30 -e 20251121
python specific_option_quote.py -t AVGO -s 32 -e 20251121
python specific_option_quote.py -t AVGO -s 35 -e 20251121
```

### Scripting and Automation
```bash
# Create a batch script to check multiple options
echo "python specific_option_quote.py -t AVGO -s 32 -e 20251121" > get_quotes.bat
echo "python specific_option_quote.py -t AAPL -s 150 -e 20251024 --call" >> get_quotes.bat
```

### Integration with Other Programs
```python
# Use in Python scripts
import subprocess

result = subprocess.run([
    'python', 'specific_option_quote.py', 
    '--ticker', 'AVGO', 
    '--strike', '32', 
    '--expiration', '20251121'
], capture_output=True, text=True)

print(result.stdout)
```

## Why Use Specific Expiration Dates?

1. **Precise Trading Strategy**: Target exact expiration dates for your strategy
2. **Event-Based Trading**: Align expiration with earnings, ex-dividend dates, etc.
3. **Time Decay Analysis**: Compare options with different time to expiration
4. **Liquidity Considerations**: Focus on monthly expirations for better liquidity
5. **Greeks Analysis**: Understand how time affects option pricing

## Integration with Existing Code

These enhanced programs work alongside your existing options screener:
- `options_base.py` - Your main options screening framework
- `put_option_screener.py` - Your put option screener  
- `put_screener_helper.py` - Your helper functions

The enhanced programs provide targeted functionality for specific option quotes with precise expiration control.