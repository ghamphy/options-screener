#!/usr/bin/env python3
"""
AVGO Option Quote Examples - Multiple ways to get option quotes

This script demonstrates various ways to get bid/ask prices for AVGO options,
including the specific $32 put option you requested.

Requirements:
- IBKR Gateway or TWS must be running
- Active market data subscription for options
- ib_insync library installed
"""

import sys
import time
from datetime import datetime, timedelta
from quick_option_quote import get_option_quote
from specific_option_quote import SpecificOptionQuote

def example_1_simple_quote():
    """Example 1: Simple one-line quote using utility function"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Quick Quote Function")
    print("="*60)
    
    print("Getting AVGO $32 Put quote using simple utility function...")
    
    quote = get_option_quote('AVGO', 32.0, 'P')
    
    if quote.get('success'):
        print(f"✅ SUCCESS!")
        print(f"   Bid: ${quote['bid']:.2f}")
        print(f"   Ask: ${quote['ask']:.2f}")
        if quote['bid'] and quote['ask']:
            spread = quote['ask'] - quote['bid']
            mid = (quote['bid'] + quote['ask']) / 2
            print(f"   Spread: ${spread:.2f}")
            print(f"   Mid-point: ${mid:.2f}")
        print(f"   Expiration: {quote['expiration']}")
        if quote.get('last'):
            print(f"   Last Trade: ${quote['last']:.2f}")
    else:
        print(f"❌ Error: {quote.get('error')}")

def example_2_detailed_quote():
    """Example 2: Detailed quote using the class-based approach"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Detailed Quote with Class")
    print("="*60)
    
    # Create quote retriever
    retriever = SpecificOptionQuote(port=4001)  # Adjust port as needed
    
    try:
        print("Connecting to IBKR...")
        if not retriever.connect():
            print("❌ Failed to connect")
            return
        
        print("✅ Connected! Getting detailed quote...")
        
        quote = retriever.get_specific_option_quote('AVGO', 32.0, option_type='P')
        
        if 'error' not in quote:
            print(f"✅ Detailed Quote Retrieved!")
            print(f"   Symbol: {quote['symbol']}")
            print(f"   Strike: ${quote['strike']}")
            print(f"   Type: {'Put' if quote['option_type'] == 'P' else 'Call'}")
            print(f"   Expiration: {quote['expiration']}")
            print(f"   Bid: ${quote['bid']:.2f}" if quote['bid'] else "   Bid: No data")
            print(f"   Ask: ${quote['ask']:.2f}" if quote['ask'] else "   Ask: No data")
            
            if quote.get('delta'):
                print(f"   Delta: {quote['delta']:.3f}")
            if quote.get('implied_vol'):
                print(f"   Implied Vol: {quote['implied_vol']:.1%}")
            if quote.get('volume'):
                print(f"   Volume: {quote['volume']:,}")
                
            print(f"   Data Quality: {'Good' if quote['data_received'] else 'Poor'}")
        else:
            print(f"❌ Error: {quote['error']}")
    
    finally:
        retriever.disconnect()

def example_3_multiple_strikes():
    """Example 3: Get quotes for multiple strike prices"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Multiple AVGO Put Strikes")
    print("="*60)
    
    strikes = [28, 30, 32, 34, 36]  # Multiple strikes around $32
    
    print(f"Getting quotes for AVGO put options at strikes: {strikes}")
    print("-" * 60)
    
    for strike in strikes:
        print(f"Strike ${strike}:")
        quote = get_option_quote('AVGO', float(strike), 'P', client_id=3)
        
        if quote.get('success'):
            bid = f"${quote['bid']:.2f}" if quote['bid'] else "N/A"
            ask = f"${quote['ask']:.2f}" if quote['ask'] else "N/A"
            print(f"  Bid: {bid:>8} | Ask: {ask:>8}")
        else:
            print(f"  Error: {quote.get('error', 'Unknown')}")
        
        time.sleep(1)  # Small delay between requests

def example_4_different_expirations():
    """Example 4: Same strike, different expirations"""
    print("\n" + "="*60)
    print("EXAMPLE 4: AVGO $32 Put - Different Expirations")
    print("="*60)
    
    target_dtes = [7, 14, 30, 45, 60]  # Different expiration timeframes
    
    print("Getting $32 puts with different expiration dates:")
    print("-" * 60)
    
    for dte in target_dtes:
        print(f"Target DTE ~{dte} days:")
        quote = get_option_quote('AVGO', 32.0, 'P', target_dte=dte, client_id=4)
        
        if quote.get('success'):
            bid = f"${quote['bid']:.2f}" if quote['bid'] else "N/A"
            ask = f"${quote['ask']:.2f}" if quote['ask'] else "N/A"
            exp_date = quote['expiration']
            # Calculate actual DTE
            actual_dte = (datetime.strptime(exp_date, '%Y%m%d').date() - datetime.now().date()).days
            print(f"  Exp: {exp_date} ({actual_dte} DTE) | Bid: {bid} | Ask: {ask}")
        else:
            print(f"  Error: {quote.get('error', 'Unknown')}")
        
        time.sleep(1)

def check_ibkr_connection():
    """Check if IBKR connection is available"""
    print("Checking IBKR connection...")
    
    # Try a quick connection test
    test_quote = get_option_quote('AAPL', 150.0, 'P', client_id=99)
    
    if 'error' in test_quote:
        print("❌ IBKR Connection Problem:")
        print(f"   {test_quote['error']}")
        print("\nTroubleshooting:")
        print("1. Make sure IBKR Gateway or TWS is running")
        print("2. Check if the port is correct (4001 for Gateway, 7497 for TWS Paper)")
        print("3. Ensure you have market data permissions for options")
        print("4. Verify API is enabled in TWS/Gateway settings")
        return False
    else:
        print("✅ IBKR connection appears to be working")
        return True

def main():
    """Main function to run all examples"""
    print("AVGO $32 Put Option Quote Examples")
    print("Interactive Brokers API Demo")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check connection first
    if not check_ibkr_connection():
        print("\n⚠️  Cannot proceed without IBKR connection")
        return
    
    print("\nRunning examples...")
    
    try:
        # Run examples
        example_1_simple_quote()
        time.sleep(2)
        
        example_2_detailed_quote() 
        time.sleep(2)
        
        example_3_multiple_strikes()
        time.sleep(2)
        
        example_4_different_expirations()
        
        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60)
        
        print("\nNOTE: If you see 'No data' or errors:")
        print("- Market might be closed")
        print("- Option might not be actively traded")
        print("- You might need market data subscriptions")
        print("- Strike/expiration might not exist")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()