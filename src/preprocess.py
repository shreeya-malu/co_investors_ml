import pandas as pd

def preprocess_dataset(df):
    """
    Preprocess Indian Startup Funding CSV for Apriori
    - Normalize investor names
    - Split multiple investors per startup
    - Extract verticals/domains if available
    """
    df = df.copy()
    df = df.dropna(subset=['Startup Name','Investors Name'])

    # Normalize investor names: strip, lower, simple replacements
    def normalize_investor(name):
        name = str(name).strip().lower()
        name = name.replace('sequoia capital india','sequoia')
        name = name.replace('accel partners','accel')
        name = name.replace('matrix partners india','matrix')
        name = name.title()
        return name

    # Split investors (comma-separated)
    df['investors_list'] = df['Investors Name'].apply(lambda x: [normalize_investor(i) for i in str(x).split(',')])

    # If vertical/domain info exists, split it - check for both 'SubVertical' and 'Vertical' columns
    if 'SubVertical' in df.columns:
        df['verticals_list'] = df['SubVertical'].apply(lambda x: [v.strip() for v in str(x).split(',')] if pd.notna(x) else [])
    elif 'Vertical' in df.columns:
        df['verticals_list'] = df['Vertical'].apply(lambda x: [v.strip() for v in str(x).split(',')] if pd.notna(x) else [])
    else:
        df['verticals_list'] = [[] for _ in range(len(df))]

    df['startup_name'] = df['Startup Name']

    # Return processed df + list of unique investors + list of startups
    all_investors = set(i for invs in df['investors_list'] for i in invs)
    all_startups = list(df['startup_name'])

    return df, list(all_investors), all_startups
