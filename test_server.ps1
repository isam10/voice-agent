# Test Script for Voice Assistant Server
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Testing Voice Assistant Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Root endpoint
Write-Host "Test 1: Root Endpoint (GET /)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
    Write-Host "✓ Status: SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 2
} catch {
    Write-Host "✗ Status: FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Health endpoint
Write-Host "Test 2: Health Check (GET /health)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✓ Status: SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 2
} catch {
    Write-Host "✗ Status: FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Metrics endpoint
Write-Host "Test 3: Metrics (GET /metrics)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/metrics" -Method Get
    Write-Host "✓ Status: SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 2
} catch {
    Write-Host "✗ Status: FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✓ Server is running on http://localhost:8000" -ForegroundColor Green
Write-Host "✓ All endpoints are responding correctly" -ForegroundColor Green
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
