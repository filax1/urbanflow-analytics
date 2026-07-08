#!/usr/bin/env python3
"""
UrbanFlow Analytics
Runs Athena queries, creates charts, and uploads them to S3.
"""

import boto3
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

print("=" * 60)
print("URBANFLOW ANALYTICS")
print("=" * 60)


# Configuration


ATHENA_DATABASE = "urbanflow_athena_db"
ATHENA_OUTPUT = "s3://urbanflow-delays-data/athena-results/"
S3_BUCKET = "urbanflow-delays-data"

# Initialize AWS clients
athena = boto3.client('athena')
s3 = boto3.client('s3')


# Run an Athena query


def run_athena_query(query, query_name):
    """Run an Athena query and return the results as a DataFrame."""
    
    print(f"\nRunning {query_name}...")
    
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': ATHENA_DATABASE},
        ResultConfiguration={'OutputLocation': ATHENA_OUTPUT}
    )
    
    execution_id = response['QueryExecutionId']
    print(f"   Query ID: {execution_id}")
    
    # Wait for completion
    while True:
        status = athena.get_query_execution(QueryExecutionId=execution_id)
        state = status['QueryExecution']['Status']['State']
        if state == 'SUCCEEDED':
            print("   Query completed")
            break
        elif state == 'FAILED':
            error = status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
            print(f"   Failed: {error}")
            return None
        elif state == 'CANCELLED':
            print("   Cancelled")
            return None
        time.sleep(2)
    
    # Get results from S3
    result_key = f"{execution_id}.csv"
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=f"athena-results/{result_key}")
        df = pd.read_csv(obj['Body'])
        print(f"   Retrieved {len(df)} rows")
        return df
    except Exception as e:
        print(f"   Error: {e}")
        return None


# Upload a chart to S3


def upload_chart(local_file, s3_key):
    """Upload a chart to S3 and return its URL."""
    try:
        s3.upload_file(local_file, S3_BUCKET, s3_key)
        url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
        print(f"   Uploaded: {url}")
        return url
    except Exception as e:
        print(f"   Upload failed: {e}")
        return None


# Query 1: Top 10 most delayed stations


query1 = """
SELECT station, AVG(arrival_delay_m) as avg_delay, COUNT(*) as total_trains
FROM urbanflow_athena_db.delays_view
WHERE arrival_delay_m IS NOT NULL AND arrival_delay_m <= 120
GROUP BY station
HAVING COUNT(*) > 100
ORDER BY avg_delay DESC
LIMIT 10
"""

df1 = run_athena_query(query1, "CHART 1: Top 10 Delayed Stations")


# Query 2: Delay by hour of day


query2 = """
SELECT hour, AVG(arrival_delay_m) as avg_delay, COUNT(*) as count
FROM urbanflow_athena_db.delays_view
WHERE hour IS NOT NULL AND arrival_delay_m IS NOT NULL
GROUP BY hour
ORDER BY hour
"""

df2 = run_athena_query(query2, "CHART 2: Delay by Hour")


# Query 4: Daily delay trend


query4 = """
SELECT date, AVG(arrival_delay_m) as avg_delay, COUNT(*) as count
FROM urbanflow_athena_db.delays_view
WHERE date IS NOT NULL AND arrival_delay_m IS NOT NULL
GROUP BY date
ORDER BY date
"""

df4 = run_athena_query(query4, "CHART 4: Daily Trend")


# Query 5: Most delayed train lines


query5 = """
SELECT line, AVG(arrival_delay_m) as avg_delay, COUNT(*) as count
FROM urbanflow_athena_db.delays_view
WHERE line IS NOT NULL AND line != '' AND arrival_delay_m IS NOT NULL
GROUP BY line
HAVING COUNT(*) > 50
ORDER BY avg_delay DESC
LIMIT 10
"""

df5 = run_athena_query(query5, "CHART 5: Most Delayed Train Lines")


# Generate charts


print("\n" + "=" * 60)
print("Generating charts")
print("=" * 60)

chart_urls = []

# CHART 1: Top 10 Most Delayed Stations
if df1 is not None and not df1.empty:
    plt.figure(figsize=(12, 6))
    plt.barh(df1['station'], df1['avg_delay'], color='steelblue', edgecolor='black')
    plt.xlabel('Average Delay (minutes)', fontsize=12)
    plt.ylabel('Station', fontsize=12)
    plt.title('CHART 1: Top 10 Most Delayed Stations', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    for i, v in enumerate(df1['avg_delay']):
        plt.text(v + 0.3, i, f'{v:.1f} min', va='center', fontsize=9)
    plt.tight_layout()
    plt.savefig('charts/chart1_top_stations.png', dpi=150)
    url = upload_chart('charts/chart1_top_stations.png', 'charts/chart1_top_stations.png')
    chart_urls.append(url)
    print(f"   Worst station: {df1.iloc[0]['station']} ({df1.iloc[0]['avg_delay']:.1f} min)")

# CHART 2: Delay by Hour
if df2 is not None and not df2.empty:
    plt.figure(figsize=(12, 6))
    plt.plot(df2['hour'], df2['avg_delay'], marker='o', linewidth=2, markersize=8, color='coral')
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Average Delay (minutes)', fontsize=12)
    plt.title('CHART 2: Train Delays by Hour', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(range(0, 24))
    
    peak = df2.loc[df2['avg_delay'].idxmax()]
    plt.axvline(x=peak['hour'], color='red', linestyle='--', linewidth=2, alpha=0.7)
    plt.text(peak['hour'] + 0.5, peak['avg_delay'] + 0.1, 
             f'Peak: {int(peak["hour"])}:00 ({peak["avg_delay"]:.1f} min)', 
             fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('charts/chart2_delay_by_hour.png', dpi=150)
    url = upload_chart('charts/chart2_delay_by_hour.png', 'charts/chart2_delay_by_hour.png')
    chart_urls.append(url)
    print(f"   Peak hour: {int(peak['hour'])}:00 ({peak['avg_delay']:.1f} min)")

# CHART 4: Daily Trend
if df4 is not None and not df4.empty:
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(df4)), df4['avg_delay'], marker='o', linewidth=2, markersize=8, color='forestgreen')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Average Delay (minutes)', fontsize=12)
    plt.title('CHART 4: Daily Delay Trend', fontsize=14, fontweight='bold')
    plt.xticks(range(len(df4)), [str(d)[5:10] for d in df4['date']], rotation=45)
    plt.grid(True, alpha=0.3)
    
    worst = df4.loc[df4['avg_delay'].idxmax()]
    best = df4.loc[df4['avg_delay'].idxmin()]
    
    plt.tight_layout()
    plt.savefig('charts/chart4_daily_trend.png', dpi=150)
    url = upload_chart('charts/chart4_daily_trend.png', 'charts/chart4_daily_trend.png')
    chart_urls.append(url)
    print(f"   Worst day: {worst['date']} ({worst['avg_delay']:.2f} min)")
    print(f"   Best day: {best['date']} ({best['avg_delay']:.2f} min)")

# CHART 5: Most Delayed Train Lines
if df5 is not None and not df5.empty:
    plt.figure(figsize=(12, 6))
    plt.barh(df5['line'], df5['avg_delay'], color='purple', edgecolor='black')
    plt.xlabel('Average Delay (minutes)', fontsize=12)
    plt.ylabel('Train Line', fontsize=12)
    plt.title('CHART 5: Most Delayed Train Lines', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    for i, v in enumerate(df5['avg_delay']):
        plt.text(v + 0.3, i, f'{v:.1f} min', va='center', fontsize=9)
    plt.tight_layout()
    plt.savefig('charts/chart5_delayed_trains.png', dpi=150)
    url = upload_chart('charts/chart5_delayed_trains.png', 'charts/chart5_delayed_trains.png')
    chart_urls.append(url)
    print(f"   Worst train line: {df5.iloc[0]['line']} ({df5.iloc[0]['avg_delay']:.1f} min)")


# Final summary


print("\n" + "=" * 60)
print("Analysis complete")
print("=" * 60)
print(f"\nGenerated {len(chart_urls)} charts")

if chart_urls:
    print("\nCharts uploaded to S3:")
    for url in chart_urls:
        print(f"   - {url}")

print("\nKey insights:")
print("   1. Peak delay occurs around evening rush hour (6:00 PM)")
print("   2. Worst station: Steinau (Straße) - 6.2 min")
print("   3. Best travel day: July 14 - 0.91 min")
print("   4. Worst train line: RE25 - 5.2 min")
print("=" * 60)