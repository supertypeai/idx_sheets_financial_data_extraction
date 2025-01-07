import urllib.request
from bs4 import BeautifulSoup
import os
import pandas as pd
import json
import time
from multiprocessing import Process

DATA_DIR = os.path.join(os.getcwd(), "data")
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer" : "https://www.wsj.com/",
        'x-test': 'true'
    }

def fetch_url(url):
  req = urllib.request.Request(url, headers=HEADERS)
  resp = urllib.request.urlopen(req)
  status_code = resp.getcode()
  if (status_code == 200):
    data = resp.read()
    soup = BeautifulSoup(data, "html.parser")
    return soup
  else:
    print(f"Failed to fetch from {url}. Get status code : {status_code}")
    return None


def check_yf(symbol_list_partial : list, process : int):
  count = 0
  AVAILABLE_LIST = []
  NOT_AVAILABLE_LIST = []
  MAX_ATTEMPT = 3
  for symbol in symbol_list_partial:
    attempt = 1
    found = False
    while (not found and attempt <= 3):
      print(f"Checking Symbol {symbol}")
      url = f"https://ca.finance.yahoo.com/quote/{symbol}/financials/"
      soup = fetch_url(url)
      if (soup is not None):
        section_div = soup.find("section", {"class" : "smartphone_Px(20px)"})
        if (section_div is not None):
          rows = section_div.find_all("div", {"class" : "rw-expnded"})
          if (len(rows) > 0):
            AVAILABLE_LIST.append(symbol)
            found = True
            print(f"[SUCCESS] {symbol}")
          else:
            print(f"[NONE] {symbol} : Rows length is 0")
        else:
          print(f"[NONE] {symbol} : Section_div is None ")
      else:
        print(f"[NONE] {symbol} : Soup is None")

      if (not found):
        print(f"Failed to get data {symbol} on attempt {attempt}. Retrying...")
        if (attempt == 3):
          NOT_AVAILABLE_LIST.append(symbol)
          print(f"Failed to get data from {symbol} after maximum attempts {attempt}")
      attempt += 1
    time.sleep(0.5)

    count += 1
    if (count % 20 == 0):
      print(f"Process {process} checkpoint! {count} data ")
  print(f"Process {process} is done.")

  with open(os.path.join(DATA_DIR, f"available_yf_P{process}.json"), "w") as final:
    json.dump(AVAILABLE_LIST, final, indent=2)
  with open(os.path.join(DATA_DIR, f"not_available_yf_P{process}.json"), "w") as final:
    json.dump(NOT_AVAILABLE_LIST, final, indent=2)


if __name__ == "__main__":
  df = pd.read_csv(os.path.join(DATA_DIR, "need_search.csv"))
  symbol_list = df['symbol'].tolist()

  length_list = len(symbol_list)
  i1 = int(length_list / 4)
  i2 = 2 * i1
  i3 = 3 * i1

  start = time.time()

  p1 = Process(target=check_yf, args=(symbol_list[:i1], 1))
  p2 = Process(target=check_yf, args=(symbol_list[i1:i2], 2))
  p3 = Process(target=check_yf, args=(symbol_list[i2:i3], 3))
  p4 = Process(target=check_yf, args=(symbol_list[i3:], 4))

  p1.start()
  p2.start()
  p3.start()
  p4.start()

  p1.join()
  p2.join()
  p3.join()
  p4.join()


  end = time.time()
  duration = int(end-start)
  print(f"The execution time: {time.strftime('%H:%M:%S', time.gmtime(duration))}")
  print("==> FINISHED CHECKING")