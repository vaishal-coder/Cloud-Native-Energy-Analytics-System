# AWS Credentials Setup Guide

## ⚠️ Issue Detected
```
Error: Unable to locate credentials
```

Your AWS credentials are not configured. Let's fix this!

---

## 🔑 Option 1: Configure AWS CLI (Recommended)

### Step 1: Get Your AWS Credentials

You need:
- **AWS Access Key ID** (looks like: AKIAIOSFODNN7EXAMPLE)
- **AWS Secret Access Key** (looks like: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY)

#### How to Get Credentials:

1. **Log in to AWS Console**: https://console.aws.amazon.com/
2. **Go to IAM**: Search for "IAM" in the top search bar
3. **Create Access Key**:
   - Click "Users" in left sidebar
   - Click your username (or create a new user)
   - Click "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)"
   - Check the confirmation box
   - Click "Create access key"
   - **IMPORTANT**: Download or copy both keys NOW (you can't see the secret key again!)

### Step 2: Configure AWS CLI

Open PowerShell and run:

```powershell
aws configure
```

You'll be prompted for:

```
AWS Access Key ID [None]: PASTE_YOUR_ACCESS_KEY_HERE
AWS Secret Access Key [None]: PASTE_YOUR_SECRET_KEY_HERE
Default region name [None]: us-east-1
Default output format [None]: json
```

**Example**:
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

### Step 3: Verify Configuration

```powershell
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

### Step 4: Deploy Again

```powershell
cd D:\energy\energy-analytics-system
python infrastructure/deploy.py
```

---

## 🔑 Option 2: Use Environment Variables

If you prefer not to use `aws configure`, set environment variables:

### PowerShell:
```powershell
$env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
$env:AWS_DEFAULT_REGION="us-east-1"

# Then deploy
python infrastructure/deploy.py
```

### Command Prompt:
```cmd
set AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
set AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
set AWS_DEFAULT_REGION=us-east-1

python infrastructure/deploy.py
```

---

## 🔑 Option 3: Use AWS SSO (If Your Organization Uses It)

```powershell
aws sso login --profile your-profile-name
```

Then set the profile:
```powershell
$env:AWS_PROFILE="your-profile-name"
python infrastructure/deploy.py
```

---

## 🔑 Option 4: Use AWS CloudShell (No Credentials Needed!)

This is the easiest option if you don't want to configure credentials locally:

1. **Open AWS Console**: https://console.aws.amazon.com/
2. **Click CloudShell icon** (terminal icon in top-right corner)
3. **Upload project folder**:
   - Click "Actions" → "Upload file"
   - Upload the entire `energy-analytics-system` folder as a zip
   - Or use: `git clone` if you have it in a repository

4. **Run deployment**:
   ```bash
   cd energy-analytics-system
   pip install -r requirements.txt --user
   python infrastructure/deploy.py
   ```

**Advantages**:
- ✅ No credential configuration needed
- ✅ Credentials automatically available
- ✅ Free to use
- ✅ Python pre-installed

---

## 🔒 Security Best Practices

### ✅ DO:
- Store credentials securely
- Use IAM users with minimal required permissions
- Rotate access keys regularly (every 90 days)
- Use AWS SSO when available
- Delete unused access keys

### ❌ DON'T:
- Share your secret access key
- Commit credentials to Git
- Use root account credentials
- Store credentials in plain text files
- Give full admin access unless necessary

---

## 🎯 Recommended IAM Permissions

For this project, your IAM user needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "lambda:*",
        "iam:*",
        "athena:*",
        "glue:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Or use AWS managed policy**: `AdministratorAccess` (for testing)

---

## 🧪 Test Your Credentials

After configuring, test with:

```powershell
# Test 1: Check identity
aws sts get-caller-identity

# Test 2: List S3 buckets
aws s3 ls

# Test 3: List Lambda functions
aws lambda list-functions

# If all work, you're ready to deploy!
```

---

## 🚀 Quick Deployment After Setup

Once credentials are configured:

```powershell
# Navigate to project
cd D:\energy\energy-analytics-system

# Deploy infrastructure
python infrastructure/deploy.py

# Generate test data
python data/generate_data.py

# Upload and trigger pipeline
python scripts/upload_data.py data/output/energy_data.csv

# Check results (wait 30 seconds first)
python scripts/check_results.py
```

---

## ❓ Troubleshooting

### Issue: "aws: command not found"
**Solution**: Install AWS CLI
```powershell
# Using MSI installer
# Download from: https://awscli.amazonaws.com/AWSCLIV2.msi

# Or using winget
winget install Amazon.AWSCLI
```

### Issue: "Access Denied" errors
**Solution**: Your IAM user needs more permissions. Add the policies mentioned above.

### Issue: "Region not found"
**Solution**: Specify a valid AWS region:
```powershell
aws configure set region us-east-1
```

Valid regions:
- us-east-1 (N. Virginia)
- us-west-2 (Oregon)
- eu-west-1 (Ireland)
- ap-southeast-1 (Singapore)

### Issue: Credentials work but deployment fails
**Solution**: Check CloudWatch logs for specific errors:
```powershell
aws logs tail /aws/lambda/energy-pipeline --follow
```

---

## 📞 Need More Help?

### AWS Documentation:
- **Configure AWS CLI**: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html
- **IAM Users**: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html
- **Access Keys**: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html

### Quick Links:
- **AWS Console**: https://console.aws.amazon.com/
- **IAM Console**: https://console.aws.amazon.com/iam/
- **CloudShell**: https://console.aws.amazon.com/cloudshell/

---

## ✅ Checklist

Before deploying, ensure:

- [ ] AWS account created
- [ ] IAM user created (or using root - not recommended)
- [ ] Access keys generated
- [ ] AWS CLI installed
- [ ] Credentials configured (`aws configure`)
- [ ] Credentials tested (`aws sts get-caller-identity`)
- [ ] Sufficient IAM permissions
- [ ] Region selected (us-east-1 recommended)

---

## 🎉 Ready to Deploy!

Once credentials are configured, run:

```powershell
python infrastructure/deploy.py
```

Expected output:
```
======================================================================
ENERGY ANALYTICS SYSTEM - AUTOMATED DEPLOYMENT
======================================================================

Step 1: Creating S3 Bucket and Folder Structure
----------------------------------------------------------------------
✓ Created S3 bucket: energy-analytics-abc12345
  ✓ Created folder: raw/
  ✓ Created folder: processed/
  ...

Step 2: Creating IAM Role and Policies
----------------------------------------------------------------------
✓ Created IAM role: energy-lambda-role
  ...

[Deployment continues...]
```

**Time to completion**: 30-60 seconds

---

**Next**: After successful deployment, see **START_HERE.md** for next steps!
