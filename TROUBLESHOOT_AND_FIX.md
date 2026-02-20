# Troubleshoot and Fix Lambda

## Issue: Lambda Not Being Triggered

The S3 trigger may not be configured properly. Let's fix this step by step.

---

## Solution 1: Manually Invoke Lambda (Test if Lambda Works)

```powershell
python scripts/invoke_lambda_manually.py
```

This will:
- Directly invoke Lambda with a test event
- Show you the exact error if Lambda fails
- Confirm if Lambda code is working

**If this works**, the issue is the S3 trigger configuration.  
**If this fails**, the issue is in the Lambda code itself.

---

## Solution 2: Fix S3 Trigger (Most Likely Issue)

The S3 trigger might not be configured correctly. Let's fix it manually:

### Option A: Via AWS Console (Easiest)

1. **Go to S3 Console**: https://console.aws.amazon.com/s3/
2. **Open bucket**: `energy-analytics-6uuv1acp`
3. **Go to Properties tab**
4. **Scroll to "Event notifications"**
5. **Click "Create event notification"**:
   - Name: `energy-pipeline-trigger`
   - Event types: Check "All object create events"
   - Prefix: `raw/`
   - Suffix: `.csv`
   - Destination: Lambda function
   - Lambda function: `energy-pipeline`
6. **Click "Save changes"**

### Option B: Via AWS CLI

```powershell
# Create notification configuration
$config = @"
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:085470048041:function:energy-pipeline",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {"Name": "prefix", "Value": "raw/"},
            {"Name": "suffix", "Value": ".csv"}
          ]
        }
      }
    }
  ]
}
"@

# Save to file
$config | Out-File -FilePath notification.json -Encoding utf8

# Apply configuration
aws s3api put-bucket-notification-configuration --bucket energy-analytics-6uuv1acp --notification-configuration file://notification.json
```

---

## Solution 3: Test After Fixing Trigger

After configuring the S3 trigger:

```powershell
# Upload a new test file
aws s3 cp data/output/energy_data.csv s3://energy-analytics-6uuv1acp/raw/test_$(Get-Date -Format 'yyyyMMddHHmmss').csv

# Wait 15 seconds
Start-Sleep -Seconds 15

# Check results
python scripts/check_results.py
```

---

## Solution 4: Check Lambda Logs

```powershell
# View recent logs
aws logs tail /aws/lambda/energy-pipeline --since 10m

# Or follow logs in real-time
aws logs tail /aws/lambda/energy-pipeline --follow
```

---

## Solution 5: Verify Lambda Permissions

Lambda needs permission to be invoked by S3:

```powershell
aws lambda get-policy --function-name energy-pipeline
```

If this fails or shows no S3 permissions, add them:

```powershell
aws lambda add-permission `
  --function-name energy-pipeline `
  --statement-id S3InvokePermission `
  --action lambda:InvokeFunction `
  --principal s3.amazonaws.com `
  --source-arn arn:aws:s3:::energy-analytics-6uuv1acp `
  --source-account 085470048041
```

---

## Quick Diagnostic Commands

```powershell
# 1. Check if Lambda exists
aws lambda get-function --function-name energy-pipeline

# 2. Check S3 trigger configuration
aws s3api get-bucket-notification-configuration --bucket energy-analytics-6uuv1acp

# 3. Check Lambda permissions
aws lambda get-policy --function-name energy-pipeline

# 4. List files in S3 raw folder
aws s3 ls s3://energy-analytics-6uuv1acp/raw/

# 5. Check CloudWatch log groups
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/energy-pipeline
```

---

## Expected Outputs

### Working S3 Trigger:
```json
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:085470048041:function:energy-pipeline",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {"Name": "prefix", "Value": "raw/"},
            {"Name": "suffix", "Value": ".csv"}
          ]
        }
      }
    }
  ]
}
```

### Working Lambda Permissions:
```json
{
  "Statement": [
    {
      "Sid": "S3InvokePermission",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:us-east-1:085470048041:function:energy-pipeline",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": "085470048041"
        },
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:s3:::energy-analytics-6uuv1acp"
        }
      }
    }
  ]
}
```

---

## Complete Fix Script

I'll create an automated fix script:

```powershell
python scripts/fix_s3_trigger.py
```

This will:
1. Check current S3 trigger configuration
2. Check Lambda permissions
3. Fix any issues automatically
4. Test the pipeline

---

## Still Not Working?

If none of the above works:

1. **Delete and recreate Lambda**:
   ```powershell
   python infrastructure/deploy.py
   ```

2. **Check IAM role permissions**:
   ```powershell
   aws iam get-role --role-name energy-lambda-role
   ```

3. **Verify S3 bucket exists**:
   ```powershell
   aws s3 ls s3://energy-analytics-6uuv1acp/
   ```

4. **Contact support** with:
   - CloudWatch logs
   - S3 trigger configuration
   - Lambda permissions
   - IAM role details

---

## Success Indicators

✅ S3 trigger shows in bucket properties  
✅ Lambda has S3 invoke permission  
✅ CloudWatch logs show Lambda executions  
✅ Files appear in processed/, forecast/, reports/ folders  
✅ No errors in CloudWatch logs  

---

## Next Steps After Fix

1. Test pipeline: `python scripts/test_pipeline.py`
2. Check results: `python scripts/check_results.py`
3. View report: `aws s3 ls s3://energy-analytics-6uuv1acp/reports/`
4. Query data: `python scripts/query_athena.py`

---

**Start with**: `python scripts/invoke_lambda_manually.py` to test if Lambda works!
