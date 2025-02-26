from supabase import create_client
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv
import json

load_dotenv()

def preprocess(data):
    data_dict = json.loads(data)
    
    for k, v in data_dict.items():
       if (v is not None):
          data_dict[k] = int(v)

    return data_dict

if __name__ == "__main__":
  url_supabase = os.getenv("SUPABASE_URL")
  key = os.getenv("SUPABASE_KEY")
  supabase = create_client(url_supabase, key)
  
  df = pd.read_csv("data/data_annual.csv")
  df = df.drop(['industry_code'], axis=1)
  df = df.replace({np.nan: None})
  data_dict = df.to_dict(orient="records")

  for record in data_dict:
      # for k, v in record.items():
      #    print(k, v)

      try:
        # # UNCOMMENT TO INSERT QUARTER DATA
        # response = supabase.table("idx_financial_sheets_quarterly").insert(
        #   {
        #       'symbol' : record['symbol'],
        #       'date' : record['date'],
        #       'income_stmt_metrics' : preprocess(record['income_stmt_metrics'])  if record['income_stmt_metrics'] is not None else None,
        #       'balance_sheet_metrics' : preprocess(record['balance_sheet_metrics']) if record['balance_sheet_metrics'] is not None else None,
        #       'cash_flow_metrics' : preprocess(record['cash_flow_metrics']) if record['cash_flow_metrics'] is not None else None,
        #       'income_stmt_metrics_cumulative' : preprocess(record['income_stmt_metrics_cumulative']) if record['income_stmt_metrics_cumulative'] is not None else None
        #   }
        # ).execute()
        # print(f"[INSERT] Inserted {record['symbol']} {record['date']}")


        # UNCOMMENT TO INSERT ANNUAL DATA
        response = supabase.table("idx_financial_sheets_annual").insert(
          {
              'symbol' : record['symbol'],
              'date' : record['date'],
              'income_stmt_metrics' : preprocess(record['income_stmt_metrics'])  if record['income_stmt_metrics'] is not None else None,
              'balance_sheet_metrics' : preprocess(record['balance_sheet_metrics']) if record['balance_sheet_metrics'] is not None else None,
              'cash_flow_metrics' : preprocess(record['cash_flow_metrics']) if record['cash_flow_metrics'] is not None else None
          }
        ).execute()
        print(f"[INSERT] Inserted {record['symbol']} {record['date']}")

      except Exception as e:
        print(f"[FAILED] Failed to insert {record['symbol']} {record['date']} to Database: {e}")

  print(f"[SUCCESS] Successfully insert {len(data_dict)} data to database")

