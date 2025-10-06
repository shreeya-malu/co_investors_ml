from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

def run_apriori_unweighted(df, min_support=0.02, min_confidence=0.4):
    """
    Run unweighted Apriori on investor transactions
    """
    # Create one-hot encoded transaction matrix
    all_investors = set(i for invs in df['investors_list'] for i in invs)
    oht = pd.DataFrame([{inv: (inv in invs) for inv in all_investors} for invs in df['investors_list']])

    freq_items = apriori(oht, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_items, metric='confidence', min_threshold=min_confidence)

    # Format for JSON
    itemsets = [{'items': list(row['itemsets']), 'support': float(row['support'])} for idx,row in freq_items.iterrows()]
    rules_out = [{'antecedent': list(row['antecedents']), 'consequent': list(row['consequents']),
                  'support': float(row['support']), 'confidence': float(row['confidence']),
                  'lift': float(row['lift'])} for idx,row in rules.iterrows()]

    return itemsets, rules_out
