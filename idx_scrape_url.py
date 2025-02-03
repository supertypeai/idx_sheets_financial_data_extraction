from idx_utils import DATA_RESULT_DIR, DATA_IDX_URL_DIR, BASE_URL, PERIOD_LIST, create_headers
import urllib.request
import json
import time
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import warnings

load_dotenv()

warnings.simplefilter(action='ignore', category=UserWarning)

PROXY_URL = os.getenv("proxy")
PROXIES = {
    'http': PROXY_URL,
    'https': PROXY_URL,
}


def fetch_url(period: str, symbol: str, year: str, process: int, use_proxy : bool = False):
  # period = ["tw1", "tw2", "tw3", "audit"]
  try:
    url = f"{BASE_URL}/primary/ListedCompany/GetFinancialReport?year={year}&reportType=rdf&EmitenType=s&periode={period}&kodeEmiten={symbol.upper()}&SortColumn=KodeEmiten&SortOrder=asc"

    if (not use_proxy):
      req = urllib.request.Request(url, headers=create_headers())
      resp = urllib.request.urlopen(req)
      status_code = resp.getcode()
    else:
      response = requests.get(url, proxies=PROXIES, verify=False)   
      status_code = response.status_code

    if (status_code == 200):
      if (not use_proxy):
        data= resp.read()
        json_data = json.loads(data)
      else:
        json_data = response.json()

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
  FAILED_LIST = []
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
        json_data = fetch_url(period, adjusted_symbol, recuring_year, process, False)
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

        else:
          data_dict = {
              "symbol" : symbol,
              "year" : recuring_year,
              "period" : adjusted_period,
            }
          FAILED_LIST.append(data_dict)

        time.sleep(1.5)

    count +=1
    if (count % 20 == 0):
      print(f"[CHECKPOINT] P{process} has covered {count} data")

  dataframe = pd.DataFrame(RESULT_LIST)
  filename_store = os.path.join(DATA_IDX_URL_DIR, f"scrapped_list_P{process}.csv")
  dataframe.to_csv(filename_store, index = False)   

  failed_datafrane = pd.DataFrame(FAILED_LIST)
  failed_filename = os.path.join(DATA_IDX_URL_DIR, f"failed_list_P{process}.csv")
  failed_datafrane.to_csv(failed_filename, index= False)
  print(f"[COMPLETED] The file data has been stored in {filename_store}")
