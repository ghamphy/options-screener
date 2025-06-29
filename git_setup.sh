#!/bin/bash
# Git setup script for Options Screener repository

echo "🚀 Setting up Git repository for Options Screener"
echo "=================================================="

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
else
    echo "📦 Git repository already exists"
fi

# Add all files to staging
echo "📁 Adding files to staging..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "feat: initial release of Options Screener v1.0.0

- Modular architecture with extensible OptionsScreener base class
- Put options screening with PutScreener (5x performance improvement)
- Multi-fallback stock price retrieval and market data handling
- Black-Scholes calculations and trading session detection
- Command-line interface with interactive and batch modes
- Comprehensive documentation and GitHub-ready structure"

echo ""
echo "✅ Repository is ready!"
echo ""
echo "Next steps:"
echo "1. Create a repository on GitHub"
echo "2. Add the remote origin:"
echo "   git remote add origin https://github.com/yourusername/options_screener.git"
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "To create a new branch for development:"
echo "   git checkout -b develop"
echo "   git push -u origin develop"
echo ""
echo "Happy coding! 🎉" 