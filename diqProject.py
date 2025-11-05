import pandas as pd
from pandasgui import show
import numpy as np
import os

# ANSI color codes
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(SCRIPT_DIR, "Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv")

def load_data(file_path):
    """Load data from a CSV file into a pandas DataFrame."""
    try:
        data = pd.read_csv(file_path, sep=';', encoding='utf-16')
        print(f"Data loaded successfully from {file_path}")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    

def dataProfiling(data):
    """Perform basic data profiling."""
    
    # Set display options for better formatting
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 50)

    # Dataset shape printout
    print(RED + "="*100)
    print("=" + " "*98 + "=")
    print("=" + "DATASET SHAPE".center(98) + "=")
    print("=" + " "*98 + "=")
    print("="*100 + RESET + "\n")
    print(f"Rows: {data.shape[0]}")
    print(f"Columns: {data.shape[1]}")
    print(f"Total cells: {data.shape[0] * data.shape[1]}")
    print("\n")

    # Data head printout
    print(RED + "="*100)
    print("=" + " "*98 + "=")
    print("=" + "DATA HEAD".center(98) + "=")
    print("=" + " "*98 + "=")
    print("="*100 + RESET + "\n")
    print(data.head().to_string())
    print("\n")

    # Columns names printout
    print(RED + "="*100)
    print("=" + " "*98 + "=")
    print("=" + "COLUMNS NAMES".center(98) + "=")
    print("=" + " "*98 + "=")
    print("="*100 + RESET)
    print(f"Total columns: {len(data.columns)}\n")
    for i, col in enumerate(data.columns, 1):
        print(f"{i:2d}. {col}")
    print("\n")

    # Data types printout
    print(RED + "="*100)
    print("=" + " "*98 + "=")
    print("=" + "DATA TYPES AND MISSING VALUES SUMMARY".center(98) + "=")
    print("=" + " "*98 + "=")
    print("="*100 + RESET)
    dtypes_df = pd.DataFrame({
        'Column': data.dtypes.index,
        'Data Type': data.dtypes.values,
        'Distinct Count': data.nunique().values,
        'Non-Null Count': data.count().values,
        'Null Count': data.isnull().sum().values,
        'Missing %': (data.isnull().sum() / len(data) * 100).round(2).values
    })
    print(dtypes_df.to_string(index=False))
    print(f"\nTotal missing values: {data.isnull().sum().sum()}")
    print("\n")


    # Statistical summary printout
    """print("\n" + RED + "="*100)
    #print("=" + " "*98 + "=")
    #print("=" + " STATISTICAL SUMMARY (Superficie somministrazione)".center(98) + "=")
    #print("=" + " "*98 + "=")
    #print("="*100 + RESET + "\n")
    #print(data["Superficie somministrazione"].describe().transpose().to_string())
    #print("\n")"""


def valueBalanceAnalysis(data, top_n=20):
    """Analyze value balance for each column showing duplicates, unique values, and percentages.
    top_n: Number of top values to display per column.
    """

    print("\n" + RED + "="*100)
    print("=" + " "*98 + "=")
    print("=" + "VALUE BALANCE ANALYSIS".center(98) + "=")
    print("=" + " "*98 + "=")
    print("="*100 + RESET + "\n")

    tot_value_counts = data.size
    tot_NAN_value_counts_notNaN = data.isnull().sum().sum()
    tot_NotNAN_value_counts = data.size - data.isnull().sum().sum()
    tot_unique_counts = data.nunique().sum() - data.isnull().sum().sum()
    tot_duplicate_counts = tot_value_counts - tot_unique_counts
    tot_duplicate_percentage = round(tot_duplicate_counts / tot_value_counts * 100, 2)  

    print(f"Total values: {tot_value_counts}")
    print(f"Total null values: {tot_NAN_value_counts_notNaN}")
    print(f"Total values (not null): {tot_NotNAN_value_counts}")
    print(f"Total unique values (not null): {tot_unique_counts}")
    print(f"Total duplicate values (not null): {tot_duplicate_counts}")
    print(f"Total duplicate percentage (not null): {tot_duplicate_percentage}%")
    print("\n")

    for col in data.columns:
        print(CYAN + '='*40 + RESET)
        print(f"Column: {col}")
        print(CYAN + '='*40 + RESET)

        # Calculate value counts (excluding NaN from display)
        value_counts = data[col].value_counts(dropna=True)
        total_values = len(data[col])
        unique_values = data[col].nunique(dropna=True)
        
        # Add column summary
        print(f"\nTotal rows: {total_values}")
        print(f"Unique values: {unique_values}")
        print(f"Duplicate percentage: {round((total_values - unique_values) / total_values * 100, 2)}%")
        
        # Show top N values or all if fewer than top_n
        if unique_values <= top_n:
            # Show all values
            balance_df = pd.DataFrame({
                'Value': value_counts.index,
                'Count': value_counts.values,
                'Percentage': (value_counts.values / total_values * 100).round(2)
            })
            print(f"\nValue distribution (all {unique_values} values):")
            print(balance_df.to_string(index=False))
        else:
            # Show top N values
            top_values = value_counts.head(top_n)
            balance_df = pd.DataFrame({
                'Value': top_values.index,
                'Count': top_values.values,
                'Percentage': (top_values.values / total_values * 100).round(2)
            })
            
            # Calculate stats for remaining values
            remaining_count = unique_values - top_n
            remaining_total = value_counts.iloc[top_n:].sum()
            remaining_percentage = round(remaining_total / total_values * 100, 2)
            
            print(f"\nValue distribution (top {top_n} of {unique_values} values):")
            print(balance_df.to_string(index=False))
            print(f"\n... and {remaining_count} other values accounting for {remaining_total} rows ({remaining_percentage}%)")
        
        print("\n")


    

if __name__ == "__main__":
    data = load_data(FILE_PATH)
    if data is not None:
        dataProfiling(data)
        valueBalanceAnalysis(data)

