import pandas as pd
import os

# Tries to open Excel File, return None if fails
def open_excel_file(filename: str, sheetname: str):
  try:
    df = pd.read_excel(filename, sheet_name=sheetname)
    return df
  except Exception as e:
    print(f'[WRONG FILE/ SHEET] Failed to open file {filename}: {e}')
    return None
  

DATA_TEMP = os.path.join(os.getcwd(), "data_temp")
filename = os.path.join(DATA_TEMP, "FinancialStatement-2024-I-UNVR.xlsx")

df = open_excel_file(filename, "1611000")

temp_df = df['Unnamed: 2']
print(temp_df)

for _, row in df.iterrows():
  if (row['Unnamed: 1'] == "Aset tetap"):
    print(row['Unnamed: 1'], row['Unnamed: 2'])