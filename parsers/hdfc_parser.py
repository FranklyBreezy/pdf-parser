import pandas as pd
from parsers.base_parser import clean_amount

def parse(pdf):
    """
    Parses the HDFC MoneyBack Credit Card statement.
    """
    transactions = []
    
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            df = pd.DataFrame(table)
            
            # Find the header of the transaction table
            if 'Transaction Description' in df.values and 'Amount (inRs.)' in df.values:
                # Find the row index of the header
                header_row = df.where(df == 'Transaction Description').dropna(how='all').index[0]
                
                # Set the correct header
                df.columns = df.iloc[header_row]
                # Get all rows after the header
                df = df.iloc[header_row + 1:]
                
                # Filter for valid transaction rows
                df = df[['Date', 'Transaction Description', 'Amount (inRs.)']].dropna()

                for _, row in df.iterrows():
                    transactions.append({
                        "Date": row['Date'],
                        "Description": row['Transaction Description'],
                        "Amount": clean_amount(row['Amount (inRs.)'])
                    })

    final_df = pd.DataFrame(transactions)
    # Remove any zero-amount transactions (like waivers)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df