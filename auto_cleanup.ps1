# Auto Cleanup and Push Script
Write-Host "Starting cleanup..." -ForegroundColor Cyan

# Step 1: Remove temporary files
$filesToRemove = @(
    "deployment_info.json", "report.txt", "NEXT_STEP.txt", "RUN_THIS_NOW.txt",
    "TEST_LAMBDA_NOW.txt", "FINAL_STEPS.txt", "PUSH_TO_GITHUB_NOW.txt",
    "RUN_THIS_TO_PUSH_GITHUB.txt", "START_HERE_FINAL.md", "CLEANUP_AND_PUSH.txt",
    "PUSH_COMMANDS.txt", "RUN_THESE_COMMANDS.txt", "cleanup_and_push.ps1",
    "CONGRATULATIONS.txt", "GITHUB_SUCCESS.md", "PROJECT_STRUCTURE.txt",
    "PROJECT_OVERVIEW.txt", "PROJECT_SUMMARY.txt", "DEPLOYMENT_SUMMARY.txt",
    "EXECUTION_SUMMARY.md", "AUTONOMOUS_EXECUTION_REPORT.md", "COMPLETE_DEPLOYMENT.md",
    "START_HERE.md", "TROUBLESHOOT_AND_FIX.md", "GITHUB_SETUP.md",
    "SETUP_AWS_CREDENTIALS.md", "EVERYTHING_YOU_NEED_TO_KNOW.md", "QUICK_ANSWERS.md",
    "PROJECT_COMPLETE.md", "DOCUMENTATION_INDEX.md", "CLEANUP_SCRIPT.txt",
    "FINAL_CLEANUP_COMMANDS.txt"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "Removed: $file" -ForegroundColor Green
    }
}

# Step 2: Replace README
if (Test-Path "README_NEW.md") {
    Remove-Item "README.md" -Force -ErrorAction SilentlyContinue
    Move-Item "README_NEW.md" "README.md" -Force
    Write-Host "Updated README.md" -ForegroundColor Green
}

# Step 3: Move docs
$docsToMove = @("ARCHITECTURE.md", "DEPLOYMENT_GUIDE.md", "QUICK_REFERENCE.md", "HOW_IT_WORKS.md", "TROUBLESHOOTING.md")
foreach ($doc in $docsToMove) {
    if (Test-Path $doc) {
        Move-Item $doc "docs/" -Force -ErrorAction SilentlyContinue
        Write-Host "Moved: $doc to docs/" -ForegroundColor Green
    }
}

# Step 4: Git operations
Write-Host "`nPushing to GitHub..." -ForegroundColor Cyan
git add .
git commit -m "Reorganize project structure - Add Flutter integration and API docs"
git push origin main

Write-Host "`nDone! Check: https://github.com/vaishal-coder/Cloud-Native-Energy-Analytics-System" -ForegroundColor Green
