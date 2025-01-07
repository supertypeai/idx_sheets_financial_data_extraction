from urllib.request import urlopen
import json
import os
import pandas as pd
import time
from multiprocessing import Process
from scraper_trading_view_financials import make_url, iterate_scrape


DATA_DIR = os.path.join(os.getcwd(), "data")

# def iterate_symbol_scrape(symbol_list: list, process: int):
#   result_dict = dict()
#   count = 1
#   for symbol in symbol_list:
#     adjusted_symbol = symbol.replace(".JK", "")
#     result_dict[symbol] = dict()
#     count_false = 0
    
#     is_fy_url = make_url(adjusted_symbol, 0, 0)
#     bs_fy_url = make_url(adjusted_symbol, 1, 0)
#     cf_fy_url = make_url(adjusted_symbol, 2, 0)
#     is_fq_url = make_url(adjusted_symbol, 0, 1)
#     bs_fq_url = make_url(adjusted_symbol, 1, 1)
#     cf_fq_url = make_url(adjusted_symbol, 2, 1)

#     is_fy_data = get_income_statement_data(is_fy_url)
#     is_fq_data = get_income_statement_data(is_fq_url)
#     bs_fy_data = get_balance_sheet_data(bs_fy_url)
#     bs_fq_data = get_balance_sheet_data(bs_fq_url)
#     cf_fy_data = get_cash_flow_data(cf_fy_url)
#     cf_fq_data = get_cash_flow_data(cf_fq_url)

#     if (is_fy_data is not None):
#       result_dict[symbol]['income_statement_annual'] = True
#       print(f"[SUCCESS] Successfully get {symbol} annual income statment data")
#     else:
#       count_false += 1
#       result_dict[symbol]['income_statement_annual'] = False

#     if (is_fq_data is not None):
#       result_dict[symbol]['income_statement_quarter'] = True
#       print(f"[SUCCESS] Successfully get {symbol} quarter income statment data")
#     else:
#       count_false += 1
#       result_dict[symbol]['income_statement_quarter'] = False
    
#     if (bs_fy_data is not None):
#       result_dict[symbol]['balance_sheet_annual'] = True
#       print(f"[SUCCESS] Successfully get {symbol} annual annual sheet data")
#     else:
#       count_false += 1
#       result_dict[symbol]['balance_sheet_annual'] = False

#     if (bs_fq_data is not None):
#       result_dict[symbol]['balance_sheet_quarter'] = True
#       print(f"[SUCCESS] Successfully get {symbol} quarter balance sheet data")
#     else:
#       count_false += 1
#       result_dict[symbol]['balance_sheet_quarter'] = False

#     if (cf_fy_data is not None):
#       result_dict[symbol]['cash_flow_annual'] = True
#       print(f"[SUCCESS] Successfully get {symbol} annual cash flow data")
#     else:
#       count_false += 1
#       result_dict[symbol]['cash_flow_annual'] = False

#     if (cf_fq_data is not None):
#       result_dict[symbol]['cash_flow_quarter'] = True
#       print(f"[SUCCESS] Successfully get {symbol} quarter cash flow data")
#     else:
#       count_false += 1
#       result_dict[symbol]['cash_flow_quarter'] = False

#     if (count_false == 0):
#       result_dict[symbol]['is_data_complete'] = True
#       print(f"[ULTRA SUCCESS] Successfully get all {symbol} data")
#     else:
#       result_dict[symbol]['is_data_complete'] = False

#     if (count % 20 == 0):
#       print(f"Checkpoint on P{process}: {count} data")
#       with open(os.path.join(DATA_DIR, f"check_availability_tv_P{process}.json"), 'w') as fp:
#         json.dump(result_dict, fp, indent=2)
#     count +=1
  
#   with open(os.path.join(DATA_DIR, f"check_availability_tv_P{process}.json"), 'w') as fp:
#     json.dump(result_dict, fp, indent=2)


if __name__ == "__main__":
  df = pd.read_csv(os.path.join(DATA_DIR, "need_search.csv"))
  symbol_list = df['symbol'].tolist()

  symbol_list = symbol_list[:40]
  length_list = len(symbol_list)
  i1 = int(length_list / 4)
  i2 = 2 * i1
  i3 = 3 * i1

  start = time.time()

  p1 = Process(target=iterate_scrape, args=(symbol_list[:i1], 1))
  p2 = Process(target=iterate_scrape, args=(symbol_list[i1:i2], 2))
  p3 = Process(target=iterate_scrape, args=(symbol_list[i2:i3], 3))
  p4 = Process(target=iterate_scrape, args=(symbol_list[i3:], 4))

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
  print(f"[FINISHED] The execution time: {time.strftime('%H:%M:%S', time.gmtime(duration))}")

  



    