import requests
import pandas as pd
import numpy as np
import pickle
import re
import warnings
warnings.filterwarnings('ignore')

# Load secrets
with open(r'C:\the force\00_Master\secrets.md', 'r') as f:
    secrets = f.read()

ALPHA_VANTAGE_API_KEY = re.search(r'Alpha Vantage\s+`([^`]+)`', secrets).group(1)
FRED_API_KEY = re.search(r'FRED \(St\. Louis Fed\)\s+`([^`]+)`', secrets).group(1)

# Fetch GBP/USD daily data (full history)
print("Fetching GBP/USD daily data from Alpha Vantage...")
url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=GBP&to_symbol=USD&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}'
response = requests.get(url)
data = response.json()

ts_key = 'Time Series FX (Daily)'
if ts_key not in data:
    raise Exception(f"Alpha Vantage API error: {data}")

df = pd.DataFrame.from_dict(data[ts_key], orient='index')
df.index = pd.to_datetime(df.index)
df = df.sort_index(ascending=True)
df = df.rename(columns={
    '1. open': 'open',
    '2. high': 'high',
    '3. low': 'low',
    '4. close': 'close'
})
df = df[['open', 'high', 'low', 'close']].astype(float)
df['volume'] = 0

print(f"Loaded {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")

# Fetch FRED data
print("Fetching FRED data (UNRATE, PAYEMS)...")

def fetch_fred_series(series_id, api_key):
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json'
    response = requests.get(url)
    data = response.json()
    if 'observations' not in data:
        raise Exception(f"FRED API error for {series_id}: {data}")
    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df[['date', 'value']].dropna()
    df.set_index('date', inplace=True)
    return df

unrate_df = fetch_fred_series('UNRATE', FRED_API_KEY)
payems_df = fetch_fred_series('PAYEMS', FRED_API_KEY)

print(f"UNRATE: {len(unrate_df)} obs from {unrate_df.index[0].date()} to {unrate_df.index[-1].date()}")
print(f"PAYEMS: {len(payems_df)} obs from {payems_df.index[0].date()} to {payems_df.index[-1].date()}")

# Calculate MoM change for macro gates (resample to daily and forward fill)
unrate_daily = unrate_df['value'].resample('D').ffill()
payems_daily = payems_df['value'].resample('D').ffill()

# Align to FX index
unrate_aligned = unrate_daily.reindex(df.index, method='ffill')
payems_aligned = payems_daily.reindex(df.index, method='ffill')

# Calculate MoM change (approx 21 trading days)
unrate_mom = unrate_aligned.pct_change(21) * 100
payems_mom = payems_aligned.pct_change(21) * 100

print("Data preparation complete.")
print(f"FX bars: {len(df)}, UNRATE aligned: {unrate_aligned.notna().sum()}, PAYEMS aligned: {payems_aligned.notna().sum()}")

# Save data for later use
with open(r'C:\the force\03_Context\projects\trading\optimization_data.pkl', 'wb') as f:
    pickle.dump({
        'df': df,
        'unrate_mom': unrate_mom,
        'payems_mom': payems_mom
    }, f)

print("Data saved to optimization_data.pkl")
print("DONE")