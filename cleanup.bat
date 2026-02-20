@echo off
echo Starting cleanup...

del /F /Q deployment_info.json 2>nul
del /F /Q report.txt 2>nul
del /F /Q NEXT_STEP.txt 2>nul
del /F /Q RUN_THIS_NOW.txt 2>nul
del /F /Q TEST_LAMBDA_NOW.txt 2>nul
del /F /Q FINAL_STEPS.txt 2>nul
del /F /Q PUSH_TO_GITHUB_NOW.txt 2>nul
del /F /Q RUN_THIS_TO_PUSH_GITHUB.txt 2>nul
del /F /Q START_HERE_FINAL.md 2>nul
del /F /Q CLEANUP_AND_PUSH.txt 2>nul
del /F /Q PUSH_COMMANDS.txt 2>nul
del /F /Q RUN_THESE_COMMANDS.txt 2>nul
del /F /Q cleanup_and_push.ps1 2>nul
del /F /Q CONGRATULATIONS.txt 2>nul
del /F /Q GITHUB_SUCCESS.md 2>nul
del /F /Q PROJECT_STRUCTURE.txt 2>nul
del /F /Q PROJECT_OVERVIEW.txt 2>nul
del /F /Q PROJECT_SUMMARY.txt 2>nul
del /F /Q DEPLOYMENT_SUMMARY.txt 2>nul
del /F /Q EXECUTION_SUMMARY.md 2>nul
del /F /Q AUTONOMOUS_EXECUTION_REPORT.md 2>nul
del /F /Q COMPLETE_DEPLOYMENT.md 2>nul
del /F /Q START_HERE.md 2>nul
del /F /Q TROUBLESHOOT_AND_FIX.md 2>nul
del /F /Q GITHUB_SETUP.md 2>nul
del /F /Q SETUP_AWS_CREDENTIALS.md 2>nul
del /F /Q EVERYTHING_YOU_NEED_TO_KNOW.md 2>nul
del /F /Q QUICK_ANSWERS.md 2>nul
del /F /Q PROJECT_COMPLETE.md 2>nul
del /F /Q DOCUMENTATION_INDEX.md 2>nul
del /F /Q CLEANUP_SCRIPT.txt 2>nul
del /F /Q FINAL_CLEANUP_COMMANDS.txt 2>nul

echo Updating README...
del /F /Q README.md 2>nul
move /Y README_NEW.md README.md 2>nul

echo Moving docs...
move /Y ARCHITECTURE.md docs\ 2>nul
move /Y DEPLOYMENT_GUIDE.md docs\ 2>nul
move /Y QUICK_REFERENCE.md docs\ 2>nul
move /Y HOW_IT_WORKS.md docs\ 2>nul
move /Y TROUBLESHOOTING.md docs\ 2>nul

echo Pushing to GitHub...
git add .
git commit -m "Reorganize project structure - Add Flutter integration and API docs"
git push origin main

echo Done!
echo Check: https://github.com/vaishal-coder/Cloud-Native-Energy-Analytics-System
pause
