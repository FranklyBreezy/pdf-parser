import pandas as pd
import streamlit as st
import re
from parsers.base_parser import clean_amount

def parse(pdf):
    """
    Parses the ICICI Amazon Pay statement.
    This statement has a very messy table format.
    """
    transactions = []
    
    # Regex to find a date in DD/MM/YYYY format
    date_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')

    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            
            for row in table:
                if not row or len(row) < 3:
                    continue

                col1 = row[0]
                col2 = row[1]
                col3 = row[2]
                
                if not col1 or not col2 or not col3:
                    continue

                # Search for a date in the first column
                date_match = date_pattern.search(str(col1))
                
                # This is a transaction row if col1 has a date and col3 has an amount
                if date_match:
                    date_str = date_match.group(1)
                    description = str(col2).replace('\n', ' ')
                    amount = clean_amount(str(col3))
                    
                    if amount != 0.0:
                        transactions.append({
                            "Date": date_str,
                            "Description": description,
                            "Amount": amount
                        })

    if not transactions:
        st.warning("Could not find any transactions in the ICICI Amazon PDF.")
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df