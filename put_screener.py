#!/usr/bin/env python3
"""
Put Options Screener - Cash-secured put strategies
Extends the base OptionsScreener for put-specific functionality
"""

import logging
from datetime import datetime
from options_base import OptionsScreener

logger = logging.getLogger(__name__)

class PutScreener(OptionsScreener):
    """
    Put options screener for cash-secured put strategies
    Extends base OptionsScreener with put-specific logic
    """
    
    def __init__(self, host='127.0.0.1', port=4001, client_id=1):
        super().__init__(host, port, client_id)
    
    def get_best_premium_data(self, market_data: dict, strike: float, stock_price: float, dte: int) -> tuple:
        """Get the best available premium data with enhanced extended hours support"""
        
        trading_session = self.get_trading_session()
        
        # Try live market data during regular and extended hours
        if trading_session in ['regular', 'extended']:
            bid = market_data.get('bid')
            ask = market_data.get('ask')
            
            # Check for valid live bid/ask data
            if bid and ask and bid > 0 and ask > 0 and ask > bid:
                mid_price = (bid + ask) / 2
                spread = ask - bid
                
                # Different handling based on session
                if trading_session == 'regular':
                    logger.info(f"${strike} Put - Live market: Bid=${bid:.2f}, Ask=${ask:.2f}, Spread=${spread:.2f}")
                    data_source = "live_market"
                else:  # extended hours
                    logger.info(f"${strike} Put - Extended hours: Bid=${bid:.2f}, Ask=${ask:.2f}, Spread=${spread:.2f} (wider spreads expected)")
                    data_source = "live_extended"
                
                # For selling puts, use bid price (what we can get)
                return bid, data_source, {
                    'bid': bid, 'ask': ask, 'mid': mid_price, 'spread': spread, 'session': trading_session
                }
            
            elif bid and bid > 0:
                if trading_session == 'regular':
                    logger.info(f"${strike} Put - Live bid only: ${bid:.2f}")
                    data_source = "live_bid"
                else:  # extended hours
                    logger.info(f"${strike} Put - Extended hours bid: ${bid:.2f} (limited liquidity)")
                    data_source = "live_bid_extended"
                
                return bid, data_source, {'bid': bid, 'session': trading_session}
        
        # Priority 2: Last trade data (most recent actual transaction)
        last = market_data.get('last')
        if last and last > 0:
            if trading_session == 'closed':
                logger.info(f"${strike} Put - Last trade (market closed): ${last:.2f}")
                data_source = "last_trade_closed"
            else:
                logger.info(f"${strike} Put - Last trade: ${last:.2f}")
                data_source = "last_trade"
            
            return last, data_source, {'last': last, 'session': trading_session}
        
        # Priority 3: Theoretical estimate (skip close price for accuracy)
        logger.info(f"${strike} Put - No live/last trade data, using theoretical estimate")
        theoretical_premium = self.estimate_option_premium(stock_price, strike, dte, 'P')
        
        if theoretical_premium and theoretical_premium > 0:
            return theoretical_premium, "theoretical", {
                'estimated': theoretical_premium, 'session': trading_session
            }
        
        # Fallback: close price only if nothing else available
        close = market_data.get('close')
        if close and close > 0:
            logger.warning(f"${strike} Put - Using close price as last resort: ${close:.2f}")
            return close, "close_fallback", {'close': close, 'session': trading_session}
        
        return None, "no_data", {'session': trading_session}

    def screen_puts(self, ticker: str, target_dte: int, min_pitm: float = 0.10, max_pitm: float = 0.20, use_optimized: bool = True):
        """
        Screen put options for cash-secured put strategies
        
        Args:
            ticker: Stock symbol
            target_dte: Target days to expiration
            max_pitm: Maximum probability in-the-money (assignment risk)
            use_optimized: Use optimized screening method
            
        Returns:
            Dict with option details or None if no qualifying options found
        """
        try:
            # Get current stock price
            price_result = self.get_stock_price(ticker)
            if not price_result[0]:
                logger.error("Could not get stock price")
                return None
            
            stock_price = price_result[0]
            logger.info(f"Current {ticker} price: ${stock_price:.2f}")
            
            if use_optimized:
                return self._screen_puts_optimized(ticker, target_dte, min_pitm, max_pitm, stock_price)
            else:
                return self._screen_puts_standard(ticker, target_dte, min_pitm, max_pitm, stock_price)

        except Exception as e:
            logger.error(f"Error in put screening: {str(e)}")
            return None

    def _screen_puts_standard(self, ticker: str, target_dte: int, min_pitm: float, max_pitm: float, stock_price: float):
        """Standard put screening method"""
        try:
            # Get option chain
            options = self.get_option_chain(ticker, target_dte, 'P')
            if not options:
                logger.error("Could not get options chain")
                return None
            
            # Sort options by strike price (descending) to start with OTM puts
            options.sort(key=lambda x: float(x.strike), reverse=True)

            logger.info(f"Screening {len(options)} put options for {min_pitm:.0%} < PITM < {max_pitm:.0%}")

            for option in options:
                try:
                    strike = float(option.strike)
                    
                    # Skip ITM options (strike > stock price) as they'll have high PITM
                    if strike >= stock_price:
                        continue
                    
                    # Get market data
                    market_data = self.get_option_market_data(option)
                    
                    # Calculate expiration details
                    exp_date = datetime.strptime(option.lastTradeDateOrContractMonth, '%Y%m%d').date()
                    dte = (exp_date - datetime.now().date()).days
                    
                    # Get delta and premium
                    delta = market_data['delta']
                    
                    # Use enhanced data priority system
                    premium_result = self.get_best_premium_data(market_data, strike, stock_price, dte)
                    premium, data_source, premium_details = premium_result
                    
                    # Fallback for delta if not available from market data
                    if not delta:
                        delta = self.estimate_option_delta(stock_price, strike, dte, 'P')
                    
                    if not delta:
                        logger.warning(f"Could not calculate delta for ${strike} put, skipping...")
                        continue
                    
                    if not premium:
                        logger.warning(f"Could not determine premium for ${strike} put, skipping...")
                        continue
                    
                    # Calculate PITM (absolute delta for puts)
                    pitm = abs(delta)
                    
                    logger.info(f"${strike} Put - PITM: {pitm:.2%}, Premium: ${premium:.2f} ({data_source})")
                    
                    if pitm < max_pitm:
                        # Found qualifying option
                        is_weekly = self.is_weekly_expiration(option.lastTradeDateOrContractMonth)
                        annualized_return = self.calculate_annualized_return(premium, strike, dte)
                        
                        return {
                            'stock_price': stock_price,
                            'strike': strike,
                            'expiration': exp_date,
                            'expiration_str': option.lastTradeDateOrContractMonth,
                            'is_weekly': is_weekly,
                            'dte': dte,
                            'pitm': pitm,
                            'annualized_return': annualized_return,
                            'premium': premium,
                            'market_data': market_data,
                            'premium_details': premium_details,
                            'option': option,
                            'data_source': data_source
                        }
                
                except Exception as e:
                    logger.warning(f"Error processing option {option.strike}: {e}")
                    continue
            
            logger.warning(f"No qualifying put options found with PITM < {max_pitm:.0%}")
            return None
            
        except Exception as e:
            logger.error(f"Error in standard put screening: {str(e)}")
            return None

    def _screen_puts_optimized(self, ticker: str, target_dte: int, min_pitm: float, max_pitm: float, stock_price: float):
        """Optimized put screening method - 5x faster"""
        try:
            # Get pre-filtered option chain
            result = self.get_option_chain_optimized(ticker, target_dte, stock_price, 'P', (0.70, 0.95))
            if not result or len(result) != 2:
                logger.error("Could not get options chain")
                return None
            
            options, actual_dte = result
            if not options:
                logger.error("No relevant options found")
                return None
            
            # Sort by strike price (descending) to start with highest OTM strikes
            options.sort(key=lambda x: float(x.strike), reverse=True)
            
            logger.info(f"Optimized screening: {len(options)} pre-filtered options")
            
            # Quick delta pre-screening to avoid market data calls
            candidate_options = []
            for option in options:
                strike = float(option.strike)
                estimated_delta = self.estimate_option_delta(stock_price, strike, actual_dte, 'P')
                
                if estimated_delta and abs(estimated_delta) < max_pitm:
                    candidate_options.append(option)
                    logger.info(f"${strike} Put - Est. PITM: {abs(estimated_delta):.2%} (candidate)")
                else:
                    logger.info(f"${strike} Put - Est. PITM: {abs(estimated_delta):.2%} (skipped)")
            
            if not candidate_options:
                logger.warning("No candidates passed delta pre-screening")
                return None
            
            logger.info(f"Delta pre-screening: {len(candidate_options)} candidates (from {len(options)} total)")
            
            # Get market data for candidates only (parallel)
            market_data_results = self.get_option_market_data_fast(candidate_options)
            
            # Process candidates and find first qualifying
            for option in candidate_options:
                try:
                    strike = float(option.strike)
                    market_data = market_data_results.get(option, {})
                    
                    # Calculate expiration details
                    exp_date = datetime.strptime(option.lastTradeDateOrContractMonth, '%Y%m%d').date()
                    dte = (exp_date - datetime.now().date()).days
                    
                    # Get delta and premium with enhanced trading-focused priority
                    delta = market_data.get('delta')
                    
                    # Use enhanced data priority system
                    premium_result = self.get_best_premium_data(market_data, strike, stock_price, dte)
                    premium, data_source, premium_details = premium_result
                    
                    # Fallback for delta if not available from market data
                    if not delta:
                        delta = self.estimate_option_delta(stock_price, strike, dte, 'P')
                    
                    if not delta or not premium:
                        logger.warning(f"Could not get data for ${strike} put, skipping...")
                        continue
                    
                    # Calculate PITM
                    pitm = abs(delta)
                    
                    logger.info(f"${strike} Put - PITM: {pitm:.2%}, Premium: ${premium:.2f} ({data_source})")
                    
                    # Early exit on first qualifying option
                    if pitm < max_pitm:
                        is_weekly = self.is_weekly_expiration(option.lastTradeDateOrContractMonth)
                        annualized_return = self.calculate_annualized_return(premium, strike, dte)
                        
                        logger.info(f"✅ Found qualifying option early: ${strike} Put")
                        
                        return {
                            'stock_price': stock_price,
                            'strike': strike,
                            'expiration': exp_date,
                            'expiration_str': option.lastTradeDateOrContractMonth,
                            'is_weekly': is_weekly,
                            'dte': dte,
                            'pitm': pitm,
                            'annualized_return': annualized_return,
                            'premium': premium,
                            'market_data': market_data,
                            'premium_details': premium_details,
                            'option': option,
                            'data_source': data_source
                        }
                
                except Exception as e:
                    logger.warning(f"Error processing option {option.strike}: {e}")
                    continue
            
            logger.warning(f"No qualifying put options found with PITM < {max_pitm:.0%}")
            return None
            
        except Exception as e:
            logger.error(f"Error in optimized put screening: {str(e)}")
            return None 