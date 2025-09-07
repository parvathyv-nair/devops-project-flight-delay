# preprocess.py
import pandas as pd

# Load dataset
data = pd.read_csv("flight_delays.csv")

# Quick look at the data
print("Dataset shape:", data.shape)
print("Columns:", data.columns)

# Example preprocessing steps:

# 1. Drop rows with missing values
data = data.dropna()

# 2. Convert date/time columns to datetime format (if present)
if 'ScheduledDeparture' in data.columns:
    data['ScheduledDeparture'] = pd.to_datetime(data['ScheduledDeparture'])

if 'ScheduledArrival' in data.columns:
    data['ScheduledArrival'] = pd.to_datetime(data['ScheduledArrival'])

# 3. Create new features (example: flight duration in minutes)
if 'ScheduledDeparture' in data.columns and 'ScheduledArrival' in data.columns:
    data['FlightDuration'] = (data['ScheduledArrival'] - data['ScheduledDeparture']).dt.total_seconds() / 60

# 4. Encode categorical columns
categorical_cols = data.select_dtypes(include=['object']).columns
for col in categorical_cols:
    data[col] = data[col].astype('category').cat.codes

# Save processed dataset
data.to_csv("processed_flight_delays.csv", index=False)

print("Preprocessing complete. Processed data saved to processed_flight_delays.csv")
