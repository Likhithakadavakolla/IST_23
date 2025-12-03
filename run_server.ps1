Write-Host "=== EduReach Flask Server Startup ===" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".\venv\Scripts\python.exe") {
    Write-Host "[OK] Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Check Flask installation
Write-Host "Testing Flask installation..."
& .\venv\Scripts\python.exe -c "import flask; print('Flask version:', flask.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Flask not installed properly!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting Flask server..." -ForegroundColor Yellow
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:5000" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Gray

# Run the server
& .\venv\Scripts\python.exe app.py
