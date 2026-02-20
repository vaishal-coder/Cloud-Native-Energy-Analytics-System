"""Generate synthetic energy usage data"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import APPLIANCES, DATA_DAYS, HOURS_PER_DAY

def generate_energy_data():
    """Generate 30 days of hourly energy consumption data"""
    np.random.seed(42)
    
    start_date = datetime.now() - timedelta(days=DATA_DAYS)
    timestamps = []
    appliances = []
    kwh_values = []
    
    # Base consumption patterns for each appliance
    base_consumption = {
        'AC': 2.5,
        'Refrigerator': 0.15,
        'Heater': 1.8,
        'Washing Machine': 0.5
    }
    
    # Peak hour multipliers (6 PM - 9 PM)
    peak_hours = [18, 19, 20]
    
    for day in range(DATA_DAYS):
        current_date = start_date + timedelta(days=day)
        
        for hour in range(HOURS_PER_DAY):
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            
            for appliance in APPLIANCES:
                base = base_consumption[appliance]
                
                # Add hourly variation
                hourly_factor = 1.0
                
                # Peak hours (evening)
                if hour in peak_hours:
                    hourly_factor = 1.5 + np.random.uniform(0, 0.5)
                # Night hours (reduced usage)
                elif hour >= 22 or hour <= 6:
                    hourly_factor = 0.3 + np.random.uniform(0, 0.2)
                # Day hours
                else:
                    hourly_factor = 0.8 + np.random.uniform(0, 0.4)
                
                # Calculate consumption with noise
                kwh = base * hourly_factor + np.random.normal(0, 0.1)
                kwh = max(0, kwh)  # Ensure non-negative
                
                # Add occasional anomalies (5% chance)
                if np.random.random() < 0.05:
                    kwh *= np.random.uniform(2.0, 3.5)
                
                timestamps.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                appliances.append(appliance)
                kwh_values.append(round(kwh, 3))
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'appliance': appliances,
        'kwh': kwh_values
    })
    
    return df

def save_to_csv(df, filename='energy_data.csv'):
    """Save DataFrame to CSV"""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"✓ Generated dataset: {filepath}")
    print(f"  Records: {len(df)}")
    print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    return filepath

if __name__ == '__main__':
    df = generate_energy_data()
    filepath = save_to_csv(df)
    
    # Display sample
    print("\nSample data:")
    print(df.head(10))
    print("\nStatistics:")
    print(df.groupby('appliance')['kwh'].describe())
