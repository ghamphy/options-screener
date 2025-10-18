#!/usr/bin/env python3
"""
Put Options Screener - Main Application
Uses modular screener library for cash-secured put strategies
"""

import sys
import argparse
import time
from put_screener import PutScreener

def display_result(result, trading_session):
    """Display the screening results in a formatted way"""
    if not result:
        print("❌ No qualifying put options found")
        return False
    
    # Display results
    print("\n" + "="*75)
    print("🎯 QUALIFYING PUT OPTION FOUND")
    print("="*75)
    
    print(f"📊 Current Stock Price:    ${result['stock_price']:.2f}")
    print(f"💰 Strike Price:           ${result['strike']:.2f}")
    print(f"📅 Expiration Date:        {result['expiration'].strftime('%Y-%m-%d')} ({result['expiration_str']})")
    print(f"📈 Expiration Type:        {'Weekly' if result['is_weekly'] else 'Monthly'}")
    print(f"⏰ Days to Expiration:     {result['dte']} days")
    print(f"📉 Probability ITM (PITM): {result['pitm']:.2%}")
    print(f"💵 Premium:                ${result['premium']:.2f}")
    print(f"📈 Annualized Return:      {result['annualized_return']:.2f}%")
    
    # Show data source with explanation
    source_descriptions = {
        "live_market": "Live Market Data (Regular Hours)",
        "live_extended": "Live Market Data (Extended Hours)",
        "live_bid": "Live Bid Price (Regular Hours)",
        "live_bid_extended": "Live Bid Price (Extended Hours)",
        "last_trade": "Last Trade Price",
        "last_trade_closed": "Last Trade Price (Market Closed)",
        "theoretical": "Theoretical Estimate",
        "close_fallback": "Previous Close Price"
    }
    source_desc = source_descriptions.get(result['data_source'], result['data_source'].title())
    print(f"📡 Data Source:            {source_desc}")
    
    # Get session info if available
    session = result.get('premium_details', {}).get('session', 'unknown')
    
    # Additional market data based on source type
    if result['data_source'] == 'live_market':
        # Full live market data available (regular hours)
        if 'premium_details' in result and result['premium_details']:
            details = result['premium_details']
            if 'ask' in details:
                print(f"💸 Ask Price:              ${details['ask']:.2f}")
                print(f"🔄 Bid-Ask Spread:         ${details['spread']:.2f}")
                print(f"📊 Mid Price:              ${details['mid']:.2f}")
        print(f"🟢 Status: Live market data (regular hours) - highly accurate for trading")
        
        if result['market_data'].get('iv'):
            print(f"📊 Implied Volatility:     {result['market_data']['iv']:.2%}")
    
    elif result['data_source'] == 'live_extended':
        # Extended hours live data
        if 'premium_details' in result and result['premium_details']:
            details = result['premium_details']
            if 'ask' in details:
                print(f"💸 Ask Price:              ${details['ask']:.2f}")
                print(f"🔄 Bid-Ask Spread:         ${details['spread']:.2f}")
                print(f"📊 Mid Price:              ${details['mid']:.2f}")
        print(f"🟡 Status: Live extended hours data - usable but exercise caution")
        print(f"⚠️  Extended Hours Warning: Lower liquidity, wider spreads expected")
        
        if result['market_data'].get('iv'):
            print(f"📊 Implied Volatility:     {result['market_data']['iv']:.2%}")
    
    elif result['data_source'] == 'live_bid':
        print(f"🟡 Status: Live bid available (regular hours) - good for trading")
        if result['market_data'].get('iv'):
            print(f"📊 Implied Volatility:     {result['market_data']['iv']:.2%}")
    
    elif result['data_source'] == 'live_bid_extended':
        print(f"🟠 Status: Live bid available (extended hours) - limited liquidity")
        print(f"⚠️  Extended Hours Warning: Verify depth and consider market impact")
        if result['market_data'].get('iv'):
            print(f"📊 Implied Volatility:     {result['market_data']['iv']:.2%}")
    
    elif result['data_source'] == 'last_trade':
        print(f"🟠 Status: Using last trade - reasonable for reference")
    
    elif result['data_source'] == 'last_trade_closed':
        print(f"🔴 Status: Last trade data (market closed) - verify before trading")
        print(f"💡 Note: Market is closed, consider waiting for next session")
    
    elif result['data_source'] == 'theoretical':
        print(f"🔵 Status: Theoretical estimate - use for reference only")
        print(f"⚠️  Note: Based on Black-Scholes with 25% IV assumption")
        if session == 'extended':
            print(f"💡 Extended Hours: Consider waiting for regular hours for live data")
    
    elif result['data_source'] == 'close_fallback':
        print(f"🔴 Status: Previous close price - least accurate")
        print(f"⚠️  Caution: Stale data, verify before trading")
    
    # Risk assessment
    print(f"\n📋 RISK ASSESSMENT:")
    assignment_prob = result['pitm'] * 100
    print(f"   Assignment Probability: {assignment_prob:.1f}%")
    print(f"   Max Loss (if assigned): ${result['strike'] - result['premium']:.2f} per share")
    print(f"   Breakeven Price:        ${result['strike'] - result['premium']:.2f}")
    
    # Trading considerations based on session and data source
    print(f"\n🎯 TRADING CONSIDERATIONS:")
    data_source = result['data_source']
    session = result.get('premium_details', {}).get('session', trading_session)
    
    if data_source in ['live_market', 'live_bid'] and session == 'regular':
        print(f"✅ Optimal conditions: Live data during regular hours")
        print(f"   💡 Action: Safe to place trades with current pricing")
        
    elif data_source in ['live_extended', 'live_bid_extended'] and session == 'extended':
        print(f"⚠️  Extended hours trading:")
        print(f"   💡 Action: Consider smaller position sizes due to lower liquidity")
        print(f"   💡 Tip: Place limit orders with buffer for wider spreads")
        
    elif data_source in ['last_trade', 'last_trade_closed'] and session == 'closed':
        print(f"🔴 Market closed conditions:")
        print(f"   💡 Action: Wait for next trading session for live pricing")
        print(f"   💡 Alternative: Use data for planning, verify prices when market opens")
        
    elif data_source == 'theoretical':
        print(f"🔵 Theoretical pricing:")
        print(f"   💡 Action: Use for screening only, get live quotes before trading")
        if session == 'extended':
            print(f"   💡 Extended hours: Wait for regular hours for better data quality")
        elif session == 'closed':
            print(f"   💡 Market closed: Plan trade for next session")
    
    # Options trading reminders
    print(f"\n📝 OPTIONS TRADING REMINDERS:")
    print(f"   • This is a CASH-SECURED PUT strategy")
    print(f"   • Required capital: ${result['strike'] * 100:.0f} per contract")
    print(f"   • Assignment risk increases as expiration approaches")
    print(f"   • Monitor delta and adjust position if needed")
    
    print("="*75)
    return True

def screen_put_options(ticker='AAPL', target_dte=45, min_assignment_risk=10.0, max_assignment_risk=20.0, use_optimized=True):
    """Main screening function"""
    min_pitm = min_assignment_risk / 100.0  # Convert percentage to decimal
    max_pitm = max_assignment_risk / 100.0  # Convert percentage to decimal
    
    optimization_mode = "⚡ OPTIMIZED" if use_optimized else "🐌 STANDARD"
    print(f"📊 Finding {ticker.upper()} Put Option (~{target_dte} DTE) with Assignment Risk < {max_assignment_risk}%")
    print(f"🔧 Mode: {optimization_mode}")
    print("=" * 75)
    
    screener = None
    try:
        screener = PutScreener()
        print("✅ PutScreener created")
        
        # Connect
        print("🔗 Connecting to IBKR...")
        if not screener.connect():
            print("❌ Failed to connect to IBKR")
            return False
        
        print("✅ Successfully connected!")
        
        # Show trading session info
        trading_session = screener.get_trading_session()
        session_icons = {
            'regular': '🟢',
            'extended': '🟡', 
            'closed': '🔴'
        }
        session_descriptions = {
            'regular': 'Regular Hours (9:30 AM - 4:00 PM ET)',
            'extended': 'Extended Hours (4:00 AM - 9:30 AM or 4:00 PM - 8:00 PM ET)',
            'closed': 'Market Closed'
        }
        
        icon = session_icons.get(trading_session, '⚪')
        desc = session_descriptions.get(trading_session, trading_session.title())
        print(f"📅 Trading Session:        {icon} {desc}")
        
        if trading_session == 'extended':
            print("⚠️  Extended Hours Notice: Lower liquidity and wider spreads expected")
        elif trading_session == 'closed':
            print("💡 Market Closed Notice:  Using historical/last trade data")
        
        # Find qualifying put option
        print("🔍 Searching for qualifying put option...")
        print(f"   Criteria: ~{target_dte} DTE, {min_assignment_risk} < Assignment Probability < {max_assignment_risk}%")

        result = screener.screen_puts(ticker.upper(), target_dte, min_pitm, max_pitm, use_optimized)

        return display_result(result, trading_session)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if screener:
            screener.disconnect()
            print("✅ Disconnected")

def get_interactive_inputs():
    """Get screening parameters interactively from user"""
    print("📋 Interactive Put Options Screener")
    print("=" * 50)
    
    # Get ticker
    while True:
        ticker = input("Enter ticker symbol (e.g., AAPL, MSFT, TSLA): ").strip().upper()
        if ticker and ticker.isalpha():
            break
        print("⚠️  Please enter a valid ticker symbol (letters only)")
    
    # Get target DTE
    while True:
        try:
            dte_input = input("Enter target days to expiration (DTE) [30-120]: ").strip()
            if not dte_input:
                target_dte = 45  # Default
                break
            target_dte = int(dte_input)
            if 7 <= target_dte <= 365:
                break
            print("⚠️  Please enter a DTE between 7 and 365 days")
        except ValueError:
            print("⚠️  Please enter a valid number")
    
    # Get min assignment risk
    while True:
        try:
            risk_input = input("Enter Minimum assignment risk % (1-50): ").strip()
            if not risk_input:
                min_risk = 10.0  # Default
                break
            min_risk = float(risk_input)
            if 1.0 <= min_risk <= 50.0:
                break
            print("⚠️  Please enter a risk between 1% and 50%")
        except ValueError:
            print("⚠️  Please enter a valid number")
        
    # Get max assignment risk
    while True:
        try:
            risk_input = input("Enter maximum assignment risk % (5-50): ").strip()
            if not risk_input:
                max_risk = 20.0  # Default
                break
            max_risk = float(risk_input)
            if 1.0 <= max_risk <= 50.0:
                break
            print("⚠️  Please enter a risk between 1% and 50%")
        except ValueError:
            print("⚠️  Please enter a valid number")

    return ticker, target_dte, min_risk, max_risk

def benchmark_comparison(ticker='AAPL', target_dte=45, min_assignment_risk=10.0, max_assignment_risk=20.0):
    """Benchmark both methods and compare performance"""
    max_pitm = max_assignment_risk / 100.0
    min_pitm = min_assignment_risk / 100.0

    print(f"🏁 BENCHMARKING: {ticker} PUT OPTIONS SCREENING")
    print("=" * 60)
    print(f"Target: ~{target_dte} DTE, Min Risk: {min_assignment_risk}%, Max Risk: {max_assignment_risk}%")
    print()
    
    screener = None
    try:
        screener = PutScreener()
        
        if not screener.connect():
            print("❌ Failed to connect to IBKR for benchmark")
            return False
        
        print("✅ Connected to IBKR")
        print()
        
        # Test Standard Method
        print("🐌 TESTING STANDARD METHOD...")
        start_time = time.time()
        
        try:
            standard_result = screener.screen_puts(ticker, target_dte, min_pitm, max_pitm, use_optimized=False)
            standard_time = time.time() - start_time
            standard_success = standard_result is not None
        except Exception as e:
            print(f"❌ Standard method failed: {e}")
            standard_time = time.time() - start_time
            standard_success = False
            standard_result = None
        
        print(f"⏱️  Standard Method Time: {standard_time:.1f} seconds")
        print(f"✅ Standard Result: {'Success' if standard_success else 'Failed'}")
        if standard_result:
            print(f"   Found: ${standard_result['strike']} Put, {standard_result['pitm']:.2%} PITM")
        print()
        
        # Test Optimized Method
        print("⚡ TESTING OPTIMIZED METHOD...")
        start_time = time.time()
        
        try:
            optimized_result = screener.screen_puts(ticker, target_dte, max_pitm, use_optimized=True)
            optimized_time = time.time() - start_time
            optimized_success = optimized_result is not None
        except Exception as e:
            print(f"❌ Optimized method failed: {e}")
            optimized_time = time.time() - start_time
            optimized_success = False
            optimized_result = None
        
        print(f"⏱️  Optimized Method Time: {optimized_time:.1f} seconds")
        print(f"✅ Optimized Result: {'Success' if optimized_success else 'Failed'}")
        if optimized_result:
            print(f"   Found: ${optimized_result['strike']} Put, {optimized_result['pitm']:.2%} PITM")
        print()
        
        # Performance Summary
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 40)
        
        if standard_time > 0 and optimized_time > 0:
            speedup = standard_time / optimized_time
            time_saved = standard_time - optimized_time
            efficiency = ((standard_time - optimized_time) / standard_time) * 100
            
            print(f"🐌 Standard Time:     {standard_time:.1f}s")
            print(f"⚡ Optimized Time:    {optimized_time:.1f}s")
            print(f"⏱️  Time Saved:       {time_saved:.1f}s")
            print(f"🚀 Speed Improvement: {speedup:.1f}x faster")
            print(f"📈 Efficiency Gain:   {efficiency:.1f}%")
        
        # Result Comparison
        if standard_success and optimized_success:
            if standard_result['strike'] == optimized_result['strike']:
                print(f"🎯 Results: IDENTICAL (both found ${standard_result['strike']} Put)")
            else:
                print(f"🔄 Results: DIFFERENT")
                print(f"   Standard: ${standard_result['strike']} Put")
                print(f"   Optimized: ${optimized_result['strike']} Put")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Benchmark error: {e}")
        return False
        
    finally:
        if screener:
            screener.disconnect()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Screen put options for cash-secured put strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python put_option_screener.py                           # Interactive mode (fast)
  python put_option_screener.py AAPL                     # AAPL with defaults (fast)
  python put_option_screener.py AAPL --dte 60            # AAPL, 60 DTE (fast)
  python put_option_screener.py MSFT --dte 30 --minrisk 10 --maxrisk 20   # MSFT, 30 DTE, 15% risk (fast)
  python put_option_screener.py AAPL --slow              # Use standard slower method
  python put_option_screener.py AAPL --benchmark         # Compare both methods
        """
    )
    
    parser.add_argument('ticker', nargs='?', help='Stock ticker symbol (e.g., AAPL, MSFT)')
    parser.add_argument('--dte', type=int, default=45, help='Target days to expiration (default: 45)')
    parser.add_argument('--minrisk', type=float, default=10.0, help='Minimun assignment risk percentage (default: 10.0)')
    parser.add_argument('--maxrisk', type=float, default=20.0, help='Maximum assignment risk percentage (default: 20.0)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Force interactive mode')
    parser.add_argument('--fast', action='store_true', help='Use optimized fast mode (default)')
    parser.add_argument('--slow', action='store_true', help='Use standard slower method for comparison')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmark comparing both methods')
    
    return parser.parse_args()

def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Handle benchmark mode
    if args.benchmark:
        ticker = args.ticker or 'AAPL'
        benchmark_comparison(ticker, args.dte, args.risk)
        return
    
    # Handle interactive mode
    if args.interactive or not args.ticker:
        ticker, target_dte, min_risk, max_risk = get_interactive_inputs()
        use_optimized = not args.slow  # Default to optimized unless --slow specified
    else:
        # Command line mode
        ticker = args.ticker
        target_dte = args.dte
        min_risk = args.minrisk
        max_risk = args.maxrisk
        use_optimized = not args.slow  # Use optimized by default unless --slow

        print(f"📊 Command line mode: {ticker}, {target_dte} DTE, {min_risk}% min risk, {max_risk}% max risk")

    # Run the screening
    screen_put_options(ticker, target_dte, min_risk, max_risk, use_optimized)

if __name__ == "__main__":
    main() 