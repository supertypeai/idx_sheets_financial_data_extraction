import pandas as pd
import numpy as np
import os
from supabase import create_client
from dotenv import load_dotenv
import json
import time
import time
from multiprocessing import Process
from idx_process import combine_technical_data, process_dataframe
from idx_scrape_url import fetch_url, get_data
import sys

load_dotenv()


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
  db_data = supabase.table("idx_active_company_profile").select("symbol").execute()
  df_db_data = pd.DataFrame(db_data.data)
  symbol_list : list = df_db_data['symbol'].unique().tolist()[:200]
  print(f"[DATABASE] Get {len(symbol_list)} data from database")

  length_list = len(symbol_list)
  i1 = int(length_list / 4)
  i2 = 2 * i1
  i3 = 3 * i1

  # Start time
  start = time.time()

  # Scraper Program
  # [LOOK] idx_scrape_url.py
  p1 = Process(target=get_data, args=(symbol_list[:i1], 1, year_arg))
  p2 = Process(target=get_data, args=(symbol_list[i1:i2], 2, year_arg))
  p3 = Process(target=get_data, args=(symbol_list[i2:i3], 3, year_arg))
  p4 = Process(target=get_data, args=(symbol_list[i3:], 4, year_arg))

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




  # Combine scrapped data
  all_data = combine_technical_data()

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

