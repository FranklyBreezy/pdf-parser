import pandas as pd
import streamlit as st
import re
from parsers.base_parser import clean_amount

def parse(pdf):
    """
    Parses the IDFC First Bank statement.
    """
    transactions = []
    
    # Regex to find a date in DD/MM/YYYY format
    date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')

    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            # Check if this is the main transaction table
            if not table or table[0] != ['Transaction Date', 'Transactional Details', 'FX Transactions', 'Amount ()']:
                 continue
                 
            for row in table[1:]: # Skip header row
                if not row or len(row) < 4:
                    continue

                date_str = row[0]
                desc_str = row[1]
                amount_str = row[3]

                # Check if the first column is a date and amount exists
                if date_str and date_pattern.match(date_str) and amount_str:
                    
                    if desc_str:
                        desc_str = desc_str.replace('\n', ' ')
                    
                    amount = clean_amount(amount_str)
                    
                    if amount != 0.0:
                        transactions.append({
                            "Date": date_str,
                            "Description": desc_str,
                            "Amount": amount
                        })

    if not transactions:
        st.warning("Could not find any transactions in the IDFC PDF.")
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df