"""Script to run Athena queries"""
import sys
import os
import json
import boto3
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import AWS_REGION

def load_deployment_info():
    """Load deployment information"""
    deployment_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'deployment_info.json'
    )
    
    if not os.path.exists(deployment_file):
        print("Error: deployment_info.json not found. Please run deploy.py first.")
        sys.exit(1)
    
    with open(deployment_file, 'r') as f:
        return json.load(f)

def execute_query(athena_client, query, database, output_location):
    """Execute Athena query and return results"""
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database},
        ResultConfiguration={'OutputLocation': output_location}
    )
    
    query_execution_id = response['QueryExecutionId']
    
    # Wait for query to complete
    max_attempts = 30
    for _ in range(max_attempts):
        query_status = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        status = query_status['QueryExecution']['Status']['State']
        
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(1)
    
    if status != 'SUCCEEDED':
        error = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
        return None, f"Query failed: {error}"
    
    # Get results
    results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
    return results, None

def format_results(results):
    """Format Athena results for display"""
    if not results or 'ResultSet' not in results:
        return "No results"
    
    rows = results['ResultSet']['Rows']
    if not rows:
        return "No data"
    
    # Extract headers
    headers = [col['VarCharValue'] for col in rows[0]['Data']]
    
    # Extract data
    data_rows = []
    for row in rows[1:]:
        data_rows.append([col.get('VarCharValue', '') for col in row['Data']])
    
    # Format as table
    col_widths = [max(len(str(row[i])) for row in [headers] + data_rows) for i in range(len(headers))]
    
    output = []
    
    # Header
    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
    output.append(header_line)
    output.append("-" * len(header_line))
    
    # Data
    for row in data_rows:
        output.append(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))))
    
    return "\n".join(output)

def main():
    """Run sample Athena queries"""
    print("="*70)
    print("ATHENA QUERY TOOL")
    print("="*70)
    print()
    
    deployment_info = load_deployment_info()
    bucket_name = deployment_info['bucket_name']
    database = deployment_info['athena_database']
    
    athena_client = boto3.client('athena', region_name=AWS_REGION)
    output_location = f"s3://{bucket_name}/athena-results/"
    
    queries = {
        "1": {
            "name": "Total consumption by appliance",
            "query": f"SELECT appliance, SUM(kwh) as total_kwh FROM {database}.raw_energy_data GROUP BY appliance ORDER BY total_kwh DESC"
        },
        "2": {
            "name": "Peak hours analysis",
            "query": f"SELECT CAST(SUBSTR(timestamp, 12, 2) AS INTEGER) as hour, SUM(kwh) as total_kwh FROM {database}.raw_energy_data GROUP BY CAST(SUBSTR(timestamp, 12, 2) AS INTEGER) ORDER BY total_kwh DESC LIMIT 10"
        },
        "3": {
            "name": "Latest processed data",
            "query": f"SELECT * FROM {database}.processed_energy_data LIMIT 10"
        },
        "4": {
            "name": "Latest forecast",
            "query": f"SELECT * FROM {database}.forecast_data ORDER BY ds DESC LIMIT 7"
        },
        "5": {
            "name": "Daily consumption trend",
            "query": f"SELECT SUBSTR(timestamp, 1, 10) as date, SUM(kwh) as daily_total FROM {database}.raw_energy_data GROUP BY SUBSTR(timestamp, 1, 10) ORDER BY date DESC LIMIT 10"
        }
    }
    
    print("Available Queries:")
    print("-"*70)
    for key, query_info in queries.items():
        print(f"{key}. {query_info['name']}")
    print("6. Custom query")
    print("0. Exit")
    print()
    
    while True:
        choice = input("Select query (0-6): ").strip()
        
        if choice == '0':
            break
        
        if choice == '6':
            custom_query = input("Enter SQL query: ").strip()
            if not custom_query:
                continue
            query = custom_query
            query_name = "Custom query"
        elif choice in queries:
            query = queries[choice]['query']
            query_name = queries[choice]['name']
        else:
            print("Invalid choice")
            continue
        
        print()
        print(f"Executing: {query_name}")
        print("-"*70)
        print(f"Query: {query}")
        print()
        
        results, error = execute_query(athena_client, query, database, output_location)
        
        if error:
            print(f"Error: {error}")
        else:
            print(format_results(results))
        
        print()
        print("="*70)
        print()

if __name__ == '__main__':
    main()
