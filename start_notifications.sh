#!/bin/bash

echo "🚀 Starting Agrikonnect Notification Service..."
echo ""

cd "$(dirname "$0")/microservices/notifications"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Notification service starting on http://localhost:5001"
echo "📝 Press Ctrl+C to stop"
echo ""

# Start the service
python app/app.py
