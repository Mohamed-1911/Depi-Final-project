import pandas as pd
import numpy as np
import re

# Load
df = pd.read_csv('googleplaystore.csv')
print(f"Original: {len(df)} rows")

# 1. Remove corrupted row
df = df[df['Category'] != '1.9']


# 2. Remove duplicates -> keep latest (fully normalized)
# 2a. Normalize App names: lowercase + strip spaces + remove invisible characters
df['App'] = df['App'].str.strip().str.lower()

# 2a. Convert 'Last Updated' to datetime if not already
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')

# 2b. Sort by Last Updated descending (latest first)
df = df.sort_values('Last Updated', ascending=False)

# 2c. Drop duplicates based on normalized App, keep latest
df = df.drop_duplicates(subset='App', keep='first')

# 3. Clean Installs 
df['Installs'] = df['Installs'].str.replace(',', '').str.replace('+', '') 
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# 4. Clean Size → MB
def clean_size_mb(size):
    if pd.isna(size):
        return np.nan
    size = str(size).strip()
    if size == 'Varies with device':
        return np.nan
    if 'M' in size:
        return float(size.replace('M', ''))
    if 'k' in size:
        return round(float(size.replace('k', '')) / 1024, 3)
    return np.nan

df['Size_MB'] = df['Size'].apply(clean_size_mb)
df = df.drop(columns=['Size'])

# 5. Clean Price
df['Price'] = df['Price'].str.replace('$', '').astype(float)

# 6. Clean Reviews
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# 7. Fix Rating
df.loc[df['Rating'] > 5, 'Rating'] = np.nan

# 8. Clean Type 
df['Type'] = df['Type'].fillna('Free')
df.loc[df['Price'] > 0, 'Type'] = 'Paid'
df.loc[df['Price'] == 0, 'Type'] = 'Free'

# 9. Impute missing Size_MB by category mdedian 
median_size_by_category = df.groupby('Category')['Size_MB'].median()
def fill_size_mb(row):
    if pd.isna(row['Size_MB']):
        return median_size_by_category.get(row['Category'], df['Size_MB'].median())
    return row['Size_MB']
df['Size_MB'] = df.apply(fill_size_mb, axis=1)

# 10. Clean Android Ver → extract minimum version
def extract_min_android(ver):
    if pd.isna(ver):
        return np.nan
    ver = str(ver)
    match = re.search(r'\d+\.?\d*', ver)
    return float(match.group()) if match else np.nan

df['Android_Min_Version'] = df['Android Ver'].apply(extract_min_android)

# 11. Drop messy original columns
df = df.drop(columns=['Current Ver', 'Android Ver'])

# 12. Fill missing Android version intelligently
median_android_by_category = df.groupby('Category')['Android_Min_Version'].median()

def fill_android_version(row):
    if pd.isna(row['Android_Min_Version']):
        return median_android_by_category.get(row['Category'], 4.1)  # 4.1 = global fallback
    return row['Android_Min_Version']

df['Android_Min_Version'] = df.apply(fill_android_version, axis=1)
df['Android_Min_Version'] = df['Android_Min_Version'].round(1)

print(f"Missing Android_Min_Version after filling: {df['Android_Min_Version'].isna().sum()}")  # → 0


df = df.reset_index(drop=True)
print(f"FINAL PERFECT DATASET: {len(df)} rows")
print(f"Missing Size_MB: {df['Size_MB'].isna().sum()}")
print(f"Missing Android_Min_Version: {df['Android_Min_Version'].isna().sum()}")  # → 0

#  makes numbers look clean
df['Size_MB']             = df['Size_MB'].round(2)
df['Android_Min_Version'] = df['Android_Min_Version'].round(1)
df['Price']               = df['Price'].round(2)

print("Applied beautiful rounding – no more 9.649999999999999!")

# Label nulls in rating to be "unarted" in new column 
df['Rating'] = df['Rating'].round(1)  

df['Rating_Display'] = df['Rating'].apply(
    lambda x: 'Unrated' if pd.isna(x) else f"{x:.1f} stars"
)

# Clean column genres
df['Genres'] = df['Genres'].str.replace(';', ' / ')
df['Genres'] = df['Genres'].str.replace('&', ' & ')
df['Genres'] = df['Genres'].str.strip()

# Save clean file
df.to_csv('GooglePlayStore_CLEAN.csv', index=False)
print("SAVED → GooglePlayStore_CLEAN.csv")





