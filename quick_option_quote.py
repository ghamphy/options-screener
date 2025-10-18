#!/usr/bin/env python3
"""
Quick Option Quote Utility - Simple function to get option quotes

This module provides a simple function to quickly get bid/ask prices for any option.
Can be used as a standalone script or imported as a module.

Example usage:
    from quick_option_quote import get_option_quote
    
    # Get AVGO $32 put quote
    quote = get_option_quote('AVGO', 32, option_type='P')
    print(f"Bid: ${quote['bid']}, Ask: ${quote['ask']}")
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from ib_insync import IB, Stock, Option, util

# Configure minimal logging for this utility
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_option_quote(ticker: str, strike: float, option_type: str = 'P', 
                    expiration: str = None, target_dte: int = 30,
                    host: str = '127.0.0.1', port: int = 4001, 
                    client_id: int = 2) -> Dict:
    """
    Get bid/ask quote for a specific option.
    
    Args:
        ticker: Stock symbol (e.g., 'AVGO')
        strike: Strike price (e.g., 32.0)
        option_type: 'P' for put, 'C' for call
        expiration: Specific expiration in YYYYMMDD format (optional)
        target_dte: Target days to expiration if expiration not specified
        host: IBKR host
        port: IBKR port (4001=gateway, 7497=TWS paper, 7496=TWS live)
        client_id: Client ID for connection
        
    Returns:
        Dictionary with quote data or error information
    """
    
    ib = IB()
    
    try:
        # Start event loop if needed
        try:
            util.startLoop()
        except RuntimeError:
            pass
        
        # Connect
        ib.connect(host, port, clientId=client_id)
        
        # Find expiration if not provided
        if expiration is None:
            stock = Stock(ticker, 'SMART', 'USD')
            qualified_stocks = ib.qualifyContracts(stock)
            
            if not qualified_stocks:
                return {'error': f'Could not qualify stock contract for {ticker}'}
            
            stock = qualified_stocks[0]
            chains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            
            if not chains:
                return {'error': f'No option chains found for {ticker}'}
            
            # Find nearest expiration
            target_date = datetime.now().date() + timedelta(days=target_dte)
            best_expiration = None
            min_diff = float('inf')
            
            for exp in chains[0].expirations:
                exp_date = datetime.strptime(exp, '%Y%m%d').date()
                diff = abs((exp_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    best_expiration = exp
            
            expiration = best_expiration
        
        if not expiration:
            return {'error': 'Could not find suitable expiration date'}
        
        # Create and qualify option contract
        option = Option(ticker, expiration, strike, option_type, 'SMART')
        qualified_options = ib.qualifyContracts(option)
        
        if not qualified_options:
            return {'error': f'Could not qualify option: {ticker} ${strike} {option_type} {expiration}'}
        
        option = qualified_options[0]
        
        # Get market data
        ticker_data = ib.reqMktData(option, '', False, False)
        
        # Wait for data
        for i in range(10):
            ib.sleep(0.5)
            if (not util.isNan(ticker_data.bid) and ticker_data.bid > 0) or \
               (not util.isNan(ticker_data.ask) and ticker_data.ask > 0):
                break
        
        # Extract data
        result = {
            'symbol': ticker,
            'strike': strike,
            'option_type': option_type,
            'expiration': expiration,
            'bid': ticker_data.bid if not util.isNan(ticker_data.bid) else None,
            'ask': ticker_data.ask if not util.isNan(ticker_data.ask) else None,
            'last': ticker_data.last if not util.isNan(ticker_data.last) else None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': True
        }
        
        # Clean up
        ib.cancelMktData(option)
        
        return result
        
    except Exception as e:
        return {'error': str(e), 'success': False}
    
    finally:
        try:
            ib.disconnect()
        except:
            pass

def main():
    """Quick test of the utility function."""
    print("Testing AVGO $32 Put Option Quote...")
    
    quote = get_option_quote('AVGO', 32.0, 'P')
    
    if quote.get('success'):
        print(f"✅ Bid: ${quote['bid']:.2f}, Ask: ${quote['ask']:.2f}")
        print(f"   Expiration: {quote['expiration']}")
    else:
        print(f"❌ Error: {quote.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()