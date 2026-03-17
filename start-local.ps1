# Hide Anything with QR - Local Development Startup Script (Windows)

Write-Host "🚀 Starting Hide Anything with QR - Local Development" -ForegroundColor Green
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Starting MongoDB and Redis containers..." -ForegroundColor Cyan

# Start Docker containers
docker-compose -f docker-compose.local.yml up -d

if ($?) {
    Write-Host "✅ Docker containers started" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start Docker containers" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⏳ Waiting for services to be ready (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "🔍 Checking services..." -ForegroundColor Cyan
docker-compose -f docker-compose.local.yml ps

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ Services are ready!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Open another PowerShell/CMD window" -ForegroundColor White
Write-Host "2. Navigate to the backend folder:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Yellow
Write-Host "3. (Recommended) Activate virtual environment:" -ForegroundColor White
Write-Host "   python -m venv venv" -ForegroundColor Yellow
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "4. Install dependencies:" -ForegroundColor White
Write-Host "   pip install -r requirements.txt" -ForegroundColor Yellow
Write-Host "5. Run the Flask app:" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Yellow
Write-Host ""

Write-Host "🌐 Access the app at:" -ForegroundColor Cyan
Write-Host "   http://localhost:5000" -ForegroundColor Yellow
Write-Host ""

Write-Host "💡 To stop services later, run:" -ForegroundColor Cyan
Write-Host "   docker-compose -f docker-compose.local.yml down" -ForegroundColor Yellow
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
