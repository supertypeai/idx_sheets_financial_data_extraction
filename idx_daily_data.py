import pandas as pd
import numpy as np
import urllib.request
import os
import json
import random
from datetime import datetime

DATA_DIR = os.path.join(os.getcwd(), "data")
API_URL = "https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0&date="

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
USER_AGENT_ALT_1 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'
USER_AGENT_ALT_2 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
USER_AGENT_LIST = [USER_AGENT, USER_AGENT_ALT_1, USER_AGENT_ALT_2]

HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

def create_headers():
  used_user_agent = random.choice(USER_AGENT_LIST)
  used_headers = HEADERS
  used_headers['User-Agent'] = used_user_agent
  # print(used_headers)
  return used_headers

def fetch_api_url(date: str):
  # period = ["tw1", "tw2", "tw3", "audit"]
  try:
    url = f"{API_URL}{date}"
    req = urllib.request.Request(url, headers=create_headers())
    resp = urllib.request.urlopen(req)
    status_code = resp.getcode()
    if (status_code == 200):
      data= resp.read()
      json_data = json.loads(data)['data']
      print(f"[SUCCESS] Successfully get the data")
      return json_data
    else:
      print(f"[FAILED] Failed to fetch from {url}. Get status code : {status_code}")
      return None
  except Exception as e:
    print(f"[FAILED] Failed to fetch from {url} : {e}")
    return None
  

if __name__ == "__main__":
  df = pd.read_csv(os.path.join(DATA_DIR, "non_symbol_list.csv"))
  symbol_list = df['symbol']

  date = "2024-09-03"
  adjusted_date = date.replace("-", "")
  list_data = fetch_api_url(adjusted_date)

  result_list = list()
  for symbol in symbol_list:
    adjusted_symbol = symbol.replace(".JK", "")
    found = False
    # Iterate list data
    for dict_data in list_data:
      if (dict_data['StockCode'] == adjusted_symbol):
        found = True
        print(f"[FOUND] Data for {adjusted_symbol} has been found.")
        updated_on = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        close = dict_data['Close']
        volume = dict_data['Volume']
        
        result_dict = {
          "symbol" : symbol, 
          "date" : date,
          "close" : close,
          "volume" : volume
        }
        result_list.append(result_dict)

    if (not found):
      print(f"[NOT FOUND] {adjusted_symbol} is not found!!")

  result_df = pd.DataFrame(result_list)
  filename_store = os.path.join(DATA_DIR, f"idx_daily_data_additional.csv")
  result_df.to_csv(filename_store, index = False)   
  print(f"[COMPLETED] The file data has been stored in {filename_store}")