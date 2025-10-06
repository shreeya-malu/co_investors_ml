from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

def investor_investor_apriori(df, min_support=0.02, min_confidence=0.4):
    """Investor -> Investor co-investment rules"""
    all_investors = set(i for invs in df['investors_list'] for i in invs)
    oht = pd.DataFrame([{inv: (inv in invs) for inv in all_investors} for invs in df['investors_list']])
    freq_items = apriori(oht, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_items, metric='confidence', min_threshold=min_confidence)
    return freq_items, rules

def startup_startup_apriori(df, min_support=0.02, min_confidence=0.4):
    """Startup -> Startup rules based on shared investors"""
    all_startups = df['startup_name'].tolist()
    # one-hot investors per startup
    oht = pd.DataFrame([{inv: (inv in invs) for inv in set(i for invs in df['investors_list'] for i in invs)} 
                        for invs in df['investors_list']], index=df['startup_name'])
    freq_items = apriori(oht.T, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_items, metric='confidence', min_threshold=min_confidence)
    return freq_items, rules
