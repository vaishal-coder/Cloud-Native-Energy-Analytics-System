"""Automated GitHub repository setup and push"""
import subprocess
import sys
import os

def run_command(command, check=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stderr.strip(), e.returncode

def check_git_installed():
    """Check if git is installed"""
    output, code = run_command("git --version", check=False)
    if code != 0:
        print("❌ Git is not installed")
        print("Install from: https://git-scm.com/downloads")
        return False
    print(f"✓ Git installed: {output}")
    return True

def check_gh_cli_installed():
    """Check if GitHub CLI is installed"""
    output, code = run_command("gh --version", check=False)
    if code != 0:
        print("⚠ GitHub CLI not installed (optional)")
        print("Install from: https://cli.github.com/")
        return False
    print(f"✓ GitHub CLI installed: {output.split()[0]}")
    return True

def init_git_repo():
    """Initialize git repository"""
    output, code = run_command("git rev-parse --git-dir", check=False)
    if code == 0:
        print("✓ Git repository already initialized")
        return True
    
    print("Initializing git repository...")
    output, code = run_command("git init")
    if code == 0:
        print("✓ Git repository initialized")
        return True
    else:
        print(f"❌ Failed to initialize git: {output}")
        return False

def add_and_commit():
    """Add all files and commit"""
    print("\nAdding files to git...")
    
    # Add all files
    output, code = run_command("git add .")
    if code != 0:
        print(f"❌ Failed to add files: {output}")
        return False
    
    # Check if there are changes to commit
    output, code = run_command("git status --porcelain", check=False)
    if not output:
        print("✓ No changes to commit (already committed)")
        return True
    
    # Commit
    print("Committing files...")
    commit_message = "Initial commit: Energy Analytics System - Production-ready AWS serverless platform"
    output, code = run_command(f'git commit -m "{commit_message}"')
    if code == 0:
        print("✓ Files committed")
        return True
    else:
        print(f"❌ Failed to commit: {output}")
        return False

def push_with_gh_cli(repo_name, is_private=False):
    """Push to GitHub using GitHub CLI"""
    print("\n" + "="*70)
    print("PUSHING TO GITHUB USING GITHUB CLI")
    print("="*70)
    
    # Check if authenticated
    output, code = run_command("gh auth status", check=False)
    if code != 0:
        print("\n⚠ Not logged in to GitHub")
        print("Running: gh auth login")
        print("\nFollow the prompts to login...")
        subprocess.run("gh auth login", shell=True)
    
    # Create repo and push
    visibility = "--private" if is_private else "--public"
    command = f'gh repo create {repo_name} {visibility} --source=. --push'
    
    print(f"\nCreating repository: {repo_name}")
    print(f"Visibility: {'Private' if is_private else 'Public'}")
    
    output, code = run_command(command, check=False)
    
    if code == 0:
        print("\n" + "="*70)
        print("✓ SUCCESS! Repository created and pushed to GitHub")
        print("="*70)
        
        # Get repo URL
        url_output, _ = run_command("gh repo view --web --json url -q .url", check=False)
        if url_output:
            print(f"\nRepository URL: {url_output}")
        
        return True
    else:
        if "already exists" in output.lower():
            print("\n⚠ Repository already exists")
            print("Pushing to existing repository...")
            
            # Try to push to existing repo
            push_output, push_code = run_command("git push -u origin main", check=False)
            if push_code == 0:
                print("✓ Pushed to existing repository")
                return True
            else:
                print(f"❌ Failed to push: {push_output}")
                return False
        else:
            print(f"❌ Failed to create repository: {output}")
            return False

def push_manual(repo_name):
    """Manual push instructions"""
    print("\n" + "="*70)
    print("MANUAL GITHUB SETUP REQUIRED")
    print("="*70)
    print("\nGitHub CLI not available. Follow these steps:\n")
    print("1. Create repository on GitHub:")
    print("   - Go to: https://github.com/new")
    print(f"   - Repository name: {repo_name}")
    print("   - Description: Serverless AWS energy analytics platform")
    print("   - Choose Public or Private")
    print("   - Don't initialize with README")
    print("   - Click 'Create repository'\n")
    print("2. Connect and push:")
    print("   Run these commands:\n")
    print(f"   git remote add origin https://github.com/YOUR_USERNAME/{repo_name}.git")
    print("   git branch -M main")
    print("   git push -u origin main\n")
    print("3. Enter credentials when prompted")
    print("   - Username: Your GitHub username")
    print("   - Password: Personal Access Token (not your password)")
    print("   - Create token at: https://github.com/settings/tokens\n")
    print("="*70)

def main():
    """Main function"""
    print("="*70)
    print("GITHUB REPOSITORY SETUP")
    print("="*70)
    print()
    
    # Configuration
    repo_name = "energy-analytics-system"
    
    # Check prerequisites
    if not check_git_installed():
        sys.exit(1)
    
    gh_cli_available = check_gh_cli_installed()
    print()
    
    # Initialize git
    if not init_git_repo():
        sys.exit(1)
    
    # Add and commit
    if not add_and_commit():
        sys.exit(1)
    
    # Push to GitHub
    if gh_cli_available:
        print("\n" + "="*70)
        print("READY TO PUSH TO GITHUB")
        print("="*70)
        print(f"\nRepository name: {repo_name}")
        print("\nChoose visibility:")
        print("1. Public (anyone can see)")
        print("2. Private (only you can see)")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        is_private = (choice == "2")
        
        if push_with_gh_cli(repo_name, is_private):
            print("\n✓ All done! Your project is now on GitHub!")
            print("\nNext steps:")
            print("1. View your repository on GitHub")
            print("2. Add topics: aws, lambda, serverless, python, ml")
            print("3. Star your own repo ⭐")
            print("4. Share the link!")
        else:
            print("\n⚠ Automatic push failed")
            push_manual(repo_name)
    else:
        push_manual(repo_name)
    
    print("\n" + "="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
