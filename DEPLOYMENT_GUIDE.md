# Energy Analytics System - Deployment Guide

## Prerequisites

### 1. AWS Account Setup
- Active AWS account with admin access
- AWS CLI installed and configured
- Valid AWS credentials with permissions for:
  - S3 (create buckets, upload objects)
  - Lambda (create functions, manage code)
  - IAM (create roles, attach policies)
  - Athena (create databases, tables)
  - Glue (catalog management)
  - CloudWatch (logs)

### 2. Local Environment
```bash
# Python 3.9 or higher
python --version

# AWS CLI
aws --version

# Configure AWS credentials
aws configure
```

### 3. Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start Deployment

### Step 1: Clone and Setup
```bash
cd energy-analytics-system
pip install -r requirements.txt
```

### Step 2: Configure (Optional)
Edit `config/config.py` to customize:
- AWS region
- Lambda memory/timeout
- Forecast parameters
- Anomaly detection threshold

### Step 3: Deploy Infrastructure
```bash
python infrastructure/deploy.py
```

This will automatically:
- Create S3 bucket with folder structure
- Create IAM role with least-privilege policies
- Deploy Lambda function
- Configure S3 trigger
- Setup Athena database and tables

**Expected Output:**
```
======================================================================
ENERGY ANALYTICS SYSTEM - AUTOMATED DEPLOYMENT
======================================================================

Step 1: Creating S3 Bucket and Folder Structure
----------------------------------------------------------------------
✓ Created S3 bucket: energy-analytics-abc12345
  ✓ Created folder: raw/
  ✓ Created folder: processed/
  ✓ Created folder: forecast/
  ✓ Created folder: anomalies/
  ✓ Created folder: reports/
  ✓ Created folder: athena-results/

Step 2: Creating IAM Role and Policies
----------------------------------------------------------------------
✓ Created IAM role: energy-lambda-role
  ✓ Attached S3 policy
  ✓ Attached Athena policy
  ✓ Attached CloudWatch Logs policy
Role ARN: arn:aws:iam::123456789012:role/energy-lambda-role

Step 3: Creating Lambda Function
----------------------------------------------------------------------
✓ Created Lambda function: energy-pipeline
Lambda ARN: arn:aws:lambda:us-east-1:123456789012:function:energy-pipeline

Step 4: Configuring S3 Trigger
----------------------------------------------------------------------
✓ Added Lambda invoke permission for S3
✓ Configured S3 trigger for Lambda

Step 5: Setting up Athena Database and Tables
----------------------------------------------------------------------
✓ Created Athena database: energy_db
  ✓ Created raw_energy_data table
  ✓ Created processed_energy_data table
  ✓ Created forecast_data table

======================================================================
DEPLOYMENT COMPLETED SUCCESSFULLY
======================================================================
```

### Step 4: Generate Test Data
```bash
python data/generate_data.py
```

**Output:**
```
✓ Generated dataset: data/output/energy_data.csv
  Records: 2880
  Date range: 2026-01-21 00:00:00 to 2026-02-19 23:00:00

Sample data:
              timestamp     appliance   kwh
0  2026-01-21 00:00:00            AC  0.892
1  2026-01-21 00:00:00  Refrigerator  0.067
...
```

### Step 5: Upload Data and Trigger Pipeline
```bash
python scripts/upload_data.py data/output/energy_data.csv
```

**Output:**
```
Uploading data/output/energy_data.csv to s3://energy-analytics-abc12345/raw/energy_data_1708473600.csv
✓ Upload successful!
✓ Lambda function will be triggered automatically

Monitor execution:
  aws logs tail /aws/lambda/energy-pipeline --follow

Check results:
  aws s3 ls s3://energy-analytics-abc12345/reports/
```

### Step 6: Monitor Execution
```bash
# Watch Lambda logs in real-time
aws logs tail /aws/lambda/energy-pipeline --follow

# Or check results after 30 seconds
python scripts/check_results.py
```

## Detailed Deployment Steps

### Manual AWS Console Deployment (Alternative)

If you prefer using AWS Console:

#### 1. Create S3 Bucket
1. Go to S3 Console
2. Click "Create bucket"
3. Name: `energy-analytics-<unique-id>`
4. Region: Choose your region
5. Keep default settings
6. Create folders: raw/, processed/, forecast/, anomalies/, reports/, athena-results/

#### 2. Create IAM Role
1. Go to IAM Console → Roles
2. Click "Create role"
3. Select "Lambda" as trusted entity
4. Attach policies:
   - AWSLambdaBasicExecutionRole (AWS managed)
   - Create custom inline policies (see `infrastructure/iam_policies.py`)
5. Name: `energy-lambda-role`

#### 3. Create Lambda Function
1. Go to Lambda Console
2. Click "Create function"
3. Name: `energy-pipeline`
4. Runtime: Python 3.9
5. Role: Select `energy-lambda-role`
6. Create function
7. Upload deployment package:
   ```bash
   cd lambda
   zip -r ../lambda_package.zip .
   cd ..
   ```
8. Upload zip file
9. Configure:
   - Memory: 3008 MB
   - Timeout: 900 seconds
   - Environment variables:
     - BUCKET_NAME: your-bucket-name
     - ATHENA_DATABASE: energy_db
     - AWS_REGION: your-region

#### 4. Configure S3 Trigger
1. In Lambda function, click "Add trigger"
2. Select S3
3. Bucket: your-bucket-name
4. Event type: All object create events
5. Prefix: raw/
6. Suffix: .csv
7. Add trigger

#### 5. Setup Athena
1. Go to Athena Console
2. Set query result location: s3://your-bucket/athena-results/
3. Run DDL statements from `infrastructure/aws_setup.py` → `setup_athena()`

## Configuration Options

### Environment Variables

Set in Lambda function configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| BUCKET_NAME | S3 bucket name | (required) |
| ATHENA_DATABASE | Athena database name | energy_db |
| AWS_REGION | AWS region | us-east-1 |
| OPENAI_API_KEY | OpenAI API key (optional) | (empty) |
| USE_BEDROCK | Use AWS Bedrock for GenAI | false |

### Lambda Configuration

Edit `config/config.py`:

```python
# Lambda settings
LAMBDA_RUNTIME = 'python3.9'
LAMBDA_TIMEOUT = 900  # seconds (15 minutes)
LAMBDA_MEMORY = 3008  # MB

# ML settings
FORECAST_DAYS = 7
ANOMALY_THRESHOLD_SIGMA = 2

# Data generation
DATA_DAYS = 30
APPLIANCES = ['AC', 'Refrigerator', 'Heater', 'Washing Machine']
```

## Testing the Pipeline

### Test 1: Basic Pipeline Test
```bash
python tests/test_pipeline.py
```

This will:
1. Generate test data
2. Upload to S3
3. Wait for Lambda execution
4. Verify outputs in all folders
5. Display generated report

### Test 2: Manual Upload Test
```bash
# Generate data
python data/generate_data.py

# Upload to S3
aws s3 cp data/output/energy_data.csv s3://your-bucket-name/raw/

# Monitor logs
aws logs tail /aws/lambda/energy-pipeline --follow

# Check results after 30 seconds
aws s3 ls s3://your-bucket-name/reports/
```

### Test 3: Athena Query Test
```bash
# Using AWS CLI
aws athena start-query-execution \
  --query-string "SELECT * FROM energy_db.processed_energy_data LIMIT 10" \
  --result-configuration "OutputLocation=s3://your-bucket-name/athena-results/"

# Or use Athena Console
```

## Verification Checklist

After deployment, verify:

- [ ] S3 bucket created with all folders
- [ ] IAM role exists with correct policies
- [ ] Lambda function deployed successfully
- [ ] S3 trigger configured
- [ ] Athena database and tables created
- [ ] Test data generated
- [ ] Pipeline executes without errors
- [ ] Outputs appear in all folders:
  - [ ] processed/
  - [ ] forecast/
  - [ ] anomalies/
  - [ ] reports/
- [ ] CloudWatch logs show successful execution
- [ ] Athena queries return data

## Troubleshooting

### Issue: Lambda Timeout
**Symptoms:** Lambda execution exceeds 15 minutes

**Solutions:**
1. Increase timeout in `config.py`
2. Reduce data size
3. Optimize processing code
4. Consider AWS Glue for large datasets

### Issue: IAM Permission Denied
**Symptoms:** AccessDenied errors in Lambda logs

**Solutions:**
1. Verify IAM role policies
2. Check S3 bucket permissions
3. Wait 10-15 seconds for IAM propagation
4. Redeploy Lambda function

### Issue: S3 Trigger Not Working
**Symptoms:** Lambda not invoked on file upload

**Solutions:**
1. Verify trigger configuration in Lambda console
2. Check file uploaded to `raw/` folder
3. Ensure file has `.csv` extension
4. Check Lambda permissions for S3 invocation
5. Review CloudWatch logs for errors

### Issue: Athena Query Failures
**Symptoms:** Athena queries return errors

**Solutions:**
1. Verify table schemas match data format
2. Check CSV files have headers
3. Ensure S3 paths are correct
4. Run `MSCK REPAIR TABLE` if using partitions
5. Check query result location is set

### Issue: No Forecast Generated
**Symptoms:** forecast/ folder is empty

**Solutions:**
1. Check if Prophet is installed (Lambda layer needed)
2. Verify sufficient data points (minimum 2 days)
3. Check Lambda logs for errors
4. Fallback to simple moving average should work

### Issue: GenAI Reports Empty
**Symptoms:** Reports generated but no AI insights

**Solutions:**
1. Check if OpenAI API key is set (optional)
2. Verify AWS Bedrock is enabled (optional)
3. Rule-based fallback should always work
4. Check Lambda logs for GenAI errors

## Monitoring and Maintenance

### CloudWatch Logs
```bash
# Tail logs
aws logs tail /aws/lambda/energy-pipeline --follow

# Filter errors
aws logs filter-pattern /aws/lambda/energy-pipeline --pattern "ERROR"

# Get specific time range
aws logs tail /aws/lambda/energy-pipeline --since 1h
```

### S3 Monitoring
```bash
# List recent uploads
aws s3 ls s3://your-bucket-name/raw/ --recursive --human-readable

# Check bucket size
aws s3 ls s3://your-bucket-name --recursive --summarize

# Download latest report
aws s3 cp s3://your-bucket-name/reports/ . --recursive --exclude "*" --include "final_report_*.txt"
```

### Lambda Metrics
```bash
# Get invocation count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=energy-pipeline \
  --start-time 2026-02-20T00:00:00Z \
  --end-time 2026-02-20T23:59:59Z \
  --period 3600 \
  --statistics Sum

# Get error count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=energy-pipeline \
  --start-time 2026-02-20T00:00:00Z \
  --end-time 2026-02-20T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## Cleanup

To remove all resources:

```bash
# Delete S3 bucket (including all objects)
aws s3 rb s3://your-bucket-name --force

# Delete Lambda function
aws lambda delete-function --function-name energy-pipeline

# Delete IAM role (detach policies first)
aws iam delete-role-policy --role-name energy-lambda-role --policy-name S3Access
aws iam delete-role-policy --role-name energy-lambda-role --policy-name AthenaAccess
aws iam delete-role-policy --role-name energy-lambda-role --policy-name CloudWatchLogs
aws iam delete-role --role-name energy-lambda-role

# Delete Athena database
aws athena start-query-execution \
  --query-string "DROP DATABASE IF EXISTS energy_db CASCADE" \
  --result-configuration "OutputLocation=s3://your-bucket-name/athena-results/"
```

## Next Steps

After successful deployment:

1. **Integrate with Real Data Sources**
   - Connect to IoT devices
   - Import utility company data
   - Setup automated data pipelines

2. **Enhance Analytics**
   - Add custom metrics
   - Implement advanced ML models
   - Create interactive dashboards

3. **Setup Alerting**
   - SNS notifications for anomalies
   - Email reports
   - Slack integration

4. **Scale the System**
   - Add EMR for big data processing
   - Implement real-time streaming
   - Deploy multi-region setup

5. **Build User Interface**
   - Web dashboard with React
   - Mobile app
   - API layer with API Gateway

## Support

For issues or questions:
- Check CloudWatch logs first
- Review ARCHITECTURE.md for system details
- Verify all prerequisites are met
- Ensure AWS credentials are valid
