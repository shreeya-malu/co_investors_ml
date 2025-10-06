from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

def run_apriori_weighted(df, min_support=0.02, min_confidence=0.4):
    """
    Weighted Apriori using investment amount as weight
    """
    if 'Amount in USD' not in df.columns:
        # fallback to unweighted
        from .apriori_unweighted import run_apriori_unweighted
        return run_apriori_unweighted(df, min_support, min_confidence)

    all_investors = set(i for invs in df['investors_list'] for i in invs)
    # Weight = investment amount normalized
    amounts = df['Amount in USD'].fillna(0)
    total_amount = amounts.sum()
    weights = amounts / total_amount

    # Create weighted one-hot encoded matrix
    oht = pd.DataFrame([{inv: (inv in invs)*w for inv in all_investors} for invs,w in zip(df['investors_list'], weights)])

    freq_items = apriori(oht, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_items, metric='confidence', min_threshold=min_confidence)

    # Format for JSON
    itemsets = [{'items': list(row['itemsets']), 'support': float(row['support'])} for idx,row in freq_items.iterrows()]
    rules_out = [{'antecedent': list(row['antecedents']), 'consequent': list(row['consequents']),
                  'support': float(row['support']), 'confidence': float(row['confidence']),
                  'lift': float(row['lift'])} for idx,row in rules.iterrows()]

    return itemsets, rules_out
