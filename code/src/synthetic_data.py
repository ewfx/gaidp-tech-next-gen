# This Program generates synthetic data to be used in app.py

import pandas as pd
import numpy as np
import random
import string
from dotenv import load_dotenv
import os


# Function to generate random alphanumeric strings
def generate_alphanumeric(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
df = pd.DataFrame({
    "Identifier Type": np.random.choice(["CUSIP", "ISIN", "SEDOL"], size=100),
    "Identifier Value": [generate_alphanumeric(10) for _ in range(100)],
    "Amortized Cost": np.random.normal(75000, 15000, size=100),
    "Market Value (USD Equivalent)": np.random.normal(75000, 15000, size=100),
    "Accounting Intent": np.random.choice(["AFS", "HTM", "EQ"], size=100),
    "Type of Hedge(s)": np.random.choice(["1","2"], size=100),
    "Hedged Risk": np.random.choice(["1","2","3","4","5","6","7","8","9","10","11"], size=100),
    "Hedge Interest Rate": np.random.choice(["1","2","3","4","5"], size=100),
    "Hedge Percentage": np.random.choice([0.1,0,1,0.5,0.4,10], size=100),
    "Hedge Horizon": np.random.choice(["2025-01-01","2025-02-30","2025-29-02","2024-12-30","2024-11-10"], size=100),
    "Hedged Cash Flow": np.random.choice(["1","2","3","4","5","6"], size=100),
    "Sidedness": np.random.choice(["1","2","3","4"], size=100),
    "Hedging Instrument at Fair Value": np.random.randint(1800, 6500, size=100),
    "Effective Portion of Cumulative Gains and Losses": np.random.randint(10000, 80000, size=100),
    "Hedge Designations": np.random.choice(["1","2","3"], size=100),
    
    
    
})


#load_dotenv
load_dotenv()

# Fetch the environment variable
directory_path = os.getenv("DIRECTORY_PATH")


full_file_path = directory_path + '/dataset_hedge_test.csv'
print(full_file_path)

df.to_csv(full_file_path, index=False)

