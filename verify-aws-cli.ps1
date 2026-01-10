# AWS CLI Verification Script
Write-Host "Checking AWS CLI installation..." -ForegroundColor Cyan

try {
    $awsVersion = aws --version 2>&1
    Write-Host "✓ AWS CLI is installed!" -ForegroundColor Green
    Write-Host "Version: $awsVersion" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next step: Run 'aws configure' to set up your credentials" -ForegroundColor Cyan
} catch {
    Write-Host "✗ AWS CLI is not found in PATH" -ForegroundColor Red
    Write-Host "Please make sure you:" -ForegroundColor Yellow
    Write-Host "  1. Completed the installation" -ForegroundColor Yellow
    Write-Host "  2. Closed and reopened your terminal" -ForegroundColor Yellow
    Write-Host "  3. Restarted Claude Code" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
