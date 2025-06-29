"""
Options Screener - A modular Python library for screening options using Interactive Brokers API

This package provides tools for screening options with focus on cash-secured put strategies.
Features include performance optimization, market data handling, and extensible architecture.

Main modules:
- options_base: Core IBKR functionality and base classes
- put_screener: Put-specific screening logic  
- put_option_screener: Main application with CLI interface
- put_option_test: Simple wrapper for backward compatibility

Usage:
    from options_screener import PutScreener
    
    screener = PutScreener()
    screener.connect()
    result = screener.screen_puts('AAPL', 45, 0.20)
    screener.disconnect()
"""

__version__ = '1.0.0'
__author__ = 'Options Screener Team'
__license__ = 'MIT'

# Import main classes for convenience
try:
    from .options_base import OptionsScreener
    from .put_screener import PutScreener
    
    __all__ = ['OptionsScreener', 'PutScreener']
    
except ImportError:
    # Handle case where dependencies aren't installed yet
    __all__ = [] 