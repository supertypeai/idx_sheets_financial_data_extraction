import pandas as pd
import numpy as np
import urllib.request
import os
from supabase import create_client
from dotenv import load_dotenv
import json
import time
from datetime import datetime
import time
from multiprocessing import Process
from idx_process import combine_technical_data, process_dataframe
from idx_utils import DATA_DIR, BASE_URL, PERIOD_LIST, create_headers
import sys


load_dotenv()


def fetch_url(period: str, symbol: str, year: str, process: int):
  # period = ["tw1", "tw2", "tw3", "audit"]
  try:
    url = f"{BASE_URL}/primary/ListedCompany/GetFinancialReport?year={year}&reportType=rdf&EmitenType=s&periode={period}&kodeEmiten={symbol.upper()}&SortColumn=KodeEmiten&SortOrder=asc"

    req = urllib.request.Request(url, headers=create_headers())
    resp = urllib.request.urlopen(req)
    status_code = resp.getcode()
    if (status_code == 200):
      data= resp.read()
      json_data = json.loads(data)
      if (json_data['ResultCount'] > 0):
        print(f"[SUCCESS P{process}] Successfully get the data from stock {symbol}, year {year}, period {period}")
        return json_data
      else:
        print(f"[FAILED P{process}] Data is not available for stock {symbol}, year {year}, period {period}")
        return None
    else:
      print(f"[FAILED P{process}] Failed to fetch from {url}. Get status code : {status_code}")
      return None
  except Exception as e:
    print(f"[FAILED P{process}] Failed to fetch from {url} : {e}")
    return None
  
def get_data(symbol_list: list, process: int, year : int = None):
  RESULT_LIST = []
  count = 0
  # If year is None, use the current year
  current_year = datetime.now().strftime("%Y") if year is None else year
  for symbol in symbol_list:
    adjusted_symbol = symbol.replace(".JK", "")

    # Adjust this recuring year
    YEAR_RANGE = 0
    # YEAR_RANGE == 0 if only want to fetch current year data
    for recuring_year in range(int(current_year), int(current_year) + YEAR_RANGE + 1):
      for period in PERIOD_LIST:
        json_data = fetch_url(period, adjusted_symbol, recuring_year, process)
        if (json_data is not None):
          data_list = json_data["Results"][0]["Attachments"]

          for data in data_list:
            if (data['File_Type'] == ".xlsx" and "FinancialStatement" in data['File_Name']):
              # Adjust period name
              if (period == "audit"):
                adjusted_period = "tw4"
              else:
                adjusted_period = period
                
              data_dict = {
                "symbol" : symbol,
                "year" : recuring_year,
                "period" : adjusted_period,
                "file_name" : data['File_Name'],
                "file_url" : data['File_Path']
              }
              RESULT_LIST.append(data_dict)

        time.sleep(1.5)

    count +=1
    if (count % 20 == 0):
      print(f"[CHECKPOINT] P{process} has covered {count} data")

  dataframe = pd.DataFrame(RESULT_LIST)
  filename_store = os.path.join(DATA_DIR, f"idx_url_scrapped_list_P{process}.csv")
  dataframe.to_csv(filename_store, index = False)   
  print(f"[COMPLETED] The file data has been stored in {filename_store}")


if __name__ == "__main__":

  # Connection to Supabase
  url_supabase = os.getenv("SUPABASE_URL")
  key = os.getenv("SUPABASE_KEY")
  supabase = create_client(url_supabase, key)

  # Read running argument
  if (len(sys.argv) == 1):
    year_arg  = None
  else:
    year_arg = int(sys.argv[1])

  # Get the table
  db_data = supabase.table("idx_active_company_profile").select("symbol").in_("current_source", [-1, 2]).execute()
  df_db_data = pd.DataFrame(db_data.data)
  symbol_list : list = df_db_data['symbol'].unique().tolist()
  print(f"[DATABASE] Get {len(symbol_list)} data from database")

  length_list = len(symbol_list)
  i1 = int(length_list / 4)
  i2 = 2 * i1
  i3 = 3 * i1

  # Start time
  start = time.time()

  # # Scraper Program
  # p1 = Process(target=get_data, args=(symbol_list[:i1], 1, year_arg))
  # p2 = Process(target=get_data, args=(symbol_list[i1:i2], 2, year_arg))
  # p3 = Process(target=get_data, args=(symbol_list[i2:i3], 3, year_arg))
  # p4 = Process(target=get_data, args=(symbol_list[i3:], 4, year_arg))

  # p1.start()
  # p2.start()
  # time.sleep(1)
  # p3.start()
  # p4.start()

  # p1.join()
  # p2.join()
  # p3.join()
  # p4.join()

  # End time
  end_scraping = time.time()
  scraping_duration = int(end_scraping-start)
  print(f"The scraping execution time: {time.strftime('%H:%M:%S', time.gmtime(scraping_duration))}")

  # Combine scrapped data
  all_data = combine_technical_data()

  # Use multiprocess to increase efficiency
  length_list = len(all_data)
  i1 = int(length_list / 4)
  i2 = 2 * i1
  i3 = 3 * i1

  # Process Program
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

