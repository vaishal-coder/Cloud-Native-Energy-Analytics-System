# GitHub Setup Guide

How to push this project to GitHub.

---

## Prerequisites

1. **GitHub Account**: Create at https://github.com/signup
2. **Git Installed**: Check with `git --version`
3. **GitHub CLI** (optional): Install from https://cli.github.com/

---

## Option 1: Using GitHub CLI (Easiest)

### Step 1: Install GitHub CLI

```powershell
# Windows (using winget)
winget install GitHub.cli

# Or download from https://cli.github.com/
```

### Step 2: Login to GitHub

```powershell
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Select: Login with a web browser
# Follow the prompts
```

### Step 3: Create Repository and Push

```powershell
# Navigate to project
cd D:\energy\energy-analytics-system

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Energy Analytics System"

# Create GitHub repo and push
gh repo create energy-analytics-system --public --source=. --push

# Or for private repo
gh repo create energy-analytics-system --private --source=. --push
```

**Done!** Your repo is now at: `https://github.com/YOUR_USERNAME/energy-analytics-system`

---

## Option 2: Using Git Commands (Manual)

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `energy-analytics-system`
3. Description: `Serverless AWS energy analytics platform with ML forecasting`
4. Choose Public or Private
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Initialize Git Locally

```powershell
cd D:\energy\energy-analytics-system

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Energy Analytics System"
```

### Step 3: Connect to GitHub

```powershell
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/energy-analytics-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Enter Credentials

When prompted:
- Username: Your GitHub username
- Password: Use Personal Access Token (not your password)

**To create Personal Access Token**:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Click "Generate token"
5. Copy token and use as password

---

## Option 3: Using GitHub Desktop (GUI)

### Step 1: Install GitHub Desktop

Download from: https://desktop.github.com/

### Step 2: Sign In

1. Open GitHub Desktop
2. File → Options → Accounts
3. Sign in to GitHub.com

### Step 3: Add Repository

1. File → Add local repository
2. Choose: `D:\energy\energy-analytics-system`
3. Click "Add repository"

### Step 4: Publish to GitHub

1. Click "Publish repository"
2. Name: `energy-analytics-system`
3. Description: `Serverless AWS energy analytics platform`
4. Choose Public or Private
5. Click "Publish repository"

**Done!**

---

## Verify Upload

After pushing, verify at:
```
https://github.com/YOUR_USERNAME/energy-analytics-system
```

You should see:
- ✅ All code files
- ✅ README.md displayed on homepage
- ✅ Documentation files
- ✅ Scripts and infrastructure code

---

## What Gets Uploaded

**Included** (tracked by Git):
- ✅ All Python code
- ✅ Documentation (*.md files)
- ✅ Configuration files
- ✅ Scripts
- ✅ Requirements.txt
- ✅ .gitignore

**Excluded** (in .gitignore):
- ❌ deployment_info.json (contains AWS account info)
- ❌ data/output/ (generated data files)
- ❌ *.csv files (data files)
- ❌ __pycache__/ (Python cache)
- ❌ .env files (environment variables)
- ❌ AWS credentials

---

## Repository Settings

### Add Description

1. Go to your repo on GitHub
2. Click ⚙️ (Settings) or "About" section
3. Add description: `Serverless AWS energy analytics platform with ML forecasting and anomaly detection`
4. Add topics: `aws`, `lambda`, `serverless`, `energy-analytics`, `python`, `ml`, `forecasting`

### Add README Badges

Add to top of README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20Athena-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)
```

### Enable GitHub Pages (Optional)

To host documentation:
1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main, folder: /docs
4. Save

---

## Update Repository

After making changes:

```powershell
# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

---

## Clone on Another Machine

```powershell
# Clone repository
git clone https://github.com/YOUR_USERNAME/energy-analytics-system.git

# Navigate to project
cd energy-analytics-system

# Install dependencies
pip install -r requirements.txt

# Deploy
python infrastructure/deploy.py
```

---

## Common Git Commands

```powershell
# Check status
git status

# View commit history
git log --oneline

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch
git merge feature-name

# Pull latest changes
git pull

# View remote URL
git remote -v

# Change remote URL
git remote set-url origin https://github.com/NEW_USERNAME/energy-analytics-system.git
```

---

## Troubleshooting

### Issue: "fatal: not a git repository"

**Fix**:
```powershell
git init
```

### Issue: "remote origin already exists"

**Fix**:
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/energy-analytics-system.git
```

### Issue: "failed to push some refs"

**Fix**:
```powershell
git pull origin main --rebase
git push origin main
```

### Issue: Authentication failed

**Fix**: Use Personal Access Token instead of password
1. Generate token at https://github.com/settings/tokens
2. Use token as password when prompted

---

## Security Checklist

Before pushing, verify:

- [ ] No AWS credentials in code
- [ ] No API keys in code
- [ ] deployment_info.json in .gitignore
- [ ] .env files in .gitignore
- [ ] No sensitive data in CSV files
- [ ] No personal information in code

---

## Repository Structure on GitHub

```
energy-analytics-system/
├── README.md                    ← Displayed on homepage
├── HOW_IT_WORKS.md             ← Technical documentation
├── DEPLOYMENT_GUIDE.md         ← Deployment instructions
├── TROUBLESHOOTING.md          ← Problem solving
├── ARCHITECTURE.md             ← System design
├── LICENSE                     ← MIT License
├── requirements.txt            ← Python dependencies
├── .gitignore                  ← Excluded files
├── config/                     ← Configuration
├── infrastructure/             ← AWS setup code
├── lambda/                     ← Lambda function code
├── data/                       ← Data generation
├── scripts/                    ← Utility scripts
└── tests/                      ← Test files
```

---

## Next Steps After Upload

1. **Add LICENSE file**:
   - Go to repo on GitHub
   - Click "Add file" → "Create new file"
   - Name: `LICENSE`
   - Choose template: MIT License
   - Commit

2. **Add CONTRIBUTING.md** (if accepting contributions)

3. **Add GitHub Actions** (for CI/CD)

4. **Star your own repo** ⭐

5. **Share the link**!

---

## Example Repository URL

After setup, your repo will be at:
```
https://github.com/YOUR_USERNAME/energy-analytics-system
```

Example README will show:
- Project description
- Architecture diagram
- Quick start guide
- Features list
- Documentation links

---

**Ready to push to GitHub!** 🚀

Choose Option 1 (GitHub CLI) for easiest setup.
