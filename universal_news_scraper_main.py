import pandas as pd
import ssl
import os
import sys
import time
from universal_news_scraper_scraper import handle_bloomberg, handle_cnbc, handle_cnn_edition, handle_ekonomi_bisnis, handle_finance_detik, handle_idn_financials, handle_idx ,handle_market_watch, handle_reuters, handle_yahoo_finance


URL_DICT = {
    "IDN_FINANCIALS" : {
      "url" : "https://www.idnfinancials.com/news/page/PAGE_IDX",
      "api_url" : None,
      "function" : handle_idn_financials
    },
    "CNBC" : {
      "url" : "https://www.cnbc.com/world/?region=world",  # No Pagination
      "api_url" : None,
      "function" : handle_cnbc
    },
    "YAHOO_FINANCE" : {
      "url" : "https://finance.yahoo.com/news/", # Infinite Scrolling by Scroll
      "api_url" : None,
      "function" : handle_yahoo_finance
    }, 
    "IDX" : {
      "url" : "https://www.idx.co.id/en/news/news?ds=&de=&qs=&p=PAGE_IDX",
      "api_url" : "https://www.idx.co.id/primary/NewsAnnouncement/GetNewsSearch?locale=en-us&pageNumber=PAGE_IDX&pageSize=12",
      "function" : handle_idx
    },
    "CNN_EDITION" : {
      "url" : "https://edition.cnn.com/business/economy",  # Pagination by Button Click (Load more)
      "api_url" : None,
      "function" : handle_cnn_edition
    },
    "FINANCE_DETIK" : {
      "url" : "https://finance.detik.com/indeks/PAGE_IDX",
      "api_url" : None,
      "function" : handle_finance_detik
    },
    "EKONOMI_BISNIS" : {
      "url" : "https://ekonomi.bisnis.com/",
      "api_url" : None,
      "function" : handle_ekonomi_bisnis
    },
    "MARKET_WATCH" : {
      "url" : "https://www.marketwatch.com/",  # Need Proxy, No Pagination
      "api_url" : None,
      "function" : handle_market_watch
    },
    "REUTERS" : {
      "url" : "https://www.reuters.com/markets/us/",  # Need Proxy
      "api_url" : None,
      "function" : handle_reuters
    },
    "BLOOMBERG" : {
      "url" : "https://www.bloomberg.com/asia", # No Pagination
      "api_url" : None,
      "function" : handle_bloomberg
    },
  }

def scrape_url_dict(start_idx: int, final_idx: int):
  idx = 0
  for k, v in URL_DICT.items():
    if (idx >= start_idx and idx < final_idx):
      print(f"[PROCESS] Processing for {k}")
      if (v['api_url'] is not None):
        dict_url = v['api_url']
      else:
        dict_url = v['url']

      dict_function = v['function']
      
      # Call the function
      dict_function(k, dict_url)

    idx +=1


if __name__ == "__main__":
  '''
  How to run:
  python <filename>.py <idx>
  Idx is the index of URL in the URL_LIST above.

  ex:
  python universal_news_scraper_main.py 3        #will run only the index 3 (IDX)
  python universal_news_scraper_main.py 1:4      #will run from index 1 to 3, similar to List Slicing

  valid idx = [0..6]
  0: IDN_FINANCIALS
  1: CNBC
  2: YAHOO_FINANCE
  3: IDX
  4: CNN_EDITION
  5: FINANCE_DETIK
  6: EKONOMI_BISNIS
  7: MARKET_WATCH       # Cannot be scrapped
  8: REUTERS            # Cannot be scrapped
  9: BLOOMBERG          # Cannot be scrapped

  '''
  if (sys.argv[1] is not None): 
    try:
      if (sys.argv[1] == "all"):
        input_idx = "0:10"
      else:
        input_idx = sys.argv[1]
      
      if (":" in input_idx):
        indices = input_idx.split(":")
        start_idx = int(indices[0])
        final_idx = int(indices[1])
      else:
        start_idx = int(input_idx)
        final_idx = start_idx + 1

      start = time.time()
      scrape_url_dict(start_idx, final_idx)

      end = time.time()
      duration = int(end-start)
      print(f"[FINISHED] The execution time: {time.strftime('%H:%M:%S', time.gmtime(duration))}")

    except Exception as e:
      print(f"[ERROR] Error in running the program: {e}")

  else:
    print(f"[ERROR] No args are passed. Terminating.")



