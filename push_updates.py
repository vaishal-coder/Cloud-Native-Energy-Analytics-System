#!/usr/bin/env python3
"""Push updates to GitHub"""
import subprocess
import sys

def run_command(cmd):
    """Run shell command"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    print("=" * 80)
    print("PUSHING UPDATES TO GITHUB")
    print("=" * 80)
    print()
    
    # Add all files
    print("Adding files...")
    if not run_command("git add -A"):
        sys.exit(1)
    
    # Commit
    print("\nCommitting changes...")
    commit_msg = "Add professional README, LICENSE, and complete documentation structure"
    if not run_command(f'git commit -m "{commit_msg}"'):
        print("Nothing to commit or commit failed")
    
    # Push
    print("\nPushing to GitHub...")
    if not run_command("git push origin main"):
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✓ SUCCESS! Repository updated")
    print("=" * 80)
    print("\nView at: https://github.com/vaishal-coder/Cloud-Native-Energy-Analytics-System")
    print()

if __name__ == "__main__":
    main()
