#!/bin/bash
echo "Starting cleanup..."

# Remove temporary files
rm -f deployment_info.json report.txt NEXT_STEP.txt RUN_THIS_NOW.txt TEST_LAMBDA_NOW.txt
rm -f FINAL_STEPS.txt PUSH_TO_GITHUB_NOW.txt RUN_THIS_TO_PUSH_GITHUB.txt START_HERE_FINAL.md
rm -f CLEANUP_AND_PUSH.txt PUSH_COMMANDS.txt RUN_THESE_COMMANDS.txt cleanup_and_push.ps1
rm -f CONGRATULATIONS.txt GITHUB_SUCCESS.md PROJECT_STRUCTURE.txt PROJECT_OVERVIEW.txt
rm -f PROJECT_SUMMARY.txt DEPLOYMENT_SUMMARY.txt EXECUTION_SUMMARY.md
rm -f AUTONOMOUS_EXECUTION_REPORT.md COMPLETE_DEPLOYMENT.md START_HERE.md
rm -f TROUBLESHOOT_AND_FIX.md GITHUB_SETUP.md SETUP_AWS_CREDENTIALS.md
rm -f EVERYTHING_YOU_NEED_TO_KNOW.md QUICK_ANSWERS.md PROJECT_COMPLETE.md
rm -f DOCUMENTATION_INDEX.md CLEANUP_SCRIPT.txt FINAL_CLEANUP_COMMANDS.txt

echo "Updating README..."
rm -f README.md
mv README_NEW.md README.md

echo "Moving docs..."
mv -f ARCHITECTURE.md docs/ 2>/dev/null
mv -f DEPLOYMENT_GUIDE.md docs/ 2>/dev/null
mv -f QUICK_REFERENCE.md docs/ 2>/dev/null
mv -f HOW_IT_WORKS.md docs/ 2>/dev/null
mv -f TROUBLESHOOTING.md docs/ 2>/dev/null

echo "Pushing to GitHub..."
git add .
git commit -m "Reorganize project structure - Add Flutter integration and API docs"
git push origin main

echo "Done!"
echo "Check: https://github.com/vaishal-coder/Cloud-Native-Energy-Analytics-System"
