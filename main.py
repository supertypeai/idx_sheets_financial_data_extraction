import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv
import time
import time
from multiprocessing import Process
from idx_process import  process_dataframe
from idx_scrape_url import fetch_url, get_data
import sys
from idx_utils import PERIOD_LIST, DATA_IDX_URL_DIR, DATA_PROCESSED_DIR, DATA_RESULT_DIR
from datetime import datetime, timedelta

load_dotenv()

'''
HOW TO START:
=> For automatic start:
python main.py

Automatic start will try to get the data from the last half year. #needs to be edited


=> For manual start:
program requires two parameters: {year} and {period}
Period => see PERIOD_LIST in idx_utils.py

example: 2024 tw1

To Run:
python main.py 2024 tw1
'''

# Combine scrapped data from the csv files
def combine_url_data():
  failed_file_path = [os.path.join(DATA_IDX_URL_DIR,f'failed_list_P{i}.csv') for i in range(1,5)]
  data_file_path = [os.path.join(DATA_IDX_URL_DIR,f'scrapped_list_P{i}.csv') for i in range(1,5)]

  # Combine data
  all_data = pd.DataFrame()
  failed_data = pd.DataFrame()

  for i in range(len(data_file_path)):
    try:
      file_path = data_file_path[i]
      df = pd.read_csv(file_path)
      if (i == 0):
        all_data = df
      else:
        all_data = pd.concat([all_data, df])
    except Exception as e:
      print(f"[FAILED] Failed to process DataFrame on {file_path}")

  # Combine failed data
  for i in range(len(failed_file_path)):
    try:
      file_path = failed_file_path[i]
      df = pd.read_csv(file_path)
      if (i == 0):
        failed_data = df
      else:
        failed_data = pd.concat([failed_data, df])
      os.remove(file_path)
    except Exception as e:
      print(f"[FAILED] Failed to process DataFrame on {file_path}")
  failed_data.to_csv(os.path.join(DATA_RESULT_DIR, 'data_failed.csv'), index=False)

  return all_data

def combine_processed_data():
  bank_data = pd.DataFrame()
  non_bank_data = pd.DataFrame()

  files_path =  [os.path.join(DATA_PROCESSED_DIR, filename) for filename in os.listdir(os.path.join(DATA_PROCESSED_DIR))]
  try:
    for filename in files_path:
      if ".csv" in filename:
        df = pd.read_csv(filename)

        if ("non_bank" in filename):
          if (len(non_bank_data) == 0):
            non_bank_data = df
          else:
            non_bank_data = pd.concat([non_bank_data, df])

        else : # for banks
          if (len(bank_data) == 0):
            bank_data = df
          else:
            bank_data = pd.concat([bank_data, df])

    # Save
    bank_data = bank_data.drop(['industry_code'], axis=1)
    bank_data.to_csv(os.path.join(DATA_RESULT_DIR, "data_bank.csv"), index=False)

    non_bank_data = non_bank_data.drop(['industry_code'], axis=1)
    non_bank_data.to_csv(os.path.join(DATA_RESULT_DIR, "data_non_bank.csv"), index=False)

    return bank_data, non_bank_data

  except Exception as e:
    print(f"[FAILED] Failed to combine processed Data.")





if __name__ == "__main__":

  # Connection to Supabase
  url_supabase = os.getenv("SUPABASE_URL")
  key = os.getenv("SUPABASE_KEY")
  supabase = create_client(url_supabase, key)

  
  if (len(sys.argv) > 1):
    assert len(sys.argv) == 3, "[ERROR] Invalid argument input!"

    # Read running argument
    year_arg = int(sys.argv[1])
    period_arg = sys.argv[2]
  
    assert period_arg in PERIOD_LIST, "[ERROR] Invalid period argument!"

  else:

    current_time = datetime.now()
    last_quarter = current_time - timedelta(30 * 6)
    month = int(last_quarter.month)
    month_arg_idx = max((month - 1)//3, 0)
    period_arg = PERIOD_LIST[month_arg_idx]
    year_arg = int(last_quarter.year)
    
  # Get the table
  db_data = supabase.table("idx_active_company_profile").select("symbol").execute()
  df_db_data = pd.DataFrame(db_data.data)
  symbol_list : list = df_db_data['symbol'].unique().tolist()[:300]
  print(f"[DATABASE] Get {len(symbol_list)} data from database")

  length_list = len(symbol_list)
  i1 = int(length_list / 4)
  i2 = 2 * i1
  i3 = 3 * i1

  # Start time
  start = time.time()

  # Scraper Program
  # [LOOK] idx_scrape_url.py
  p1 = Process(target=get_data, args=(symbol_list[:i1], 1, year_arg, period_arg))
  p2 = Process(target=get_data, args=(symbol_list[i1:i2], 2, year_arg, period_arg))
  p3 = Process(target=get_data, args=(symbol_list[i2:i3], 3, year_arg, period_arg))
  p4 = Process(target=get_data, args=(symbol_list[i3:], 4, year_arg, period_arg))

  p1.start()
  p2.start()
  time.sleep(1)
  p3.start()
  p4.start()

  p1.join()
  p2.join()
  p3.join()
  p4.join()

  # End time
  end_scraping = time.time()
  scraping_duration = int(end_scraping-start)
  print(f"The scraping execution time: {time.strftime('%H:%M:%S', time.gmtime(scraping_duration))}")

  print("test")

  # Combine scrapped data
  all_data = combine_url_data()

  # Use multiprocess to increase efficiency
  length_list = len(all_data)
  i1 = int(length_list / 4)
  i2 = 2 * i1
  i3 = 3 * i1

  # Process Program
  # [LOOK] idx_process.py
  p1 = Process(target=process_dataframe, args=(all_data[:i1], 1))
  p2 = Process(target=process_dataframe, args=(all_data[i1:i2], 2))
  p3 = Process(target=process_dataframe, args=(all_data[i2:i3], 3))
  p4 = Process(target=process_dataframe, args=(all_data[i3:], 4))

  p1.start()
  p2.start()
  p3.start()
  p4.start()

  p1.join()
  p2.join()
  p3.join()
  p4.join()

  # End time
  end_processing = time.time()
  processing_duration = int(end_processing-end_scraping)
  print(f"The processing execution time: {time.strftime('%H:%M:%S', time.gmtime(processing_duration))}")

  # Combine processed data
  bank_data, non_bank_data = combine_processed_data()



