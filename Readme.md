# 💳 Credit Card Statement Parser

This project is a Streamlit web application that parses 5 different types of real-world credit card PDF statements.

### Assignment Brief

* **Objective:** Build a PDF parser to extract key data from 5 major credit card issuers.

* **Data Points:** Extract transaction information (Date, Description, Amount).

* **Providers:** HDFC Bank, Axis Bank, IDFC First Bank, ICICI Bank (Coral), and ICICI Bank (Amazon Pay).

### How to Run

1. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2. **Run the App:**

    ```bash
    streamlit run app.py
    ```

3. **Usage:**

    * The application will open in your browser.

    * Upload any of the 5 supported PDF statements.

    * The app auto-detects the bank and uses the correct parser.

    * It displays a table of extracted transactions and a summary of debits/credits.

### Implementation

* **Core App:** Built in Streamlit.

* **PDF Parsing:** Uses `pdfplumber` for robust table and text extraction.

* **Architecture:** A "pluggable" design:

    * `app.py`: Handles the UI, file upload, and bank detection.

    * `parsers/`: A folder containing a specific parser module for each bank.

    * `parsers/base_parser.py`: A shared utility for cleaning data (e.g., converting "500.00 Cr" to -500.0).

<img width="940" height="175" alt="image" src="https://github.com/user-attachments/assets/556751ec-1aec-4cde-a18e-adbfd64632fe" />
<img width="940" height="530" alt="image" src="https://github.com/user-attachments/assets/6b8b6afd-c24b-439b-bd84-860f1b00ed8d" />
<img width="940" height="493" alt="image" src="https://github.com/user-attachments/assets/8e26d319-f0ae-4293-80ab-0d4d84902b49" />
<img width="940" height="437" alt="image" src="https://github.com/user-attachments/assets/29d6e101-d75b-4034-8f0c-79f3493ea828" />
<img width="940" height="408" alt="image" src="https://github.com/user-attachments/assets/46346022-e79a-4c25-bea4-b01d2e77e55f" />

