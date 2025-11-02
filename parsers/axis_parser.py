import pandas as pd
import streamlit as st
import re
from parsers.base_parser import clean_amount

def parse(pdf):
    """
    Parses the Axis My Zone Credit Card statement.
    """
    transactions = []
    
    # Regex to find a date in DD/MM/YYYY format
    date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')

    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            
            for row in table:
                if not row or len(row) < 4:
                    continue

                date_str = row[0]
                amount_str = row[3]

                # Check if the first column is a date and the fourth column exists
                if date_str and date_pattern.match(date_str) and amount_str:
                    
                    description = row[1]
                    if description:
                        description = description.replace('\n', ' ')
                    
                    amount = clean_amount(amount_str)
                    
                    if amount != 0.0:
                        transactions.append({
                            "Date": date_str,
                            "Description": description,
                            "Amount": amount
                        })

    if not transactions:
        st.warning("Could not find any transactions in the Axis PDF.")
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df