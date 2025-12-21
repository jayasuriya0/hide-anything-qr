#!/bin/bash

# Hide Anything with QR - Setup Script

echo "🚀 Setting up Hide Anything with QR..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if MongoDB is running
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB is not installed. Please install MongoDB 7.0 or higher."
    echo "Visit: https://docs.mongodb.com/manual/installation/"
fi

# Check if Redis is running
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis is not installed. Please install Redis 7.0 or higher."
    echo "Visit: https://redis.io/download"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ../.env ]; then
    echo "⚙️  Creating .env file..."
    cp ../.env.example ../.env
    echo "✏️  Please edit .env file and update the configuration values."
fi

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p static/uploads

# Go back to root
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure MongoDB and Redis are running"
echo "2. Update the .env file with your configuration"
echo "3. Run the application:"
echo "   cd backend"
echo "   python app.py"
echo ""
echo "🌐 The application will be available at http://localhost:5000"
echo ""
