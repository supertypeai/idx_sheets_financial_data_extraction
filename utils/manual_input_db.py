from supabase import create_client
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv
import json

load_dotenv()

if __name__ == "__main__":
  url_supabase = os.getenv("SUPABASE_URL")
  key = os.getenv("SUPABASE_KEY")
  supabase = create_client(url_supabase, key)
  
  df = pd.read_csv("data/data_quarter.csv")
  df = df.drop(['industry_code'], axis=1)
  df = df.replace({np.nan: None})
  data_dict = df.to_dict(orient="records")

  supabase.table("idx_financials_sheets_quarterly").upsert(data_dict).execute()

  # # try:
  # for record in data_dict:
  #     # for k, v in record.items():
  #     #    print(k, v)

  #     # print(record['income_stmt_metrics'], len(record['income_stmt_metrics']))
  #     # record['balance_sheet_metrics'] = json.loads(record['balance_sheet_metrics'])
  #     # record['income_stmt_metrics'] = json.loads(record['income_stmt_metrics'])
  #     # record['cash_flow_metrics'] = json.loads(record['cash_flow_metrics'])
  #     # record['income_stmt_metrics_cumulative'] = json.loads(record['income_stmt_metrics_cumulative'])
  #     # print(record['income_stmt_metrics'], len(record['income_stmt_metrics']))

  #     supabase.table("idx_financials_sheets_quarterly").insert(record).execute()
  #     print(f"[INSERT] Inserted {record['symbol']}")

  # print(f"[SUCCESS] Successfully insert {len(data_dict)} data to database")

  # # except Exception as e:
  # #   print(f"[FAILED] Failed to insert to Database: {e}")