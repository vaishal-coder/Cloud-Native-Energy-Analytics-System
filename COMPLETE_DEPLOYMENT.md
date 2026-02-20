# Complete the Deployment

## Current Status

✅ AWS Infrastructure deployed  
✅ S3 bucket created  
✅ IAM role created  
✅ Lambda function created  
✅ Athena database setup  
✅ Test data generated  
✅ Data uploaded to S3  
⚠️ Lambda not executing (missing dependencies)

---

## Issue

The Lambda function needs Python packages (pandas, prophet) which aren't available in the basic Lambda environment.

---

## Solution (2 Options)

### Option 1: Use Simplified Lambda (Recommended - 30 seconds)

This version works without external dependencies:

```powershell
python scripts/fix_lambda_dependencies.py
```

This will:
- Update Lambda with a simplified version
- Process data without pandas/prophet
- Use simple moving average for forecasts
- Generate all required outputs

Then test:
```powershell
aws s3 cp data/output/energy_data.csv s3://energy-analytics-6uuv1acp/raw/test_$(Get-Date -Format 'yyyyMMddHHmmss').csv
```

Wait 15 seconds and check:
```powershell
python scripts/check_results.py
```

---

### Option 2: Add Lambda Layer with Dependencies (Advanced - 10 minutes)

If you want the full Prophet ML forecasting:

1. **Create Lambda Layer** (on Linux/Mac or AWS CloudShell):
   ```bash
   mkdir -p lambda-layer/python
   pip install pandas numpy prophet pyarrow -t lambda-layer/python/
   cd lambda-layer
   zip -r ../lambda-layer.zip .
   ```

2. **Upload Layer**:
   ```bash
   aws lambda publish-layer-version \
     --layer-name energy-analytics-deps \
     --zip-file fileb://lambda-layer.zip \
     --compatible-runtimes python3.9 python3.11
   ```

3. **Attach to Lambda**:
   ```bash
   aws lambda update-function-configuration \
     --function-name energy-pipeline \
     --layers arn:aws:lambda:us-east-1:YOUR_ACCOUNT:layer:energy-analytics-deps:1
   ```

---

## Quick Commands

### Diagnose Current Issue
```powershell
python scripts/diagnose_lambda.py
```

### Fix Lambda (Simplified Version)
```powershell
python scripts/fix_lambda_dependencies.py
```

### Upload Test Data
```powershell
aws s3 cp data/output/energy_data.csv s3://energy-analytics-6uuv1acp/raw/test_$(Get-Date -Format 'yyyyMMddHHmmss').csv
```

### Check Results
```powershell
# Wait 15 seconds after upload
python scripts/check_results.py
```

### View Lambda Logs
```powershell
aws logs tail /aws/lambda/energy-pipeline --follow
```

### Download Latest Report
```powershell
aws s3 ls s3://energy-analytics-6uuv1acp/reports/
aws s3 cp s3://energy-analytics-6uuv1acp/reports/final_report_XXXXXX.txt .
```

---

## Expected Results

After fixing Lambda and uploading data, you should see:

```
processed/
  ✓ aggregated_YYYYMMDD_HHMMSS.csv

forecast/
  ✓ forecast_YYYYMMDD_HHMMSS.csv

anomalies/
  ✓ anomalies_YYYYMMDD_HHMMSS.csv (if anomalies detected)

reports/
  ✓ final_report_YYYYMMDD_HHMMSS.txt
```

---

## Verification Steps

1. **Check Lambda executed**:
   ```powershell
   aws logs tail /aws/lambda/energy-pipeline --since 5m
   ```

2. **Check outputs**:
   ```powershell
   python scripts/check_results.py
   ```

3. **View report**:
   ```powershell
   aws s3 ls s3://energy-analytics-6uuv1acp/reports/
   # Copy the latest report filename
   aws s3 cp s3://energy-analytics-6uuv1acp/reports/final_report_XXXXXX.txt - | more
   ```

4. **Query with Athena**:
   ```powershell
   python scripts/query_athena.py
   ```

---

## Troubleshooting

### Lambda Still Not Working?

1. **Check logs**:
   ```powershell
   aws logs tail /aws/lambda/energy-pipeline --follow
   ```

2. **Verify S3 trigger**:
   - Go to AWS Console → S3
   - Open bucket: energy-analytics-6uuv1acp
   - Properties → Event notifications
   - Should see Lambda trigger for raw/*.csv

3. **Manual trigger test**:
   ```powershell
   aws lambda invoke \
     --function-name energy-pipeline \
     --payload '{"Records":[{"s3":{"bucket":{"name":"energy-analytics-6uuv1acp"},"object":{"key":"raw/energy_data.csv"}}}]}' \
     response.json
   ```

### No Outputs Generated?

- Check Lambda timeout (should be 900 seconds)
- Check Lambda memory (should be 3008 MB)
- Check IAM permissions
- Review CloudWatch logs for errors

---

## Success Indicators

✅ Lambda logs show "Pipeline completed successfully"  
✅ Files appear in processed/, forecast/, reports/ folders  
✅ Report contains analysis and recommendations  
✅ Athena queries return data  
✅ No errors in CloudWatch logs  

---

## Next Steps After Completion

1. **Review the generated report**
2. **Run Athena queries** for analysis
3. **Upload real energy data** (same CSV format)
4. **Set up scheduled uploads** for automation
5. **Create dashboards** with QuickSight (optional)

---

## Quick Reference

| Task | Command |
|------|---------|
| Fix Lambda | `python scripts/fix_lambda_dependencies.py` |
| Upload data | `aws s3 cp data/output/energy_data.csv s3://energy-analytics-6uuv1acp/raw/` |
| Check results | `python scripts/check_results.py` |
| View logs | `aws logs tail /aws/lambda/energy-pipeline --follow` |
| Diagnose | `python scripts/diagnose_lambda.py` |
| Query data | `python scripts/query_athena.py` |

---

**Recommended**: Run `python scripts/fix_lambda_dependencies.py` now to complete the deployment!
