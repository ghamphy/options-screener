#!/usr/bin/env python3
"""
Option Quote Examples - Demonstrates the enhanced specific_option_quote.py

This script shows different ways to use the enhanced option quote program
with specific expiration dates and various command line options.
"""

import subprocess
import sys
import time
from datetime import datetime, timedelta

def run_command(cmd, description):
    """Run a command and display the results."""
    print(f"\n{'='*70}")
    print(f"EXAMPLE: {description}")
    print(f"COMMAND: {cmd}")
    print('='*70)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    """Run examples of the enhanced option quote program."""
    
    print("Enhanced Option Quote Program Examples")
    print("=====================================")
    print("These examples demonstrate the new expiration date functionality")
    
    # Check if the program exists
    try:
        result = subprocess.run(
            "python specific_option_quote.py --help", 
            shell=True, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print("❌ Cannot find or run specific_option_quote.py")
            return
    except:
        print("❌ Cannot test specific_option_quote.py")
        return
    
    print("✅ Program found, running examples...\n")
    
    examples = [
        # Example 1: Show help
        ("python specific_option_quote.py --help", 
         "Show all command line options"),
        
        # Example 2: List available expirations
        ("python specific_option_quote.py --list-expirations AVGO", 
         "List all available AVGO option expirations"),
        
        # Example 3: Default behavior (auto-select expiration)
        ("python specific_option_quote.py", 
         "Default AVGO $325 put with auto-selected expiration"),
        
        # Example 4: Specific expiration (you'll need to adjust this date)
        ("python specific_option_quote.py --expiration 20241115", 
         "AVGO $325 put with specific expiration 2024-11-15"),
        
        # Example 5: Different ticker and strike
        ("python specific_option_quote.py --ticker AAPL --strike 150", 
         "AAPL $150 put with auto-selected expiration"),
        
        # Example 6: Call option instead of put
        ("python specific_option_quote.py --ticker MSFT --strike 400 --call", 
         "MSFT $400 call with auto-selected expiration"),
        
        # Example 7: Different port (if using TWS instead of Gateway)
        # ("python specific_option_quote.py --port 7497", 
        #  "Connect to TWS Paper Trading port"),
    ]
    
    # Run first two examples (help and list expirations)
    for i, (cmd, desc) in enumerate(examples[:2]):
        success = run_command(cmd, desc)
        if not success and i == 1:  # If list-expirations fails
            print("❌ Could not connect to IBKR. Make sure Gateway/TWS is running.")
            break
        time.sleep(1)
    
    # Ask user if they want to continue with actual quote requests
    print(f"\n{'='*70}")
    print("The next examples will make actual market data requests.")
    print("This requires:")
    print("- IBKR Gateway or TWS running")
    print("- Market data permissions")
    print("- Market hours (or you'll see 'No data' messages)")
    
    response = input("\nContinue with live quote examples? (y/n): ").lower().strip()
    
    if response.startswith('y'):
        print("\nRunning live quote examples...")
        
        # Run the remaining examples
        for cmd, desc in examples[2:6]:  # Skip the port example for now
            success = run_command(cmd, desc)
            if not success:
                print("❌ Example failed - continuing with next one...")
            time.sleep(2)  # Wait between requests
            
        print(f"\n{'='*70}")
        print("Examples completed!")
        print("="*70)
        print("\nTips for using the program:")
        print("1. Use --list-expirations TICKER to see available dates")
        print("2. Use YYYYMMDD format for expiration dates")
        print("3. Add --call for call options (default is puts)")
        print("4. Adjust --port if using TWS instead of Gateway")
        print("5. Use --help to see all options")
        
    else:
        print("Skipped live quote examples.")

if __name__ == "__main__":
    main()