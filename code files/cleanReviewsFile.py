import pandas as pd

# Load both files
main   = pd.read_csv('GooglePlayStore_ULTIMATE_CLEAN_2025.csv')
reviews = pd.read_csv('googleplaystore_user_reviews.csv')

print(f"Raw reviews: {len(reviews):,} rows")

# STEP 1: Clean App names for joins
reviews['App'] = reviews['App'].astype(str).str.strip()

# STEP 2: Remove completely useless rows
reviews = reviews[reviews['App'] != 'nan']
reviews = reviews.dropna(subset=['Translated_Review'])               # no review text
reviews = reviews[reviews['Translated_Review'].str.lower() != 'nan']

# STEP 3: Clean Sentiment column
reviews['Sentiment'] = reviews['Sentiment'].str.title()              # Positive / Negative / Neutral
reviews = reviews[reviews['Sentiment'].isin(['Positive', 'Negative', 'Neutral'])]

# STEP 4: Clean numeric columns
reviews['Sentiment_Polarity']    = pd.to_numeric(reviews['Sentiment_Polarity'],    errors='coerce')
reviews['Sentiment_Subjectivity'] = pd.to_numeric(reviews['Sentiment_Subjectivity'], errors='coerce')

# STEP 5: Round to clean numbers (beautiful in charts)
reviews['Sentiment_Polarity']    = reviews['Sentiment_Polarity'].round(4)
reviews['Sentiment_Subjectivity'] = reviews['Sentiment_Subjectivity'].round(4)

# STEP 6: Keep only apps that exist in main file (perfect join)
common_apps = set(main['App']).intersection(set(reviews['App']))
reviews_clean = reviews[reviews['App'].isin(common_apps)]

print(f"After full cleaning: {len(reviews_clean):,} high-quality reviews")
print(f"Unique apps with reviews: {reviews_clean['App'].nunique()}")

# STEP 7: Save the file
reviews_clean.to_csv('reviews_FULLY_CLEANED_PERFECT.csv', index=False)
print("SAVED → reviews_FULLY_CLEANED_PERFECT.csv")