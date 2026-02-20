# Cleanup and Push to GitHub Script
# Run this from the energy-analytics-system directory

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                    CLEANUP AND PUSH TO GITHUB" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Remove unwanted files
Write-Host "STEP 1: Removing temporary and redundant files..." -ForegroundColor Yellow

$filesToRemove = @(
    "deployment_info.json",
    "report.txt",
    "NEXT_STEP.txt",
    "RUN_THIS_NOW.txt",
    "TEST_LAMBDA_NOW.txt",
    "FINAL_STEPS.txt",
    "PUSH_TO_GITHUB_NOW.txt",
    "RUN_THIS_TO_PUSH_GITHUB.txt",
    "START_HERE_FINAL.md"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ Removed: $file" -ForegroundColor Green
    } else {
        Write-Host "  - Not found: $file (already removed)" -ForegroundColor Gray
    }
}

Write-Host ""

# Step 2: Check git status
Write-Host "STEP 2: Checking git status..." -ForegroundColor Yellow
git status
Write-Host ""

# Step 3: Add all changes
Write-Host "STEP 3: Adding all changes to git..." -ForegroundColor Yellow
git add .
Write-Host "  ✓ All changes staged" -ForegroundColor Green
Write-Host ""

# Step 4: Commit
Write-Host "STEP 4: Committing changes..." -ForegroundColor Yellow
git commit -m "Add comprehensive documentation and cleanup temporary files"
Write-Host ""

# Step 5: Push to GitHub
Write-Host "STEP 5: Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "                    ✓ SUCCESS! PUSHED TO GITHUB" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository: https://github.com/vaishal-coder/Cloud-Native-Energy-Analytics-System" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Visit your repository" -ForegroundColor White
    Write-Host "  2. Add description and topics" -ForegroundColor White
    Write-Host "  3. Add MIT License" -ForegroundColor White
    Write-Host "  4. Star your repo ⭐" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host "                    ✗ PUSH FAILED" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running manually:" -ForegroundColor Yellow
    Write-Host "  git push origin main" -ForegroundColor White
    Write-Host ""
}
