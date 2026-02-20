"""Check AWS setup and credentials"""
import sys
import os

def check_aws_cli():
    """Check if AWS CLI is installed"""
    import subprocess
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        print("✓ AWS CLI installed")
        print(f"  Version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("✗ AWS CLI not installed")
        print("  Install: https://aws.amazon.com/cli/")
        return False

def check_credentials():
    """Check if AWS credentials are configured"""
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✓ AWS credentials configured")
        print(f"  Account: {identity['Account']}")
        print(f"  User ARN: {identity['Arn']}")
        return True
    except Exception as e:
        print("✗ AWS credentials not configured")
        print(f"  Error: {str(e)}")
        return False

def check_region():
    """Check if AWS region is configured"""
    try:
        import boto3
        session = boto3.session.Session()
        region = session.region_name
        if region:
            print(f"✓ AWS region configured: {region}")
            return True
        else:
            print("⚠ AWS region not configured (will use default)")
            return True
    except Exception as e:
        print(f"✗ Error checking region: {str(e)}")
        return False

def check_permissions():
    """Check basic AWS permissions"""
    try:
        import boto3
        
        # Test S3
        s3 = boto3.client('s3')
        s3.list_buckets()
        print("✓ S3 permissions OK")
        
        # Test Lambda
        lambda_client = boto3.client('lambda')
        lambda_client.list_functions(MaxItems=1)
        print("✓ Lambda permissions OK")
        
        # Test IAM
        iam = boto3.client('iam')
        iam.list_roles(MaxItems=1)
        print("✓ IAM permissions OK")
        
        return True
    except Exception as e:
        print(f"⚠ Permission check failed: {str(e)}")
        print("  You may need additional IAM permissions")
        return False

def main():
    """Run all checks"""
    print("="*70)
    print("AWS SETUP CHECKER")
    print("="*70)
    print()
    
    print("Checking AWS CLI...")
    print("-"*70)
    cli_ok = check_aws_cli()
    print()
    
    print("Checking AWS Credentials...")
    print("-"*70)
    creds_ok = check_credentials()
    print()
    
    if creds_ok:
        print("Checking AWS Region...")
        print("-"*70)
        region_ok = check_region()
        print()
        
        print("Checking AWS Permissions...")
        print("-"*70)
        perms_ok = check_permissions()
        print()
    else:
        region_ok = False
        perms_ok = False
    
    print("="*70)
    print("SUMMARY")
    print("="*70)
    
    if cli_ok and creds_ok and region_ok:
        print("✓ AWS setup is complete!")
        print()
        print("You can now deploy:")
        print("  python infrastructure/deploy.py")
    else:
        print("✗ AWS setup incomplete")
        print()
        print("Next steps:")
        if not cli_ok:
            print("  1. Install AWS CLI: https://aws.amazon.com/cli/")
        if not creds_ok:
            print("  2. Configure credentials: aws configure")
            print("     See SETUP_AWS_CREDENTIALS.md for detailed instructions")
        if not region_ok:
            print("  3. Set region: aws configure set region us-east-1")
        
        print()
        print("Quick setup:")
        print("  aws configure")
        print("  # Enter your AWS Access Key ID")
        print("  # Enter your AWS Secret Access Key")
        print("  # Enter region: us-east-1")
        print("  # Enter output format: json")
    
    print()
    print("="*70)

if __name__ == '__main__':
    main()
