#!/usr/bin/env python3
"""
Put Options Screener for Cash-Secured Put Strategies
Modular version using the reusable screener library
"""

import sys
from put_option_screener import screen_put_options, get_interactive_inputs, benchmark_comparison, parse_arguments

def main():
    """Main entry point - wrapper around the modular screener"""
    args = parse_arguments()
    
    # Handle benchmark mode
    if args.benchmark:
        ticker = args.ticker or 'AAPL'
        benchmark_comparison(ticker, args.dte, args.risk)
        return
    
    # Handle interactive mode
    if args.interactive or not args.ticker:
        ticker, target_dte, max_risk = get_interactive_inputs()
        use_optimized = not args.slow
    else:
        # Command line mode
        ticker = args.ticker
        target_dte = args.dte
        max_risk = args.risk
        use_optimized = not args.slow
        
        print(f"📊 Command line mode: {ticker}, {target_dte} DTE, {max_risk}% max risk")
    
    # Run the screening
    screen_put_options(ticker, target_dte, max_risk, use_optimized)

if __name__ == "__main__":
    main() 