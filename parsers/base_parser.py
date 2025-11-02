import re
import pandas as pd

def clean_amount(amount_str):
    """
    Cleans an amount string and converts it to a float.
    - Removes $, ₹, ,, and spaces
    - Treats 'Cr' or '()' as negative (payments/credits)
    - Treats 'Dr' as positive (debits/spend)
    """
    if amount_str is None:
        return 0.0
        
    s = str(amount_str).strip()
    
    # Check for credit (negative)
    is_credit = bool(re.search(r'(cr|\(.*\))', s, re.IGNORECASE))
    
    # Remove all non-numeric/non-decimal characters
    s_cleaned = re.sub(r"[^0-9\.]", "", s)
    
    try:
        amount = float(s_cleaned)
        if is_credit:
            return -amount # Make credits negative
        return amount # Debits are positive
    except ValueError:
        return 0.0