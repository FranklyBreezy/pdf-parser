import pandas as pd
from parsers.base_parser import clean_amount

def parse(pdf):
    """
    Parses the ICICI Coral Credit Card statement.
    """
    transactions = []
    
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            # Assume first row is header
            if not table:
                continue
                
            df = pd.DataFrame(table[1:], columns=table[0])
            
            # Check if this is the transaction table
            if 'Transaction Details' in df.columns and 'Amount (int)' in df.columns:
                
                df = df[['Date', 'Transaction Details', 'Amount (int)']].dropna()

                for _, row in df.iterrows():
                    # The "Amount (int)" column has 'CR' for credits
                    amount = clean_amount(row['Amount (int)'])
                    
                    transactions.append({
                        "Date": row['Date'],
                        "Description": row['Transaction Details'],
                        "Amount": amount
                    })

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df