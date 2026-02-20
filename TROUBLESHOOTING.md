# Troubleshooting Guide

Complete guide to fixing common issues with the Energy Analytics System.

---

## Quick Diagnostics

Run these commands to check system status:

```bash
# 1. Check if Lambda exists
aws lambda get-function --function-name energy-pipeline

# 2. Check S3 bucket
aws s3 ls s3://energy-analytics-6uuv1acp/

# 3. Check recent Lambda executions
aws logs tail /aws/lambda/energy-pipeline --since 10m

# 4. Check results
python scripts/check_results.py

# 5. Test Lambda manually
python scripts/invoke_lambda_manually.py
```

---

## Common Issues and Fixes

### Issue 1: Lambda Not Triggered

**Symptoms**:
- Files uploaded to S3
- No outputs generated
- No Lambda logs

**Diagnosis**:
```bash
# Check S3 trigger configuration
aws s3api get-bucket-notification-configuration --bucket energy-analytics-6uuv1acp
```

**Fix**:
1. Go to AWS Console → S3
2. Open bucket `energy-analytics-6uuv1acp`
3. Click Properties → Event notifications
4. Delete any existing notifications
5. Create new notification:
   - Name: `energy-pipeline-trigger`
   - Events: All object create events
   - Prefix: `raw/`
   - Suffix: `.csv`
   - Destination: Lambda function `energy-pipeline`

**Or use script**:
```bash
python scripts/fix_s3_trigger.py
```

---

### Issue 2: Wrong Bucket Name

**Symptoms**:
```
Error: User is not authorized to perform: s3:PutObject on resource: 
"arn:aws:s3:::energy-analytics-uen7uora/..."
```

**Cause**: Lambda has wrong bucket name in environment variable

**Fix**:
```bash
python scripts/fix_lambda_env.py
```

**Or manually**:
```bash
aws lambda update-function-configuration \
  --function-name energy-pipeline \
  --environment Variables={BUCKET_NAME=energy-analytics-6uuv1acp}
```

---

### Issue 3: IAM Permission Errors

**Symptoms**:
```
Error: User is not authorized to perform: s3:GetObject
```

**Cause**: IAM role missing permissions

**Fix**:
```bash
# Check current role
aws iam get-role --role-name energy-lambda-role

# Redeploy to fix permissions
python infrastructure/deploy.py
```

---

### Issue 4: Lambda Timeout

**Symptoms**:
```
Task timed out after 900.00 seconds
```

**Cause**: Processing takes too long

**Fix**:
1. Check file size (should be < 10 MB)
2. Increase timeout in `config/config.py`:
   ```python
   LAMBDA_TIMEOUT = 900  # Increase if needed
   ```
3. Redeploy:
   ```bash
   python infrastructure/deploy.py
   ```

---

### Issue 5: Module Not Found

**Symptoms**:
```
ModuleNotFoundError: No module named 'pandas'
```

**Cause**: Lambda missing dependencies

**Fix**: Already fixed - we use simplified Lambda without external dependencies

**If you need pandas/prophet**:
1. Create Lambda layer with dependencies
2. Attach layer to function
3. See `scripts/create_lambda_layer.sh`

---

### Issue 6: AWS Credentials Not Configured

**Symptoms**:
```
Error: Unable to locate credentials
```

**Fix**:
```bash
aws configure
# Enter AWS Access Key ID
# Enter AWS Secret Access Key
# Enter region: us-east-1
# Enter output format: json
```

**Verify**:
```bash
aws sts get-caller-identity
```

---

### Issue 7: No Outputs Generated

**Symptoms**:
- Lambda executes successfully
- No files in processed/, forecast/, reports/

**Diagnosis**:
```bash
# Check Lambda logs for errors
aws logs tail /aws/lambda/energy-pipeline --follow

# Manually invoke Lambda
python scripts/invoke_lambda_manually.py
```

**Common Causes**:
1. Wrong bucket name → Fix with `python scripts/fix_lambda_env.py`
2. IAM permissions → Redeploy with `python infrastructure/deploy.py`
3. Code error → Check CloudWatch logs

---

### Issue 8: Athena Query Fails

**Symptoms**:
```
Error: Table not found
```

**Fix**:
```bash
# Recreate Athena tables
python infrastructure/deploy.py
```

**Or manually in Athena Console**:
```sql
CREATE DATABASE IF NOT EXISTS energy_db;

CREATE EXTERNAL TABLE energy_db.raw_energy_data (
    timestamp STRING,
    appliance STRING,
    kwh DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://energy-analytics-6uuv1acp/raw/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

---

## Debugging Steps

### Step 1: Check AWS Resources Exist

```bash
# S3 bucket
aws s3 ls | grep energy-analytics

# Lambda function
aws lambda list-functions | grep energy-pipeline

# IAM role
aws iam get-role --role-name energy-lambda-role

# Athena database
aws athena list-databases --catalog-name AwsDataCatalog
```

### Step 2: Test Lambda Manually

```bash
python scripts/invoke_lambda_manually.py
```

This shows exact error if Lambda fails.

### Step 3: Check Lambda Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/energy-pipeline --follow

# Last 10 minutes
aws logs tail /aws/lambda/energy-pipeline --since 10m

# Filter for errors
aws logs filter-pattern /aws/lambda/energy-pipeline --pattern "ERROR"
```

### Step 4: Verify S3 Trigger

```bash
# Check trigger configuration
aws s3api get-bucket-notification-configuration --bucket energy-analytics-6uuv1acp

# Should show Lambda function ARN
```

### Step 5: Check IAM Permissions

```bash
# Get role policies
aws iam list-role-policies --role-name energy-lambda-role

# Get specific policy
aws iam get-role-policy --role-name energy-lambda-role --policy-name S3Access
```

---

## Error Messages Explained

### "AccessDenied"
**Meaning**: IAM role doesn't have permission  
**Fix**: Redeploy or update IAM policies

### "ResourceNotFoundException"
**Meaning**: AWS resource doesn't exist  
**Fix**: Run `python infrastructure/deploy.py`

### "InvalidParameterValueException"
**Meaning**: Invalid configuration value  
**Fix**: Check `config/config.py` settings

### "ResourceConflictException"
**Meaning**: Resource already exists or being updated  
**Fix**: Wait 10 seconds and retry

### "ThrottlingException"
**Meaning**: Too many requests to AWS API  
**Fix**: Wait and retry

---

## Performance Issues

### Slow Processing

**Check**:
```bash
# View execution time in logs
aws logs tail /aws/lambda/energy-pipeline --since 1h | grep "Duration"
```

**Optimize**:
1. Increase Lambda memory (faster CPU)
2. Reduce data size
3. Use Parquet instead of CSV

### High Costs

**Check**:
```bash
# View Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=energy-pipeline \
  --start-time 2026-02-01T00:00:00Z \
  --end-time 2026-02-28T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

**Optimize**:
1. Reduce Lambda memory if not needed
2. Use S3 Lifecycle policies
3. Compress CSV files
4. Use Parquet for Athena

---

## Getting Help

### 1. Check Documentation
- README.md - Quick start
- HOW_IT_WORKS.md - Technical details
- DEPLOYMENT_GUIDE.md - Deployment steps

### 2. Run Diagnostics
```bash
python scripts/diagnose_lambda.py
python scripts/check_aws_setup.py
```

### 3. Check Logs
```bash
aws logs tail /aws/lambda/energy-pipeline --follow
```

### 4. Test Manually
```bash
python scripts/invoke_lambda_manually.py
```

### 5. Verify Configuration
```bash
cat deployment_info.json
```

---

## Prevention

### Best Practices

1. **Always check logs after deployment**
   ```bash
   aws logs tail /aws/lambda/energy-pipeline --follow
   ```

2. **Test with small files first**
   ```bash
   python data/generate_data.py
   python scripts/test_pipeline.py
   ```

3. **Monitor costs**
   - Check AWS Cost Explorer monthly
   - Set up billing alerts

4. **Keep documentation updated**
   - Update README when changing code
   - Document any custom modifications

5. **Use version control**
   - Commit changes to Git
   - Tag releases

---

## Complete Reset

If everything is broken, start fresh:

```bash
# 1. Delete all resources
python scripts/cleanup.py

# 2. Wait 30 seconds
Start-Sleep -Seconds 30

# 3. Redeploy
python infrastructure/deploy.py

# 4. Test
python scripts/test_pipeline.py
```

---

## Contact Information

For issues not covered here:
1. Check CloudWatch logs
2. Review HOW_IT_WORKS.md
3. Test with `python scripts/invoke_lambda_manually.py`
4. Check AWS service status: https://status.aws.amazon.com/
