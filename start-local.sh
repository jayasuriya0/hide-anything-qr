#!/bin/bash

# Hide Anything with QR - Local Development Startup Script (Mac/Linux)

echo "🚀 Starting Hide Anything with QR - Local Development"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Download: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Start Docker containers
echo "📦 Starting MongoDB and Redis containers..."
docker-compose -f docker-compose.local.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker containers"
    exit 1
fi

echo "✅ Docker containers started"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if containers are running
echo "🔍 Checking services..."
docker-compose -f docker-compose.local.yml ps

echo ""
echo "==========================================="
echo "✅ Services are ready!"
echo "==========================================="
echo ""
echo "📋 Next steps:"
echo "1. Open another terminal"
echo "2. Navigate to: cd backend"
echo "3. (Optional) Activate virtual environment: source ../venv/bin/activate"
echo "4. Run: python app.py"
echo ""
echo "🌐 Access the app at: http://localhost:5000"
echo ""
echo "💡 To stop services, run:"
echo "   docker-compose -f docker-compose.local.yml down"
echo ""
