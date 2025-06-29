#!/usr/bin/env python3
"""
Base Options Screener - Core IBKR functionality for options trading

Provides reusable components for different option screening strategies.
Requires ib_insync, pandas, numpy.
"""

import logging
import time
import math
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Union
from ib_insync import IB, Stock, Option, util
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptionsScreener:
    """
    Base class for options screening with IBKR integration.
    
    Provides core functionality for stock prices, option chains, market data,
    and Black-Scholes calculations. Extend for specific strategies.
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
    
    def get_stock_price(self, ticker: str) -> Tuple[Optional[float], str, Optional[object]]:
        """
        Get current stock price with fallback methods.
        
        Returns:
            Tuple of (price, method_used, raw_data)
            Methods: 'historical_data', 'market_data', 'qualify_failed', 'all_methods_failed', 'exception'
        """
        try:
            contract = Stock(ticker, 'SMART', 'USD')
            qualified_contracts = self.ib.qualifyContracts(contract)
            
            if not qualified_contracts:
                logger.error(f"Could not qualify contract for {ticker}")
                return None, "qualify_failed", None
            
            contract = qualified_contracts[0]
            logger.info(f"Qualified contract: {contract}")
            
            # Method 1: Try historical data first (more reliable)
            try:
                logger.info("Attempting historical data request...")
                bars = self.ib.reqHistoricalData(
                    contract,
                    endDateTime='',
                    durationStr='1 D',
                    barSizeSetting='1 day',
                    whatToShow='TRADES',
                    useRTH=True,
                    formatDate=1
                )
                
                if bars and len(bars) > 0:
                    price = float(bars[-1].close)
                    logger.info(f"Got price via historical data: ${price}")
                    return price, "historical_data", bars[-1]
                    
            except Exception as e:
                logger.warning(f"Historical data request failed: {e}")
            
            # Method 2: Try market data
            try:
                logger.info("Attempting market data request...")
                ticker_data = self.ib.reqMktData(contract, '', True, False)
                
                # Wait for data
                for i in range(10):
                    self.ib.sleep(0.5)
                    if not util.isNan(ticker_data.last) and ticker_data.last > 0:
                        price = float(ticker_data.last)
                        self.ib.cancelMktData(contract)
                        logger.info(f"Got price via market data: ${price}")
                        return price, "market_data", ticker_data
                
                self.ib.cancelMktData(contract)
                
            except Exception as e:
                logger.warning(f"Market data request failed: {e}")
            
            return None, "all_methods_failed", None
            
        except Exception as e:
            logger.error(f"Error in get_stock_price for {ticker}: {str(e)}")
            return None, "exception", str(e)
    
    def get_option_chain(self, ticker: str, target_dte: int, option_type: str = 'P') -> List[Option]:
        """
        Get option chain for ticker with target DTE.
        
        Args:
            ticker: Stock symbol
            target_dte: Target days to expiration
            option_type: 'P' for puts, 'C' for calls
            
        Returns:
            List of qualified option contracts
        """
        try:
            stock = Stock(ticker, 'SMART', 'USD')
            qualified_stocks = self.ib.qualifyContracts(stock)
            
            if not qualified_stocks:
                logger.error(f"Could not qualify stock contract for {ticker}")
                return []
            
            stock = qualified_stocks[0]
            logger.info(f"Requesting option parameters for {ticker}")
            
            # Get option chains
            chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            
            if not chains:
                logger.warning(f"No option chains found for {ticker}")
                return []
            
            logger.info(f"Found {len(chains)} option chains")
            
            # Find the best expiration date
            target_date = datetime.now().date() + timedelta(days=target_dte)
            best_expiration = None
            min_diff = float('inf')
            
            chain = chains[0]
            
            for expiration in chain.expirations:
                exp_date = datetime.strptime(expiration, '%Y%m%d').date()
                diff = abs((exp_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    best_expiration = expiration
            
            if not best_expiration:
                logger.warning(f"No suitable expiration found for {ticker}")
                return []
            
            actual_dte = (datetime.strptime(best_expiration, '%Y%m%d').date() - datetime.now().date()).days
            logger.info(f"Selected expiration: {best_expiration} (DTE: {actual_dte})")
            
            # Create option contracts
            options = []
            strikes = sorted(chain.strikes)
            
            # Limit strikes to reasonable range
            middle_idx = len(strikes) // 2
            start_idx = max(0, middle_idx - 15)
            end_idx = min(len(strikes), middle_idx + 15)
            
            selected_strikes = strikes[start_idx:end_idx]
            
            for strike in selected_strikes:
                option = Option(ticker, best_expiration, strike, option_type, 'SMART')
                options.append(option)
            
            # Qualify contracts
            qualified_options = self.ib.qualifyContracts(*options)
            logger.info(f"Qualified {len(qualified_options)} {option_type} options")
            return qualified_options
            
        except Exception as e:
            logger.error(f"Error getting option chain for {ticker}: {str(e)}")
            return []

    def get_option_chain_optimized(self, ticker: str, target_dte: int, stock_price: float, 
                                 option_type: str = 'P', 
                                 price_filter_range: Tuple[float, float] = (0.70, 0.95)) -> Union[Tuple[List[Option], int], List]:
        """
        Get optimized option chain with strike filtering based on stock price.
        
        Args:
            price_filter_range: Strike filter as ratio of stock price (e.g. (0.70, 0.95) for puts)
            
        Returns:
            Tuple of (qualified_options, actual_dte) on success, empty list on error
        """
        try:
            stock = Stock(ticker, 'SMART', 'USD')
            qualified_stocks = self.ib.qualifyContracts(stock)
            
            if not qualified_stocks:
                logger.error(f"Could not qualify stock contract for {ticker}")
                return []
            
            stock = qualified_stocks[0]
            logger.info(f"Requesting option parameters for {ticker}")
            
            # Get option chains
            chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            
            if not chains:
                logger.warning(f"No option chains found for {ticker}")
                return []
            
            # Find the best expiration date
            target_date = datetime.now().date() + timedelta(days=target_dte)
            best_expiration = None
            min_diff = float('inf')
            
            chain = chains[0]
            
            for expiration in chain.expirations:
                exp_date = datetime.strptime(expiration, '%Y%m%d').date()
                diff = abs((exp_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    best_expiration = expiration
            
            if not best_expiration:
                logger.warning(f"No suitable expiration found for {ticker}")
                return []
            
            actual_dte = (datetime.strptime(best_expiration, '%Y%m%d').date() - datetime.now().date()).days
            logger.info(f"Selected expiration: {best_expiration} (DTE: {actual_dte})")
            
            # Smart strike filtering based on option type and stock price
            strikes = sorted(chain.strikes)
            
            if option_type == 'P':
                # For puts: filter strikes below stock price
                relevant_strikes = [s for s in strikes if s < stock_price]
            else:
                # For calls: filter strikes above stock price
                relevant_strikes = [s for s in strikes if s > stock_price]
            
            # Apply price filter range
            min_strike = stock_price * price_filter_range[0]
            max_strike = stock_price * price_filter_range[1]
            
            if option_type == 'P':
                relevant_strikes = [s for s in relevant_strikes if min_strike <= s <= max_strike]
            else:
                relevant_strikes = [s for s in relevant_strikes if min_strike <= s <= max_strike]
            
            # Limit to maximum 10 strikes
            if len(relevant_strikes) > 10:
                if option_type == 'P':
                    # For puts: take highest strikes (closest to stock price)
                    relevant_strikes = sorted(relevant_strikes, reverse=True)[:10]
                else:
                    # For calls: take lowest strikes (closest to stock price)
                    relevant_strikes = sorted(relevant_strikes)[:10]
            
            logger.info(f"Optimized: Selected {len(relevant_strikes)} relevant strikes (was {len(strikes)} total)")
            
            # Create option contracts
            options = []
            for strike in relevant_strikes:
                option = Option(ticker, best_expiration, strike, option_type, 'SMART')
                options.append(option)
            
            # Qualify contracts
            qualified_options = self.ib.qualifyContracts(*options)
            logger.info(f"Qualified {len(qualified_options)} {option_type} options")
            
            return qualified_options, actual_dte
            
        except Exception as e:
            logger.error(f"Error getting optimized option chain for {ticker}: {str(e)}")
            return []

    def get_option_market_data(self, option: Option) -> Dict[str, Optional[Union[float, bool]]]:
        """
        Get market data for single option: bid, ask, last, close, delta, IV.
        
        Returns:
            Dict with keys: bid, ask, last, close, delta, iv, data_received
        """
        try:
            logger.info(f"Getting market data for {option.symbol} ${option.strike} {option.right}")
            
            # Request market data with Greeks
            ticker_data = self.ib.reqMktData(option, '', False, False)
            
            # Wait for data to arrive with shorter timeout
            data_received = False
            for i in range(8):  # Wait up to 4 seconds
                self.ib.sleep(0.5)
                
                # Check if we have any useful data
                if (not util.isNan(ticker_data.bid) and ticker_data.bid > 0) or \
                   (not util.isNan(ticker_data.last) and ticker_data.last > 0) or \
                   (not util.isNan(ticker_data.close) and ticker_data.close > 0):
                    data_received = True
                    break
            
            # Get available data
            bid = ticker_data.bid if not util.isNan(ticker_data.bid) else None
            ask = ticker_data.ask if not util.isNan(ticker_data.ask) else None
            last = ticker_data.last if not util.isNan(ticker_data.last) else None
            close = ticker_data.close if not util.isNan(ticker_data.close) else None
            
            # Get Greeks
            delta = None
            iv = None
            
            if hasattr(ticker_data, 'modelGreeks') and ticker_data.modelGreeks:
                if not util.isNan(ticker_data.modelGreeks.delta):
                    delta = ticker_data.modelGreeks.delta
                if not util.isNan(ticker_data.modelGreeks.impliedVol):
                    iv = ticker_data.modelGreeks.impliedVol
            
            # If no Greeks from modelGreeks, try direct IV
            if iv is None and hasattr(ticker_data, 'impliedVolatility'):
                if not util.isNan(ticker_data.impliedVolatility):
                    iv = ticker_data.impliedVolatility
            
            # Clean up
            self.ib.cancelMktData(option)
            
            # Log what we got
            logger.info(f"Market data received - Bid: {bid}, Ask: {ask}, Last: {last}, Close: {close}, Delta: {delta}, IV: {iv}")
            
            return {
                'bid': float(bid) if bid and not util.isNan(bid) else None,
                'ask': float(ask) if ask and not util.isNan(ask) else None,
                'last': float(last) if last and not util.isNan(last) else None,
                'close': float(close) if close and not util.isNan(close) else None,
                'delta': float(delta) if delta and not util.isNan(delta) else None,
                'iv': float(iv) if iv and not util.isNan(iv) else None,
                'data_received': data_received
            }
            
        except Exception as e:
            logger.error(f"Error getting market data for option: {str(e)}")
            return {'bid': None, 'ask': None, 'last': None, 'close': None, 'delta': None, 'iv': None, 'data_received': False}

    def get_option_market_data_fast(self, options: List[Option], max_parallel: int = 5) -> Dict[Option, Dict[str, Optional[float]]]:
        """
        Get market data for multiple options in parallel batches.
        
        Args:
            max_parallel: Maximum parallel requests per batch (default: 5)
            
        Returns:
            Dict mapping each option to its market data dict
        """
        try:
            results = {}
            
            # Process options in batches
            for i in range(0, len(options), max_parallel):
                batch = options[i:i+max_parallel]
                logger.info(f"Getting market data for batch {i//max_parallel + 1}: {len(batch)} options")
                
                # Request market data for batch
                tickers = {}
                for option in batch:
                    ticker_data = self.ib.reqMktData(option, '', False, False)
                    tickers[option] = ticker_data
                
                # Wait for data
                self.ib.sleep(2)  # Reduced from 4 seconds
                
                # Collect results
                for option, ticker_data in tickers.items():
                    bid = ticker_data.bid if not util.isNan(ticker_data.bid) else None
                    ask = ticker_data.ask if not util.isNan(ticker_data.ask) else None
                    last = ticker_data.last if not util.isNan(ticker_data.last) else None
                    close = ticker_data.close if not util.isNan(ticker_data.close) else None
                    
                    # Get Greeks
                    delta = None
                    iv = None
                    
                    if hasattr(ticker_data, 'modelGreeks') and ticker_data.modelGreeks:
                        if not util.isNan(ticker_data.modelGreeks.delta):
                            delta = ticker_data.modelGreeks.delta
                        if not util.isNan(ticker_data.modelGreeks.impliedVol):
                            iv = ticker_data.modelGreeks.impliedVol
                    
                    results[option] = {
                        'bid': float(bid) if bid and not util.isNan(bid) else None,
                        'ask': float(ask) if ask and not util.isNan(ask) else None,
                        'last': float(last) if last and not util.isNan(last) else None,
                        'close': float(close) if close and not util.isNan(close) else None,
                        'delta': float(delta) if delta and not util.isNan(delta) else None,
                        'iv': float(iv) if iv and not util.isNan(iv) else None
                    }
                    
                    # Clean up
                    self.ib.cancelMktData(option)
                
                # Small delay between batches
                if i + max_parallel < len(options):
                    self.ib.sleep(0.5)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting batch market data: {str(e)}")
            return {}

    def estimate_option_delta(self, stock_price: float, strike: float, dte: int, 
                            option_type: str = 'P', iv: float = 0.25) -> Optional[float]:
        """
        Estimate option delta using Black-Scholes.
        
        Returns:
            Delta value (absolute for puts, positive for calls). None if calculation fails.
        """
        try:
            if dte <= 0 or strike <= 0 or stock_price <= 0:
                return None
            
            # Use risk-free rate approximation
            r = 0.05  # 5% risk-free rate
            t = dte / 365.0  # Time to expiration in years
            
            # Black-Scholes d1 calculation
            d1 = (math.log(stock_price / strike) + (r + 0.5 * iv * iv) * t) / (iv * math.sqrt(t))
            
            # Cumulative standard normal distribution approximation
            def norm_cdf(x):
                return 0.5 * (1 + math.erf(x / math.sqrt(2)))
            
            if option_type == 'P':
                # Put delta = -N(-d1) = N(d1) - 1
                delta = norm_cdf(d1) - 1
                return abs(delta)  # Return absolute value for probability calculation
            else:
                # Call delta = N(d1)
                delta = norm_cdf(d1)
                return delta
            
        except Exception as e:
            logger.warning(f"Could not estimate delta: {e}")
            return None
    
    def estimate_option_premium(self, stock_price: float, strike: float, dte: int, 
                              option_type: str = 'P', iv: float = 0.25) -> Optional[float]:
        """
        Estimate option premium using Black-Scholes.
        
        Returns:
            Estimated premium (minimum $0.01). None if calculation fails.
        """
        try:
            if dte <= 0 or strike <= 0 or stock_price <= 0:
                return None
            
            r = 0.05  # Risk-free rate
            t = dte / 365.0
            
            d1 = (math.log(stock_price / strike) + (r + 0.5 * iv * iv) * t) / (iv * math.sqrt(t))
            d2 = d1 - iv * math.sqrt(t)
            
            def norm_cdf(x):
                return 0.5 * (1 + math.erf(x / math.sqrt(2)))
            
            if option_type == 'P':
                # Put option price
                option_price = strike * math.exp(-r * t) * norm_cdf(-d2) - stock_price * norm_cdf(-d1)
            else:
                # Call option price
                option_price = stock_price * norm_cdf(d1) - strike * math.exp(-r * t) * norm_cdf(d2)
            
            return max(option_price, 0.01)  # Minimum $0.01
            
        except Exception as e:
            logger.warning(f"Could not estimate premium: {e}")
            return None
    
    def get_trading_session(self) -> str:
        """
        Determine current trading session: 'regular', 'extended', or 'closed'.
        
        Regular: 9:30 AM - 4:00 PM ET
        Extended: 4:00 AM - 9:30 AM or 4:00 PM - 8:00 PM ET
        Closed: Weekends or outside extended hours
        """
        try:
            import time
            
            # Get current UTC time and convert to EST/EDT approximation
            current_utc = datetime.utcnow()
            
            # Simple EST/EDT conversion (EST = UTC-5, EDT = UTC-4)
            # This is an approximation - for precise timezone use pytz
            utc_hour = current_utc.hour
            
            # Assume EDT (UTC-4) for market hours check
            et_hour = (utc_hour - 4) % 24
            et_minute = current_utc.minute
            
            # Check if it's a weekday (Monday=0, Sunday=6)
            if current_utc.weekday() >= 5:  # Saturday or Sunday
                logger.info(f"Trading session: ET time ~{et_hour:02d}:{et_minute:02d}, Weekend - CLOSED")
                return 'closed'
            
            current_time_minutes = et_hour * 60 + et_minute
            
            # Define trading sessions (all times in minutes from midnight)
            pre_market_start = 4 * 60        # 4:00 AM ET
            regular_open = 9 * 60 + 30       # 9:30 AM ET
            regular_close = 16 * 60          # 4:00 PM ET
            extended_close = 20 * 60         # 8:00 PM ET
            
            # Determine session
            if regular_open <= current_time_minutes <= regular_close:
                session = 'regular'
            elif (pre_market_start <= current_time_minutes < regular_open) or \
                 (regular_close < current_time_minutes <= extended_close):
                session = 'extended'
            else:
                session = 'closed'
            
            logger.info(f"Trading session: ET time ~{et_hour:02d}:{et_minute:02d}, Session: {session.upper()}")
            return session
            
        except Exception as e:
            logger.warning(f"Could not determine trading session: {e}")
            # Default to assuming closed for safety
            return 'closed'
    
    def is_market_hours(self) -> bool:
        """Check if currently regular market hours (9:30 AM - 4:00 PM ET)."""
        return self.get_trading_session() == 'regular'
    
    def is_weekly_expiration(self, expiration_str: str) -> bool:
        """
        Check if expiration is weekly (True) or monthly (False).
        
        Uses third Friday rule: monthly options expire on third Friday of month.
        """
        try:
            exp_date = datetime.strptime(expiration_str, '%Y%m%d').date()
            
            # Find the third Friday of the month (standard monthly expiration)
            year = exp_date.year
            month = exp_date.month
            
            # Find first day of month and its weekday
            first_day = datetime(year, month, 1).date()
            first_weekday = first_day.weekday()  # 0=Monday, 4=Friday
            
            # Calculate the third Friday
            days_to_first_friday = (4 - first_weekday) % 7
            first_friday = first_day + timedelta(days=days_to_first_friday)
            third_friday = first_friday + timedelta(days=14)
            
            # If expiration is not the third Friday, it's weekly
            return exp_date != third_friday
            
        except Exception as e:
            logger.warning(f"Could not determine weekly/monthly for {expiration_str}: {e}")
            return False  # Assume monthly if can't determine
    
    def calculate_annualized_return(self, premium: float, strike: float, dte: int) -> float:
        """
        Calculate annualized return for cash-secured strategies.
        
        Formula: (premium / strike) * (365 / dte) * 100
        """
        if dte <= 0 or strike <= 0:
            return 0.0
        return (premium / strike) * (365 / dte) * 100 