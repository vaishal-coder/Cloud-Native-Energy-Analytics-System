# Deployment Guide

Complete guide to deploying the Energy Analytics System on AWS.

## Prerequisites

- AWS Account with appropriate permissions
- Python 3.9 or higher
- AWS CLI configured with credentials
- boto3 library installed

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Deploy infrastructure
python infrastructure/deploy.py

# Generate test data
python data/generate_data.py

# Test the pipeline
python scripts/test_pipeline.py
```

## Detailed Deployment Steps

### 1. Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### 2. Deploy Infrastructure

```bash
python infrastructure/deploy.py
```

This creates:
- S3 bucket for data storage
- Lambda function for processing
- IAM role with necessary permissions
- Athena database for analytics

### 3. Verify Deployment

```bash
python scripts/check_aws_setup.py
```

### 4. Test the Pipeline

```bash
python scripts/test_pipeline.py
```

### 5. View Results

```bash
python scripts/check_results.py
```

## Configuration

Edit `config/config.py` to customize:
- AWS region
- Appliance types
- Anomaly detection thresholds
- Forecast parameters

## Cost Estimation

- S3 Storage: ~$0.002/month for 100MB
- Lambda Compute: ~$0.02/month for 100 executions
- Athena Queries: ~$0.001 per query
- CloudWatch Logs: ~$0.01/month

**Total**: ~$4/month for 100 uploads

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Monitoring

View Lambda logs:
```bash
aws logs tail /aws/lambda/energy-pipeline --follow
```

## Cleanup

To remove all AWS resources:
```bash
python scripts/cleanup.py
```

