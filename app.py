import streamlit as st
import pandas as pd
import pdfplumber
import re
import os

# --- 1. Base Helper Function ---

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

# --- 2. Individual Parser Functions (All Corrected) ---

def parse_hdfc(pdf):
    """
    Parses HDFC. (Working)
    Uses standard table extraction.
    """
    transactions = []
    date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
    
    for page in pdf.pages:
        tables = page.extract_tables() 
        for table in tables:
            if not table: continue
            for row in table:
                if not row or len(row) < 3: continue
                
                date_str = str(row[0]).strip()
                desc_str = str(row[1])
                amount_str = str(row[2])
                
                if date_pattern.match(date_str) and desc_str and amount_str and "Transaction Description" not in desc_str:
                    amount = clean_amount(amount_str)
                    if amount != 0.0:
                        transactions.append({
                            "Date": date_str,
                            "Description": desc_str.replace('\n', ' '),
                            "Amount": amount
                        })

    if not transactions:
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df

def parse_icici_coral(pdf):
    """
    Parses ICICI Coral. (Working)
    This parser uses RegEx on the page's text.
    """
    transactions = []
    # RegEx to find: Date, Ref, Description, (Junk), Amount
    txn_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+\S+\s+(.+?)\s+\d*\s*.*?\s+([\d,\.]+\s*CR|[\d,\.]+)$')

    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
            
        for line in text.split('\n'):
            match = txn_pattern.search(line)
            if match:
                date_str = match.group(1)
                desc_str = match.group(2).strip()
                amount_str = match.group(3)
                
                if "Transaction Details" in desc_str:
                    continue
                    
                amount = clean_amount(amount_str)
                if amount != 0.0:
                    transactions.append({
                        "Date": date_str,
                        "Description": desc_str,
                        "Amount": amount
                    })

    if not transactions:
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df

def parse_axis(pdf):
    """
    Parses Axis My Zone. (FIXED)
    This parser uses RegEx on the page's text.
    """
    transactions = []
    # Pattern 1: Date, Description, Category, Amount
    pat_with_cat = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+[A-Za-z\s]+\s+([\d,\.]+\s*(?:Cr|Dr))$')
    # Pattern 2: Date, Description, Amount (no category, for "INTERNET PAYMENT")
    pat_no_cat = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(INTERNET PAYMENT.+?)\s+([\d,\.]+\s*(?:Cr|Dr))$')

    for page in pdf.pages:
        text = page.extract_text() # <-- REMOVED TOLERANCES
        if not text: continue
        
        for line in text.split('\n'):
            match_cat = pat_with_cat.search(line)
            match_no_cat = pat_no_cat.search(line)
            
            date_str, desc_str, amount_str = None, None, None

            if match_cat:
                date_str = match_cat.group(1)
                desc_str = match_cat.group(2).strip()
                amount_str = match_cat.group(3)
            elif match_no_cat:
                date_str = match_no_cat.group(1)
                desc_str = match_no_cat.group(2).strip()
                amount_str = match_no_cat.group(3)
            
            if date_str:
                amount = clean_amount(amount_str)
                if amount != 0.0:
                    transactions.append({
                        "Date": date_str,
                        "Description": desc_str,
                        "Amount": amount
                    })

    if not transactions:
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df

def parse_idfc(pdf):
    """
    Parses IDFC First Bank. (Working)
    This parser uses RegEx on the page's text.
    """
    transactions = []
    # RegEx to find lines that are NOT EMI amortization
    # Format: Date, Description, Amount
    txn_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,\.]+\s*CR|[\d,\.]+)$')
    
    for page in pdf.pages:
        text = page.extract_text() # <-- REMOVED TOLERANCES
        if not text:
            continue
        
        for line in text.split('\n'):
            # First, check if it's an excluded line
            if "Amortization" in line or "IGST" in line or "Interest charges" in line:
                continue
            
            # If not excluded, try to match as a transaction
            match = txn_pattern.search(line)
            if match:
                date_str = match.group(1)
                desc_str = match.group(2).strip()
                amount_str = match.group(3)

                amount = clean_amount(amount_str)
                if amount != 0.0:
                    transactions.append({
                        "Date": date_str,
                        "Description": desc_str,
                        "Amount": amount
                    })

    if not transactions:
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df

def parse_icici_amazon(pdf):
    """
    Parses ICICI Amazon Pay. (Working)
    Uses "text" table extraction.
    """
    transactions = []
    date_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')
    date_pattern_strict = re.compile(r'^\d{2}/\d{2}/\d{4}$') 

    for page in pdf.pages:
        tables = page.extract_tables({
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
        })
        for table in tables:
            if not table: continue
            for row in table:
                if not row: continue

                # Handle 5-column layout
                if len(row) >= 5:
                    date_str = str(row[0]).strip()
                    desc_str = str(row[2])
                    amount_str = str(row[4])
                    
                    if date_pattern_strict.match(date_str) and desc_str and "Transaction Details" not in desc_str:
                        amount = clean_amount(amount_str)
                        if amount != 0.0:
                            transactions.append({
                                "Date": date_str,
                                "Description": desc_str.replace('\n', ' '),
                                "Amount": amount
                            })
                
                # Handle 3-column layout
                elif len(row) >= 3:
                    col1 = str(row[0])
                    col2 = str(row[1])
                    col3 = str(row[2])
                    
                    date_match = date_pattern.search(col1)
                    
                    if date_match and col2 and "Transaction Details" not in col2:
                        date_str = date_match.group(1)
                        amount = clean_amount(col3)
                        
                        if amount != 0.0:
                            transactions.append({
                                "Date": date_str,
                                "Description": col2.replace('\n', ' '),
                                "Amount": amount
                            })

    if not transactions:
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    final_df = pd.DataFrame(transactions)
    final_df = final_df[final_df['Amount'] != 0.0].reset_index(drop=True)
    return final_df


# --- 3. Main Streamlit App ---

# --- Parser Mapping ---
PARSER_MAP = {
    "HDFC": parse_hdfc,
    "ICICI_CORAL": parse_icici_coral,
    "ICICI_AMAZON": parse_icici_amazon,
    "AXIS": parse_axis,
    "IDFC": parse_idfc,
}

def detect_bank(pdf):
    """
    Robust bank detection (FIXED)
    Extracts text from the first 2 pages to find keywords.
    """
    full_text = ""
    num_pages_to_check = min(len(pdf.pages), 2) # Check first 2 pages

    for i in range(num_pages_to_check):
        page = pdf.pages[i]
        # Use default extraction (no tolerances) for compressed PDFs
        text = page.extract_text() 
        if text:
            full_text += text.lower()
    
    # --- Axis Bank Check (NEW, more robust) ---
    if ("axis bank" in full_text or "axisbank" in full_text) and \
       ("my zone credit card" in full_text or "ambika shekhawat" in full_text or "axis edge" in full_text or "45145700" in full_text):
        return "AXIS"

    # --- ICICI Bank Check ---
    if "icici bank" in full_text:
        if "amazon pay" in full_text or "amazonpaycc@icicibank.com" in full_text:
            return "ICICI_AMAZON"
        if "coral" in full_text or "4375" in full_text: 
            return "ICICI_CORAL"
        return "ICICI_CORAL" # Default ICICI

    # --- HDFC Bank Check ---
    if "hdfc bank" in full_text:
        return "HDFC"
        
    # --- IDFC Bank Check ---
    if "idfc first" in full_text or "idfc first\n bank" in full_text:
        return "IDFC"
        
    return None

def main():
    st.set_page_config(layout="wide")
    st.title("💳 Credit Card Statement Parser")

    uploaded_file = st.file_uploader("Upload your PDF statement", type="pdf")

    if uploaded_file:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                
                bank = detect_bank(pdf) # Pass the whole pdf object
                
                if bank:
                    st.success(f"Detected: **{bank}**")
                    
                    try:
                        parser_function = PARSER_MAP[bank]
                        df = parser_function(pdf)
                        
                        if df.empty:
                            st.error(f"The parser for **{bank}** ran, but found 0 transactions. This file's layout may be unexpected.")
                        else:
                            st.subheader("Extracted Transactions")
                            st.dataframe(df)
                            
                            st.subheader("Data Summary")
                            total_spend = df[df['Amount'] > 0]['Amount'].sum()
                            total_payments = df[df['Amount'] < 0]['Amount'].sum()
                            st.metric("Total Spend (Debits)", f"₹{total_spend:,.2f}")
                            st.metric("Total Payments (Credits)", f"₹{total_payments:,.2f}")
                            
                    except Exception as e:
                        st.error(f"An error occurred while parsing the {bank} file: {e}")
                        
                else:
                    st.error("Could not determine bank from PDF. The file may be an unsupported or compressed PDF.")

        except Exception as e:
            st.error(f"Error reading PDF: {e}")

if __name__ == "__main__":
    main()