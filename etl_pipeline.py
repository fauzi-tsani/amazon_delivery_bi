"""
ETL Pipeline for Amazon Delivery Data Warehouse
================================================
This script performs Extract, Transform, and Load operations
to create a Star Schema Data Warehouse.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = 'amazon_delivery.csv'
OUTPUT_DIR = 'warehouse_data'

# Create output directory if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_data(file_path):
    """
    Extract data from CSV source
    """
    print("="*60)
    print("STEP 1: EXTRACTION")
    print("="*60)
    
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Data extracted successfully from: {file_path}")
        print(f"  - Total rows: {len(df):,}")
        print(f"  - Total columns: {len(df.columns)}")
        print(f"  - Columns: {', '.join(df.columns.tolist())}")
        return df
    except Exception as e:
        print(f"✗ Error during extraction: {str(e)}")
        raise

def transform_data(df):
    """
    Transform raw data into dimensional model format
    """
    print("\n" + "="*60)
    print("STEP 2: TRANSFORMATION")
    print("="*60)
    
    df_transformed = df.copy()
    
    # 2.1 Data Quality Assessment
    print("\n[2.1] Data Quality Assessment")
    print("-" * 40)
    
    # Check for missing values
    missing = df_transformed.isnull().sum()
    print(f"  Missing values per column:")
    for col, count in missing.items():
        if count > 0:
            print(f"    - {col}: {count} ({count/len(df)*100:.2f}%)")
    
    # Check for duplicates
    duplicates = df_transformed.duplicated().sum()
    print(f"  Duplicate rows: {duplicates}")
    
    # Check for data quality issues
    print("\n  Data Quality Issues Found:")
    
    # Check for zero/null coordinates
    zero_coords = df_transformed[(df_transformed['Store_Latitude'] == 0) | 
                               (df_transformed['Store_Longitude'] == 0)]
    print(f"    - Records with zero coordinates: {len(zero_coords)}")
    
    # Check for unrealistic ratings
    invalid_ratings = df_transformed[(df_transformed['Agent_Rating'] < 1) | 
                                    (df_transformed['Agent_Rating'] > 5)]
    print(f"    - Records with invalid ratings: {len(invalid_ratings)}")
    
    # 2.2 Data Cleaning
    print("\n[2.2] Data Cleaning")
    print("-" * 40)
    
    # Handle zero coordinates - flag them
    df_transformed['Coordinate_Flag'] = 'Valid'
    df_transformed.loc[(df_transformed['Store_Latitude'] == 0) | 
                      (df_transformed['Store_Longitude'] == 0), 'Coordinate_Flag'] = 'Invalid'
    print(f"  ✓ Flagged {len(zero_coords)} records with zero coordinates")
    
    # Remove duplicates
    before_dedup = len(df_transformed)
    df_transformed = df_transformed.drop_duplicates()
    after_dedup = len(df_transformed)
    print(f"  ✓ Removed {before_dedup - after_dedup} duplicate rows")
    
    # 2.3 Data Type Conversions
    print("\n[2.3] Data Type Conversions")
    print("-" * 40)
    
    # Convert date and time columns
    df_transformed['Order_Date'] = pd.to_datetime(df_transformed['Order_Date'])
    
    # Handle time columns - some may have NaN or invalid values
    def safe_time_convert(time_val):
        if pd.isna(time_val) or str(time_val).strip() in ['NaN', 'nan', '']:
            return None
        try:
            return pd.to_datetime(time_val, format='%H:%M:%S').time()
        except:
            try:
                return pd.to_datetime(str(time_val).strip()).time()
            except:
                return None
    
    df_transformed['Order_Time'] = df_transformed['Order_Time'].apply(safe_time_convert)
    df_transformed['Pickup_Time'] = df_transformed['Pickup_Time'].apply(safe_time_convert)
    
    # Extract hour from order time for analysis
    df_transformed['Order_Hour'] = df_transformed['Order_Time'].apply(lambda x: x.hour if x else None)
    
    print("  ✓ Converted date and time columns")
    
    # Extract date components for dimension
    df_transformed['Order_Year'] = df_transformed['Order_Date'].dt.year
    df_transformed['Order_Month'] = df_transformed['Order_Date'].dt.month
    df_transformed['Order_Day'] = df_transformed['Order_Date'].dt.day
    df_transformed['Order_Weekday'] = df_transformed['Order_Date'].dt.day_name()
    df_transformed['Order_Quarter'] = df_transformed['Order_Date'].dt.quarter
    print("  ✓ Extracted date components")
    
    # 2.4 Create Derived Metrics
    print("\n[2.4] Derived Metrics Calculation")
    print("-" * 40)
    
    # Calculate Haversine distance between store and drop location
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c
    
    df_transformed['Distance_KM'] = haversine_distance(
        df_transformed['Store_Latitude'], df_transformed['Store_Longitude'],
        df_transformed['Drop_Latitude'], df_transformed['Drop_Longitude']
    )
    print("  ✓ Calculated delivery distance (km)")
    
    # Calculate pickup delay in minutes
    def time_diff_minutes(time1, time2, date):
        # Handle None values
        if time1 is None or time2 is None:
            return None
        try:
            datetime1 = datetime.combine(date, time1)
            datetime2 = datetime.combine(date, time2)
            diff = (datetime2 - datetime1).total_seconds() / 60
            return diff if diff >= 0 else diff + 1440  # Handle midnight crossover
        except:
            return None
    
    df_transformed['Pickup_Delay_Min'] = df_transformed.apply(
        lambda row: time_diff_minutes(
            row['Order_Time'], row['Pickup_Time'], row['Order_Date'].date()
        ), axis=1
    )
    print("  ✓ Calculated pickup delay (minutes)")
    
    # Calculate delivery speed
    df_transformed['Speed_KM_H'] = np.where(
        df_transformed['Delivery_Time'] > 0,
        (df_transformed['Distance_KM'] / df_transformed['Delivery_Time']) * 60,
        0
    )
    print("  ✓ Calculated delivery speed (km/h)")
    
    # Categorize delivery performance
    def categorize_performance(delivery_time):
        if delivery_time <= 60:
            return 'Fast'
        elif delivery_time <= 120:
            return 'Normal'
        elif delivery_time <= 180:
            return 'Slow'
        else:
            return 'Very Slow'
    
    df_transformed['Performance_Category'] = df_transformed['Delivery_Time'].apply(categorize_performance)
    print("  ✓ Categorized delivery performance")
    
    print("\n[2.5] Transformation Summary")
    print("-" * 40)
    print(f"  - Original rows: {len(df):,}")
    print(f"  - Final rows: {len(df_transformed):,}")
    print(f"  - New columns added: {len(df_transformed.columns) - len(df.columns)}")
    print(f"  - Data quality flags applied: Yes")
    
    return df_transformed

def create_dimension_tables(df):
    """
    Create dimension tables for Star Schema
    """
    print("\n" + "="*60)
    print("STEP 3: DIMENSION TABLE CREATION")
    print("="*60)
    
    dimensions = {}
    
    # 3.1 Agent Dimension
    print("\n[3.1] Creating Agent Dimension...")
    agent_dim = df[['Agent_Age', 'Agent_Rating']].drop_duplicates().reset_index(drop=True)
    agent_dim['Agent_ID'] = range(1, len(agent_dim) + 1)
    agent_dim = agent_dim[['Agent_ID', 'Agent_Age', 'Agent_Rating']]
    agent_dim['Rating_Category'] = agent_dim['Agent_Rating'].apply(
        lambda x: 'Excellent' if x >= 4.5 else 'Good' if x >= 4.0 else 'Average' if x >= 3.5 else 'Below Average'
    )
    dimensions['Dim_Agent'] = agent_dim
    print(f"  ✓ Agent Dimension: {len(agent_dim)} records")
    
    # 3.2 Time Dimension
    print("\n[3.2] Creating Time Dimension...")
    time_data = df[['Order_Date', 'Order_Year', 'Order_Month', 'Order_Day', 
                   'Order_Weekday', 'Order_Quarter']].drop_duplicates().reset_index(drop=True)
    time_data['Time_ID'] = range(1, len(time_data) + 1)
    
    # Add time of day category
    def categorize_time(order_time):
        hour = order_time.hour if hasattr(order_time, 'hour') else int(str(order_time)[:2])
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'
    
    time_data['Order_Time_Category'] = df.groupby('Order_Date')['Order_Time'].first().reset_index()['Order_Time'].apply(categorize_time)
    
    # Determine season
    def get_season(month):
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'
        else:
            return 'Winter'
    
    time_data['Season'] = time_data['Order_Month'].apply(get_season)
    time_data['Is_Weekend'] = time_data['Order_Weekday'].isin(['Saturday', 'Sunday'])
    
    time_dim = time_data[['Time_ID', 'Order_Date', 'Order_Year', 'Order_Month', 'Order_Day',
                         'Order_Weekday', 'Order_Quarter', 'Order_Time_Category', 'Season', 'Is_Weekend']]
    dimensions['Dim_Time'] = time_dim
    print(f"  ✓ Time Dimension: {len(time_dim)} records")
    
    # 3.3 Location Dimension
    print("\n[3.3] Creating Location Dimension...")
    location_data = df[['Store_Latitude', 'Store_Longitude', 
                       'Drop_Latitude', 'Drop_Longitude', 'Area']].drop_duplicates().reset_index(drop=True)
    location_data['Location_ID'] = range(1, len(location_data) + 1)
    
    # Calculate distance
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c
    
    location_data['Distance_KM'] = haversine_distance(
        location_data['Store_Latitude'], location_data['Store_Longitude'],
        location_data['Drop_Latitude'], location_data['Drop_Longitude']
    )
    
    # Categorize distance
    location_data['Distance_Category'] = location_data['Distance_KM'].apply(
        lambda x: 'Short' if x < 5 else 'Medium' if x < 15 else 'Long' if x < 30 else 'Very Long'
    )
    
    location_dim = location_data[['Location_ID', 'Store_Latitude', 'Store_Longitude',
                                  'Drop_Latitude', 'Drop_Longitude', 'Area', 
                                  'Distance_KM', 'Distance_Category']]
    dimensions['Dim_Location'] = location_dim
    print(f"  ✓ Location Dimension: {len(location_dim)} records")
    
    # 3.4 Weather Dimension
    print("\n[3.4] Creating Weather Dimension...")
    weather_data = df[['Weather']].drop_duplicates().reset_index(drop=True)
    weather_data['Weather_ID'] = range(1, len(weather_data) + 1)
    
    # Categorize weather severity
    def categorize_weather_severity(weather):
        severe = ['Stormy', 'Sandstorms']
        moderate = ['Rainy', 'Cloudy', 'Fog', 'Windy']
        good = ['Sunny']
        
        if weather in severe:
            return 'Severe'
        elif weather in moderate:
            return 'Moderate'
        else:
            return 'Good'
    
    weather_data['Weather_Severity'] = weather_data['Weather'].apply(categorize_weather_severity)
    
    # Impact on delivery
    def weather_impact(weather):
        high_impact = ['Stormy', 'Sandstorms', 'Fog']
        medium_impact = ['Rainy', 'Cloudy', 'Windy']
        low_impact = ['Sunny']
        
        if weather in high_impact:
            return 'High'
        elif weather in medium_impact:
            return 'Medium'
        else:
            return 'Low'
    
    weather_data['Delivery_Impact'] = weather_data['Weather'].apply(weather_impact)
    
    weather_dim = weather_data[['Weather_ID', 'Weather', 'Weather_Severity', 'Delivery_Impact']]
    dimensions['Dim_Weather'] = weather_dim
    print(f"  ✓ Weather Dimension: {len(weather_dim)} records")
    
    # 3.5 Vehicle Dimension
    print("\n[3.5] Creating Vehicle Dimension...")
    vehicle_data = df[['Vehicle', 'Traffic']].drop_duplicates().reset_index(drop=True)
    vehicle_data['Vehicle_ID'] = range(1, len(vehicle_data) + 1)
    
    # Categorize vehicle type
    def categorize_vehicle(vehicle):
        two_wheeler = ['motorcycle', 'scooter']
        four_wheeler = ['van']
        
        vehicle_clean = vehicle.strip().lower()
        if vehicle_clean in two_wheeler:
            return 'Two Wheeler'
        elif vehicle_clean in four_wheeler:
            return 'Four Wheeler'
        else:
            return 'Other'
    
    vehicle_data['Vehicle_Category'] = vehicle_data['Vehicle'].apply(categorize_vehicle)
    
    # Traffic impact
    def traffic_severity(traffic):
        traffic_clean = traffic.strip().lower()
        if 'jam' in traffic_clean:
            return 'High'
        elif 'high' in traffic_clean:
            return 'High'
        elif 'medium' in traffic_clean:
            return 'Medium'
        else:
            return 'Low'
    
    vehicle_data['Traffic_Impact'] = vehicle_data['Traffic'].apply(traffic_severity)
    
    vehicle_dim = vehicle_data[['Vehicle_ID', 'Vehicle', 'Vehicle_Category', 'Traffic', 'Traffic_Impact']]
    dimensions['Dim_Vehicle'] = vehicle_dim
    print(f"  ✓ Vehicle Dimension: {len(vehicle_dim)} records")
    
    # 3.6 Category Dimension
    print("\n[3.6] Creating Category Dimension...")
    category_data = df[['Category']].drop_duplicates().reset_index(drop=True)
    category_data['Category_ID'] = range(1, len(category_data) + 1)
    
    # Categorize product type
    def categorize_product_type(category):
        electronics = ['Electronics']
        fashion = ['Clothing', 'Shoes', 'Apparel', 'Jewelry', 'Cosmetics']
        home = ['Kitchen', 'Grocery']
        entertainment = ['Toys', 'Books', 'Sports']
        outdoor = ['Outdoors']
        other = ['Snacks']
        
        if category in electronics:
            return 'Electronics'
        elif category in fashion:
            return 'Fashion & Beauty'
        elif category in home:
            return 'Home & Living'
        elif category in entertainment:
            return 'Entertainment'
        elif category in outdoor:
            return 'Outdoor'
        else:
            return 'Other'
    
    category_data['Product_Type'] = category_data['Category'].apply(categorize_product_type)
    
    # Fragility category (assumption based on category)
    def fragility_level(category):
        fragile = ['Electronics', 'Jewelry', 'Cosmetics', 'Toys']
        moderately_fragile = ['Kitchen', 'Snacks']
        not_fragile = ['Clothing', 'Shoes', 'Books', 'Sports', 'Grocery', 'Outdoors', 'Apparel']
        
        if category in fragile:
            return 'High'
        elif category in moderately_fragile:
            return 'Medium'
        else:
            return 'Low'
    
    category_data['Fragility_Level'] = category_data['Category'].apply(fragility_level)
    
    category_dim = category_data[['Category_ID', 'Category', 'Product_Type', 'Fragility_Level']]
    dimensions['Dim_Category'] = category_dim
    print(f"  ✓ Category Dimension: {len(category_dim)} records")
    
    print("\n" + "="*60)
    print("DIMENSION CREATION COMPLETE")
    print("="*60)
    print(f"Total Dimensions Created: {len(dimensions)}")
    for name, dim in dimensions.items():
        print(f"  - {name}: {len(dim)} rows")
    
    return dimensions

def create_fact_table(df, dimensions):
    """
    Create Fact Delivery table by joining with dimension tables
    """
    print("\n" + "="*60)
    print("STEP 4: FACT TABLE CREATION")
    print("="*60)
    
    fact_df = df.copy()
    
    # Join with Agent Dimension
    print("\n[4.1] Joining with Agent Dimension...")
    fact_df = fact_df.merge(
        dimensions['Dim_Agent'][['Agent_ID', 'Agent_Age', 'Agent_Rating']],
        on=['Agent_Age', 'Agent_Rating'],
        how='left'
    )
    print(f"  ✓ Joined with Dim_Agent")
    
    # Join with Time Dimension
    print("\n[4.2] Joining with Time Dimension...")
    fact_df = fact_df.merge(
        dimensions['Dim_Time'][['Time_ID', 'Order_Date', 'Order_Year', 'Order_Month', 'Order_Day']],
        on=['Order_Date', 'Order_Year', 'Order_Month', 'Order_Day'],
        how='left'
    )
    print(f"  ✓ Joined with Dim_Time")
    
    # Join with Location Dimension
    print("\n[4.3] Joining with Location Dimension...")
    fact_df = fact_df.merge(
        dimensions['Dim_Location'][['Location_ID', 'Store_Latitude', 'Store_Longitude', 
                                  'Drop_Latitude', 'Drop_Longitude']],
        on=['Store_Latitude', 'Store_Longitude', 'Drop_Latitude', 'Drop_Longitude'],
        how='left'
    )
    print(f"  ✓ Joined with Dim_Location")
    
    # Join with Weather Dimension
    print("\n[4.4] Joining with Weather Dimension...")
    fact_df = fact_df.merge(
        dimensions['Dim_Weather'][['Weather_ID', 'Weather']],
        on=['Weather'],
        how='left'
    )
    print(f"  ✓ Joined with Dim_Weather")
    
    # Join with Vehicle Dimension
    print("\n[4.5] Joining with Vehicle Dimension...")
    fact_df = fact_df.merge(
        dimensions['Dim_Vehicle'][['Vehicle_ID', 'Vehicle', 'Traffic']],
        on=['Vehicle', 'Traffic'],
        how='left'
    )
    print(f"  ✓ Joined with Dim_Vehicle")
    
    # Join with Category Dimension
    print("\n[4.6] Joining with Category Dimension...")
    fact_df = fact_df.merge(
        dimensions['Dim_Category'][['Category_ID', 'Category']],
        on=['Category'],
        how='left'
    )
    print(f"  ✓ Joined with Dim_Category")
    
    # Select fact table columns
    fact_columns = [
        'Order_ID', 'Agent_ID', 'Time_ID', 'Location_ID', 'Weather_ID',
        'Vehicle_ID', 'Category_ID', 'Order_Time', 'Pickup_Time',
        'Distance_KM', 'Pickup_Delay_Min', 'Delivery_Time', 'Speed_KM_H',
        'Performance_Category', 'Coordinate_Flag'
    ]
    
    fact_table = fact_df[fact_columns].copy()
    
    # Create surrogate key for fact table
    fact_table['Delivery_Fact_ID'] = range(1, len(fact_table) + 1)
    
    # Reorder columns
    cols = ['Delivery_Fact_ID'] + [c for c in fact_columns if c != 'Order_ID']
    fact_table = fact_table[cols]
    
    print("\n" + "="*60)
    print("FACT TABLE CREATION COMPLETE")
    print("="*60)
    print(f"  - Fact Table: {len(fact_table):,} records")
    print(f"  - Total columns: {len(fact_table.columns)}")
    print(f"\n  Fact Table Columns:")
    for col in fact_table.columns:
        print(f"    - {col}")
    
    return fact_table

def load_data(dimensions, fact_table):
    """
    Load dimension and fact tables to CSV files
    """
    print("\n" + "="*60)
    print("STEP 5: LOADING TO DATA WAREHOUSE")
    print("="*60)
    
    loaded_files = []
    
    # Load dimension tables
    for dim_name, dim_df in dimensions.items():
        file_path = os.path.join(OUTPUT_DIR, f"{dim_name}.csv")
        dim_df.to_csv(file_path, index=False)
        loaded_files.append(file_path)
        print(f"✓ Loaded {dim_name}: {len(dim_df):,} records -> {file_path}")
    
    # Load fact table
    fact_file = os.path.join(OUTPUT_DIR, "Fact_Delivery.csv")
    fact_table.to_csv(fact_file, index=False)
    loaded_files.append(fact_file)
    print(f"✓ Loaded Fact_Delivery: {len(fact_table):,} records -> {fact_file}")
    
    # Generate load summary
    summary = {
        'total_dimensions': len(dimensions),
        'total_fact_records': len(fact_table),
        'files_created': len(loaded_files),
        'output_directory': OUTPUT_DIR
    }
    
    print("\n" + "="*60)
    print("LOAD COMPLETE - SUMMARY")
    print("="*60)
    print(f"  - Dimension tables: {summary['total_dimensions']}")
    print(f"  - Fact table records: {summary['total_fact_records']:,}")
    print(f"  - Files created: {summary['files_created']}")
    print(f"  - Output directory: {summary['output_directory']}")
    
    return loaded_files, summary

def main():
    """
    Main ETL Pipeline Execution
    """
    print("="*60)
    print("AMAZON DELIVERY DATA WAREHOUSE - ETL PIPELINE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        # Step 1: Extract
        raw_data = extract_data(INPUT_FILE)
        
        # Step 2: Transform
        transformed_data = transform_data(raw_data)
        
        # Step 3: Create Dimensions
        dimensions = create_dimension_tables(transformed_data)
        
        # Step 4: Create Fact Table
        fact_table = create_fact_table(transformed_data, dimensions)
        
        # Step 5: Load
        files, summary = load_data(dimensions, fact_table)
        
        print("\n" + "="*60)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        return {
            'status': 'success',
            'files_created': files,
            'summary': summary,
            'dimensions': dimensions,
            'fact_table': fact_table
        }
        
    except Exception as e:
        print("\n" + "="*60)
        print("ETL PIPELINE FAILED!")
        print("="*60)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }

if __name__ == "__main__":
    result = main()
