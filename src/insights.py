import pandas as pd
from .multi_level_apriori import investor_investor_apriori, startup_startup_apriori
from collections import Counter

def compute_insights(df):
    # Stats
    n_startups = len(df)
    n_investors = len(set(i for invs in df['investors_list'] for i in invs))

    # Top co-investors
    co_count = Counter()
    for invs in df['investors_list']:
        co_count.update(invs)
    top_co = co_count.most_common(10)

    # Top domains
    domain_count = Counter()
    for domains in df['verticals_list']:
        domain_count.update(domains)
    top_domains = domain_count.most_common(10)

    # Top startups by investor count
    top_startups = df.groupby('startup_name')['investors_list'].count().sort_values(ascending=False).head(10).to_dict()

    # Multi-level Apriori (investor-investor)
    inv_freq, inv_rules = investor_investor_apriori(df)
    
    # Multi-level Apriori (startup-startup)
    startup_freq, startup_rules = startup_startup_apriori(df)

    return {
        'stats': {'n_startups': n_startups, 'n_unique_investors': n_investors},
        'top_co': top_co,
        'top_domains': top_domains,
        'top_startups': top_startups,
        'inv_apriori_freq': inv_freq,
        'inv_apriori_rules': inv_rules,
        'startup_apriori_freq': startup_freq,
        'startup_apriori_rules': startup_rules
    }
