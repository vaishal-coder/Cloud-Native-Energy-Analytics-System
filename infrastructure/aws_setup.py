"""AWS infrastructure setup and management"""
import boto3
import json
import time
import zipfile
import io
import os
from botocore.exceptions import ClientError
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import *
from infrastructure.iam_policies import *

class AWSInfrastructure:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=AWS_REGION)
        self.iam_client = boto3.client('iam', region_name=AWS_REGION)
        self.lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        self.athena_client = boto3.client('athena', region_name=AWS_REGION)
        self.glue_client = boto3.client('glue', region_name=AWS_REGION)
        self.sts_client = boto3.client('sts', region_name=AWS_REGION)
        
    def get_account_id(self):
        """Get AWS account ID"""
        return self.sts_client.get_caller_identity()['Account']
    
    def create_s3_bucket(self):
        """Create S3 bucket with folder structure"""
        try:
            if AWS_REGION == 'us-east-1':
                self.s3_client.create_bucket(Bucket=BUCKET_NAME)
            else:
                self.s3_client.create_bucket(
                    Bucket=BUCKET_NAME,
                    CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                )
            print(f"✓ Created S3 bucket: {BUCKET_NAME}")
            
            # Create folder structure
            for folder_name, folder_path in S3_FOLDERS.items():
                self.s3_client.put_object(Bucket=BUCKET_NAME, Key=folder_path)
                print(f"  ✓ Created folder: {folder_path}")
            
            return BUCKET_NAME
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print(f"✓ Bucket {BUCKET_NAME} already exists")
                return BUCKET_NAME
            else:
                raise
    
    def create_iam_role(self):
        """Create IAM role for Lambda with necessary policies"""
        try:
            # Create role
            role_response = self.iam_client.create_role(
                RoleName=IAM_ROLE_NAME,
                AssumeRolePolicyDocument=json.dumps(get_lambda_trust_policy()),
                Description='Role for Energy Analytics Lambda function'
            )
            role_arn = role_response['Role']['Arn']
            print(f"✓ Created IAM role: {IAM_ROLE_NAME}")
            
            # Wait for role to be available
            time.sleep(10)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                role_arn = self.iam_client.get_role(RoleName=IAM_ROLE_NAME)['Role']['Arn']
                print(f"✓ IAM role {IAM_ROLE_NAME} already exists")
            else:
                raise
        
        # Attach inline policies
        try:
            self.iam_client.put_role_policy(
                RoleName=IAM_ROLE_NAME,
                PolicyName='S3Access',
                PolicyDocument=json.dumps(get_s3_policy(BUCKET_NAME))
            )
            print("  ✓ Attached S3 policy")
            
            self.iam_client.put_role_policy(
                RoleName=IAM_ROLE_NAME,
                PolicyName='AthenaAccess',
                PolicyDocument=json.dumps(get_athena_policy(BUCKET_NAME))
            )
            print("  ✓ Attached Athena policy")
            
            self.iam_client.put_role_policy(
                RoleName=IAM_ROLE_NAME,
                PolicyName='CloudWatchLogs',
                PolicyDocument=json.dumps(get_cloudwatch_logs_policy())
            )
            print("  ✓ Attached CloudWatch Logs policy")
            
        except ClientError as e:
            print(f"  Note: Policies may already be attached")
        
        return role_arn
    
    def create_lambda_deployment_package(self, lambda_code_path):
        """Create Lambda deployment package with dependencies"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add lambda function code
            zip_file.write(lambda_code_path, 'lambda_function.py')
            
            # Add config
            config_path = os.path.join(os.path.dirname(os.path.dirname(lambda_code_path)), 'config', 'config.py')
            if os.path.exists(config_path):
                zip_file.write(config_path, 'config.py')
        
        return zip_buffer.getvalue()
    
    def create_lambda_function(self, role_arn, lambda_code_path):
        """Create Lambda function"""
        deployment_package = self.create_lambda_deployment_package(lambda_code_path)
        
        try:
            response = self.lambda_client.create_function(
                FunctionName=LAMBDA_FUNCTION_NAME,
                Runtime=LAMBDA_RUNTIME,
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': deployment_package},
                Timeout=LAMBDA_TIMEOUT,
                MemorySize=LAMBDA_MEMORY,
                Environment={
                    'Variables': {
                        'BUCKET_NAME': BUCKET_NAME,
                        'ATHENA_DATABASE': ATHENA_DATABASE,
                        'OPENAI_API_KEY': OPENAI_API_KEY,
                        'USE_BEDROCK': str(USE_BEDROCK)
                    }
                },
                Description='Energy analytics pipeline processor'
            )
            lambda_arn = response['FunctionArn']
            print(f"✓ Created Lambda function: {LAMBDA_FUNCTION_NAME}")
            return lambda_arn
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                # Update existing function
                self.lambda_client.update_function_code(
                    FunctionName=LAMBDA_FUNCTION_NAME,
                    ZipFile=deployment_package
                )
                response = self.lambda_client.get_function(FunctionName=LAMBDA_FUNCTION_NAME)
                lambda_arn = response['Configuration']['FunctionArn']
                print(f"✓ Updated Lambda function: {LAMBDA_FUNCTION_NAME}")
                return lambda_arn
            else:
                raise
    
    def configure_s3_trigger(self, lambda_arn):
        """Configure S3 to trigger Lambda on file upload"""
        account_id = self.get_account_id()
        
        # Add Lambda permission for S3 to invoke
        try:
            self.lambda_client.add_permission(
                FunctionName=LAMBDA_FUNCTION_NAME,
                StatementId='S3InvokePermission',
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{BUCKET_NAME}',
                SourceAccount=account_id
            )
            print("✓ Added Lambda invoke permission for S3")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                print("✓ Lambda permission already exists")
            else:
                raise
        
        # Configure S3 notification
        notification_config = {
            'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': lambda_arn,
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {'Name': 'prefix', 'Value': 'raw/'},
                                {'Name': 'suffix', 'Value': '.csv'}
                            ]
                        }
                    }
                }
            ]
        }
        
        try:
            self.s3_client.put_bucket_notification_configuration(
                Bucket=BUCKET_NAME,
                NotificationConfiguration=notification_config
            )
            print("✓ Configured S3 trigger for Lambda")
        except ClientError as e:
            print(f"Note: S3 trigger configuration: {e}")
    
    def setup_athena(self):
        """Setup Athena database and tables"""
        # Create database
        query = f"CREATE DATABASE IF NOT EXISTS {ATHENA_DATABASE}"
        self._execute_athena_query(query)
        print(f"✓ Created Athena database: {ATHENA_DATABASE}")
        
        # Create raw data table
        raw_table_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.raw_energy_data (
            timestamp STRING,
            appliance STRING,
            kwh DOUBLE
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION 's3://{BUCKET_NAME}/raw/'
        TBLPROPERTIES ('skip.header.line.count'='1')
        """
        self._execute_athena_query(raw_table_query)
        print("  ✓ Created raw_energy_data table")
        
        # Create processed data table
        processed_table_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.processed_energy_data (
            appliance STRING,
            total_kwh DOUBLE,
            avg_kwh DOUBLE,
            peak_hour INT
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION 's3://{BUCKET_NAME}/processed/'
        TBLPROPERTIES ('skip.header.line.count'='1')
        """
        self._execute_athena_query(processed_table_query)
        print("  ✓ Created processed_energy_data table")
        
        # Create forecast table
        forecast_table_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.forecast_data (
            ds STRING,
            yhat DOUBLE,
            yhat_lower DOUBLE,
            yhat_upper DOUBLE
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION 's3://{BUCKET_NAME}/forecast/'
        TBLPROPERTIES ('skip.header.line.count'='1')
        """
        self._execute_athena_query(forecast_table_query)
        print("  ✓ Created forecast_data table")
    
    def _execute_athena_query(self, query):
        """Execute Athena query and wait for completion"""
        response = self.athena_client.start_query_execution(
            QueryString=query,
            ResultConfiguration={
                'OutputLocation': f's3://{BUCKET_NAME}/{S3_FOLDERS["athena_results"]}'
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # Wait for query to complete
        max_attempts = 30
        for _ in range(max_attempts):
            query_status = self.athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            status = query_status['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            time.sleep(1)
        
        return status == 'SUCCEEDED'
