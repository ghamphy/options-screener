#!/usr/bin/env python3
"""
Specific Option Quote Retriever - Get bid/ask prices for a specific option

This program retrieves bid and ask prices for specific options from Interactive Brokers.
Supports command line arguments for ticker, strike, expiration, and option type.

Usage:
    python specific_option_quote.py                                    # Use defaults
    python specific_option_quote.py --ticker AAPL --strike 150 --expiration 20241115
    python specific_option_quote.py -t MSFT -s 400 -e 20241220 --call
    python specific_option_quote.py --list-expirations AVGO           # Show available expirations
    python specific_option_quote.py --help                            # Show all options

Requirements:
    - IBKR Gateway or TWS running
    - ib_insync library
    - Active market data subscription for options
"""

import logging
import time
import argparse
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from ib_insync import IB, Stock, Option, util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpecificOptionQuote:
    """
    Simple class to get bid/ask quotes for a specific option.
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 4001, client_id: int = 1):
        """
        Initialize with IBKR connection parameters.
        
        Args:
            host: IBKR gateway host (default: '127.0.0.1')
            port: IBKR gateway port (4001=gateway, 7497=TWS paper, 7496=TWS live)
            client_id: Unique client ID for connection
        """
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to IBKR gateway. Returns True if successful."""
        try:
            if not self.connected:
                try:
                    util.startLoop()
                except RuntimeError:
                    pass  # Loop already running
                
                self.ib.connect(self.host, self.port, clientId=self.client_id)
                self.connected = True
                logger.info(f"Connected to IBKR gateway at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IBKR: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from IBKR gateway."""
        try:
            if self.connected:
                self.ib.disconnect()
                self.connected = False
                logger.info("Disconnected from IBKR gateway")
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
    
    def get_available_expirations(self, ticker: str) -> Optional[List[str]]:
        """
        Get all available expiration dates for a ticker.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            List of expiration dates in YYYYMMDD format, or None if error
        """
        try:
            stock = Stock(ticker, 'SMART', 'USD')
            qualified_stocks = self.ib.qualifyContracts(stock)
            
            if not qualified_stocks:
                logger.error(f"Could not qualify stock contract for {ticker}")
                return None
            
            stock = qualified_stocks[0]
            logger.info(f"Getting option parameters for {ticker}")
            
            # Get option chains
            chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            
            if not chains:
                logger.warning(f"No option chains found for {ticker}")
                return None
            
            chain = chains[0]
            expirations = list(chain.expirations)
            logger.info(f"Found {len(expirations)} available expirations")
            
            return expirations
            
        except Exception as e:
            logger.error(f"Error getting expirations for {ticker}: {str(e)}")
            return None

    def validate_expiration(self, ticker: str, expiration: str) -> bool:
        """
        Validate if an expiration date exists for the given ticker.
        
        Args:
            ticker: Stock symbol
            expiration: Expiration date in YYYYMMDD format
            
        Returns:
            True if expiration exists, False otherwise
        """
        try:
            available_expirations = self.get_available_expirations(ticker)
            if available_expirations is None:
                return False
            
            return expiration in available_expirations
            
        except Exception as e:
            logger.error(f"Error validating expiration: {str(e)}")
            return False

    def find_nearest_expiration(self, ticker: str, target_dte: int = 30) -> Optional[str]:
        """
        Find the nearest expiration date for options.
        
        Args:
            ticker: Stock symbol
            target_dte: Target days to expiration (default: 30 days)
            
        Returns:
            Expiration date string in YYYYMMDD format, or None if not found
        """
        try:
            available_expirations = self.get_available_expirations(ticker)
            if not available_expirations:
                return None
            
            # Find the best expiration date closest to target DTE
            target_date = datetime.now().date() + timedelta(days=target_dte)
            best_expiration = None
            min_diff = float('inf')
            
            logger.info(f"Available expirations: {available_expirations[:10]}")  # Show first 10
            
            for expiration in available_expirations:
                exp_date = datetime.strptime(expiration, '%Y%m%d').date()
                diff = abs((exp_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    best_expiration = expiration
            
            if best_expiration:
                actual_dte = (datetime.strptime(best_expiration, '%Y%m%d').date() - datetime.now().date()).days
                logger.info(f"Selected expiration: {best_expiration} (DTE: {actual_dte})")
            
            return best_expiration
            
        except Exception as e:
            logger.error(f"Error finding expiration for {ticker}: {str(e)}")
            return None
        """
        Find the nearest expiration date for options.
        
        Args:
            ticker: Stock symbol
            target_dte: Target days to expiration (default: 30 days)
            
        Returns:
            Expiration date string in YYYYMMDD format, or None if not found
        """
        try:
            stock = Stock(ticker, 'SMART', 'USD')
            qualified_stocks = self.ib.qualifyContracts(stock)
            
            if not qualified_stocks:
                logger.error(f"Could not qualify stock contract for {ticker}")
                return None
            
            stock = qualified_stocks[0]
            logger.info(f"Getting option parameters for {ticker}")
            
            # Get option chains
            chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            
            if not chains:
                logger.warning(f"No option chains found for {ticker}")
                return None
            
            # Find the best expiration date closest to target DTE
            target_date = datetime.now().date() + timedelta(days=target_dte)
            best_expiration = None
            min_diff = float('inf')
            
            chain = chains[0]
            logger.info(f"Available expirations: {chain.expirations[:10]}")  # Show first 10
            
            for expiration in chain.expirations:
                exp_date = datetime.strptime(expiration, '%Y%m%d').date()
                diff = abs((exp_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    best_expiration = expiration
            
            if best_expiration:
                actual_dte = (datetime.strptime(best_expiration, '%Y%m%d').date() - datetime.now().date()).days
                logger.info(f"Selected expiration: {best_expiration} (DTE: {actual_dte})")
            
            return best_expiration
            
        except Exception as e:
            logger.error(f"Error finding expiration for {ticker}: {str(e)}")
            return None
    
    def get_specific_option_quote(self, ticker: str, strike: float, expiration: str = None, 
                                option_type: str = 'P') -> Dict[str, Optional[float]]:
        """
        Get bid and ask prices for a specific option.
        
        Args:
            ticker: Stock symbol (e.g., 'AVGO')
            strike: Strike price (e.g., 32.0)
            expiration: Expiration date in YYYYMMDD format (if None, finds nearest)
            option_type: 'P' for put, 'C' for call
            
        Returns:
            Dictionary with bid, ask, last, and other market data
        """
        try:
            # If expiration is provided, validate it first
            if expiration is not None:
                # Validate expiration format
                try:
                    datetime.strptime(expiration, '%Y%m%d')
                except ValueError:
                    return {'error': f'Invalid expiration format. Use YYYYMMDD format, got: {expiration}'}
                
                # Check if expiration exists for this ticker
                if not self.validate_expiration(ticker, expiration):
                    available_exps = self.get_available_expirations(ticker)
                    if available_exps:
                        return {'error': f'Expiration {expiration} not available for {ticker}. Available: {available_exps[:5]}...'}
                    else:
                        return {'error': f'Could not get available expirations for {ticker}'}
            else:
                # If no expiration provided, find the nearest one
                expiration = self.find_nearest_expiration(ticker)
                if expiration is None:
                    return {'error': 'Could not find suitable expiration date'}
            
            # Create the option contract
            option = Option(ticker, expiration, strike, option_type, 'SMART')
            
            # Qualify the contract
            qualified_options = self.ib.qualifyContracts(option)
            
            if not qualified_options:
                logger.error(f"Could not qualify option contract: {ticker} ${strike} {option_type} {expiration}")
                return {'error': 'Could not qualify option contract'}
            
            option = qualified_options[0]
            logger.info(f"Qualified option: {option}")
            
            # Request market data
            logger.info(f"Requesting market data for {ticker} ${strike} {option_type} exp:{expiration}")
            ticker_data = self.ib.reqMktData(option, '', False, False)
            
            # Wait for data to arrive
            data_received = False
            for i in range(10):  # Wait up to 5 seconds
                self.ib.sleep(0.5)
                
                # Check if we have bid/ask data
                if (not util.isNan(ticker_data.bid) and ticker_data.bid > 0) or \
                   (not util.isNan(ticker_data.ask) and ticker_data.ask > 0):
                    data_received = True
                    break
                    
                logger.info(f"Waiting for data... attempt {i+1}/10")
            
            # Extract the data
            result = {
                'symbol': ticker,
                'strike': strike,
                'option_type': option_type,
                'expiration': expiration,
                'bid': ticker_data.bid if not util.isNan(ticker_data.bid) else None,
                'ask': ticker_data.ask if not util.isNan(ticker_data.ask) else None,
                'last': ticker_data.last if not util.isNan(ticker_data.last) else None,
                'close': ticker_data.close if not util.isNan(ticker_data.close) else None,
                'volume': ticker_data.volume if not util.isNan(ticker_data.volume) else None,
                'data_received': data_received,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to get implied volatility and delta if available
            if hasattr(ticker_data, 'modelGreeks') and ticker_data.modelGreeks:
                if not util.isNan(ticker_data.modelGreeks.delta):
                    result['delta'] = ticker_data.modelGreeks.delta
                if not util.isNan(ticker_data.modelGreeks.impliedVol):
                    result['implied_vol'] = ticker_data.modelGreeks.impliedVol
            
            # Clean up
            self.ib.cancelMktData(option)
            
            # Log the results
            if data_received:
                logger.info(f"SUCCESS - Bid: ${result['bid']:.2f}, Ask: ${result['ask']:.2f}")
                if result['last']:
                    logger.info(f"Last: ${result['last']:.2f}")
            else:
                logger.warning("No market data received - market may be closed or option inactive")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting option quote: {str(e)}")
            return {'error': str(e)}

def parse_arguments():
    """Parse command line arguments for option parameters."""
    parser = argparse.ArgumentParser(
        description='Get bid/ask quotes for a specific option from IBKR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python specific_option_quote.py                    # Use defaults (AVGO $325 Put, auto-expiration)
  python specific_option_quote.py --ticker AAPL --strike 150 --expiration 20241115
  python specific_option_quote.py -t MSFT -s 400 -e 20241220 --call
  python specific_option_quote.py --list-expirations AVGO    # Show available expirations

Expiration format: YYYYMMDD (e.g., 20241115 for November 15, 2024)
        """
    )
    
    parser.add_argument('-t', '--ticker', 
                       default='AVGO',
                       help='Stock symbol (default: AVGO)')
    
    parser.add_argument('-s', '--strike', 
                       type=float, 
                       default=325.0,
                       help='Strike price (default: 325.0)')
    
    parser.add_argument('-e', '--expiration',
                       help='Expiration date in YYYYMMDD format (default: auto-select nearest)')
    
    parser.add_argument('--call', 
                       action='store_true',
                       help='Get call option instead of put')
    
    parser.add_argument('--list-expirations',
                       metavar='TICKER',
                       help='List available expiration dates for a ticker and exit')
    
    parser.add_argument('--port',
                       type=int,
                       default=4001,
                       help='IBKR port (4001=Gateway, 7497=TWS Paper, 7496=TWS Live)')
    
    parser.add_argument('--host',
                       default='127.0.0.1',
                       help='IBKR host (default: 127.0.0.1)')
    
    return parser.parse_args()

def list_available_expirations(ticker: str, host: str = '127.0.0.1', port: int = 4001):
    """List all available expiration dates for a ticker."""
    print(f"Getting available expiration dates for {ticker}...")
    
    quote_retriever = SpecificOptionQuote(host=host, port=port, client_id=99)
    
    try:
        if not quote_retriever.connect():
            print("❌ Failed to connect to IBKR")
            return
        
        expirations = quote_retriever.get_available_expirations(ticker)
        
        if expirations:
            print(f"\n✅ Found {len(expirations)} available expirations for {ticker}:")
            print("-" * 50)
            
            for i, exp in enumerate(expirations[:20], 1):  # Show first 20
                try:
                    exp_date = datetime.strptime(exp, '%Y%m%d')
                    dte = (exp_date.date() - datetime.now().date()).days
                    formatted_date = exp_date.strftime('%Y-%m-%d (%a)')
                    print(f"{i:2d}. {exp} → {formatted_date} ({dte:3d} DTE)")
                except:
                    print(f"{i:2d}. {exp}")
            
            if len(expirations) > 20:
                print(f"    ... and {len(expirations) - 20} more")
                
        else:
            print(f"❌ No expirations found for {ticker}")
            
    finally:
        quote_retriever.disconnect()

def main():
    """
    Main function to get option quotes with command line argument support.
    """
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Handle list-expirations command
    if args.list_expirations:
        list_available_expirations(args.list_expirations, args.host, args.port)
        return
    
    # Configuration from arguments
    TICKER = args.ticker.upper()
    STRIKE = args.strike
    OPTION_TYPE = 'C' if args.call else 'P'
    EXPIRATION = args.expiration
    HOST = args.host
    PORT = args.port
    CLIENT_ID = 1
    
    print("=" * 70)
    print(f"{TICKER} ${STRIKE} {'Call' if OPTION_TYPE == 'C' else 'Put'} Option Quote Retriever")
    if EXPIRATION:
        try:
            exp_date = datetime.strptime(EXPIRATION, '%Y%m%d')
            dte = (exp_date.date() - datetime.now().date()).days
            print(f"Specific Expiration: {EXPIRATION} ({exp_date.strftime('%Y-%m-%d')} - {dte} DTE)")
        except:
            print(f"Specific Expiration: {EXPIRATION}")
    else:
        print("Expiration: Auto-select nearest")
    print("=" * 70)
    print("TIP: Use --help to see all available options")
    print("     Use --list-expirations TICKER to see available expiration dates")
    
    # Create quote retriever instance
    quote_retriever = SpecificOptionQuote(host=HOST, port=PORT, client_id=CLIENT_ID)
    
    try:
        # Connect to IBKR
        print("\n1. Connecting to IBKR...")
        if not quote_retriever.connect():
            print("❌ Failed to connect to IBKR. Make sure Gateway/TWS is running.")
            return
        
        print("✅ Connected to IBKR successfully")
        
        # Get the option quote
        print(f"\n2. Getting quote for {TICKER} ${STRIKE} {OPTION_TYPE} option...")
        quote_data = quote_retriever.get_specific_option_quote(
            ticker=TICKER,
            strike=STRIKE,
            expiration=EXPIRATION,
            option_type=OPTION_TYPE
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("OPTION QUOTE RESULTS")
        print("=" * 60)
        
        if 'error' in quote_data:
            print(f"❌ Error: {quote_data['error']}")
        else:
            print(f"Symbol: {quote_data['symbol']}")
            print(f"Strike: ${quote_data['strike']}")
            print(f"Type: {'Put' if quote_data['option_type'] == 'P' else 'Call'}")
            print(f"Expiration: {quote_data['expiration']}")
            print(f"Timestamp: {quote_data['timestamp']}")
            print("-" * 40)
            
            if quote_data['data_received']:
                if quote_data['bid'] is not None:
                    print(f"💰 BID: ${quote_data['bid']:.2f}")
                else:
                    print("💰 BID: No data")
                    
                if quote_data['ask'] is not None:
                    print(f"💰 ASK: ${quote_data['ask']:.2f}")
                else:
                    print("💰 ASK: No data")
                
                if quote_data['bid'] is not None and quote_data['ask'] is not None:
                    spread = quote_data['ask'] - quote_data['bid']
                    mid_price = (quote_data['bid'] + quote_data['ask']) / 2
                    print(f"📊 SPREAD: ${spread:.2f}")
                    print(f"📊 MID: ${mid_price:.2f}")
                
                print("-" * 40)
                
                if quote_data.get('last'):
                    print(f"Last Trade: ${quote_data['last']:.2f}")
                if quote_data.get('close'):
                    print(f"Previous Close: ${quote_data['close']:.2f}")
                if quote_data.get('volume'):
                    print(f"Volume: {quote_data['volume']:,}")
                if quote_data.get('delta'):
                    print(f"Delta: {quote_data['delta']:.3f}")
                if quote_data.get('implied_vol'):
                    print(f"Implied Vol: {quote_data['implied_vol']:.1%}")
            else:
                print("❌ No market data received")
                print("   Possible reasons:")
                print("   - Market is closed")
                print("   - Option is not actively traded")
                print("   - Insufficient market data permissions")
                print("   - Strike/expiration combination doesn't exist")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        # Always disconnect
        print("\n3. Disconnecting...")
        quote_retriever.disconnect()
        print("✅ Disconnected from IBKR")

if __name__ == "__main__":
    main()