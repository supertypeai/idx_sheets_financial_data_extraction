from urllib.request import urlopen
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import time
import os
import logging
import pandas as pd

# Set the logging level for the 'websockets' logger
logging.getLogger('websockets').setLevel(logging.WARNING)

# If you need to configure logging for requests-html as well
logging.getLogger('requests_html').setLevel(logging.WARNING)

BASE_URL = 'https://www.tradingview.com/symbols/IDX-'
JOURNAL_LIST = ['income-statement', 'balance-sheet', 'cash-flow']
PERIOD_LIST = ['statements-period=FY', 'statements-period=FQ']
DATA_DIR = os.path.join(os.getcwd(), "data")


INCOME_STATEMENT_COLUMN_MAPPING = {
  "total revenue" : "total_revenue",
  "net income" : "net_income",
  "ebit" : "ebit",
  "ebitda" : "ebitda",
  "diluted shares outstanding" : "diluted_shares_outstanding",
  "gross profit" : "gross_income",
  "pretax income" : "pretax_income",
  "taxes" : "income_taxes",
  "interest expense, net of interest capitalized" : "interest_expense_non_operating",
  "operating income" : "operating_income"
}
BALANCE_SHEET_COLUMN_MAPPING = {
  "total assets" : "total_assets",
  "total liabilities" : "total_liabilities",
  "total current liabilities" : "total_current_liabilities",
  "total equity" : "total_equity",
  "total debt" : "total_debt",
  "shareholders' equity" : "stockholders_equity",
  "cash and short term investments" : "cash_and_short_term_investments",
  "cash & equivalents" : "cash_only",
  "total cash & due from banks" : "total_cash_and_due_from_banks",
  "total non-current assets" : "total_non_current_assets",
}
CASH_FLOW_COLUMN_MAPPING = {
  "cash from operating activities" : "net_operating_cash_flow",
  "free cash flow" : "free_cash_flow",
}
COLUMN_MAPPING_LIST = [INCOME_STATEMENT_COLUMN_MAPPING, BALANCE_SHEET_COLUMN_MAPPING, CASH_FLOW_COLUMN_MAPPING]



def make_url(symbol: str, journal_idx: int = 0, period_idx : int = 0) -> str | None:
  if (journal_idx >= 0 and journal_idx <= 2 and period_idx >= 0 and period_idx <=1):
    journal = JOURNAL_LIST[journal_idx]
    statement_period = PERIOD_LIST[period_idx]
    return f"{BASE_URL}{symbol}/financials-{journal}/?{statement_period}"
  else:
    print(f"Invalid index: {journal_idx}")
    return None
  

def scrape_page(url : str) -> BeautifulSoup | None:
  try:
    session = HTMLSession()
    response = session.get(url)

    # Use JS Injection to get container items to be clicked
    # Number 10 is chosen to iterate (got from trial and error, changable)
    script = """
      () => {
        const itemsArray = []
        for (var j = 0; j < 10; j++){
          const items = document.getElementsByClassName("arrow-C9MdAMrq");
          if(items) {
            const len = items.length;
            for (var i = 0; i < len; i++){
              if (!itemsArray.includes(items[i])){
                itemsArray.push(items[i])
                items[i].click()
              }
            }
          }
        }

      }
    """
    response.html.render(sleep=1, timeout=5, script=script)

    soup = BeautifulSoup(response.html.html, "html.parser")

    print(f"[SESSION] Session for {url} is opened")
    return soup
  except Exception as e:
    print(f"[FAILED] Failed to scrape {url}: {e}")
    return None
  finally:
    session.close()
    print(f"[SESSION] Session for {url} is closed")

def get_table_from_page(soup: BeautifulSoup):
  table_elm = soup.find("div", {'class' : "container-vKM0WfUu"})
  return table_elm

def adjust_number_val_to_num(val: str) -> int | None :
  cleaning_dict = {
    "\u202a" : "", # Blank
    "\u202c" : "", # Blank
    "\u202f" : " ", # Whitespace
  }
  for k, v in cleaning_dict.items():
    val = val.replace(k, v)
  values = val.strip().split(" ")
  num_val = values[0]
  minus_val = False
  try:
    # Handle num
    num_vals = num_val.split(".")
    # Check None
    if ("—" == num_vals[0]):
      return None
    # Check minus
    if ("−" in num_vals[0]):
      num_vals[0] = num_vals[0].replace("−", "")
      minus_val = True
    result_num = int(num_vals[0].replace(",", ""))
    if (len(num_vals) == 2): # Should be 2 if there is a number behind comma
      decimal_length = len(num_vals[1])
      decimal_num = (int(num_vals[1]))/ (10**decimal_length)  
      result_num += decimal_num
    
    # Handle minus
    if (minus_val):
      result_num *= -1

    # Handle unit 
    if (len(values) == 2): # Length of 'values' should only be 1 or 2
      unit_val = values[1]
      if (unit_val == "T"):
        result_num *= (10**12)
      elif (unit_val == "B"):
        result_num *= (10**9)
      elif (unit_val == "M"):
        result_num *= (10**6)
      elif (unit_val == "K"):
        result_num *= (10**3)
    return int(result_num)
  except Exception as e:
    print(f"Failed to convert number val: {e}")
    return None
  
def adjust_dictionary_columns(data_dict: dict, journal_idx: int):
  # Adjustment to the table in the database
  data_length = len(data_dict['symbol'])
  used_column_mapping = COLUMN_MAPPING_LIST[journal_idx]
  # Handle for column null values
  for _, v in used_column_mapping.items():
    if (v not in data_dict):
      data_dict[v] = [None for _ in range(data_length)]
  return data_dict


def get_page_data(symbol: str, journal_idx: int, period_idx: int):
  # Logging
  print(f"[LOGGING] Getting data for Symbol {symbol}")
  if (journal_idx == 0):
    print(f"[LOGGING] Journal Type: Income Statement")
  elif (journal_idx == 1):
    print(f"[LOGGING] Journal Type: Balance Sheet")
  else: #(journal_idx == 2):
    print(f"[LOGGING] Journal Type: Cash Flow")
  if (period_idx == 0):
    print(f"[LOGGING] Period Type: Annual")
  else: #(period_idx == 1):
    print(f"[LOGGING] Period Type: Quarter")

  # Income Statement Data
  url = make_url(symbol, journal_idx, period_idx)
  html = scrape_page(url)
  if (html is not None):
    try:
      table_elm = get_table_from_page(html)
      data_dict = dict()
      is_any_ttm = False

      # Handle header/ title row
      period_list = []
      title_elm = table_elm.find("div", {"class" : 'container-OWKkVLyj'})
      vals = title_elm.findAll("div", {"class": "value-OxVAcLqi"})
      for period_val in vals:
        if(period_val.text == "TTM"): # Exclude getting TTM data
          is_any_ttm = True
        else:
          period_list.append(period_val.text)
        
      
      # Handle rows data
      rows_elm = table_elm.findAll("div", {"class": "container-C9MdAMrq"})
      for rows in rows_elm:
        data_name = rows['data-name'].lower()
        # Iterate column mapping dictionary to find the suitable and adjusted column name
        adjusted_data_name = None
        used_column_mapping = COLUMN_MAPPING_LIST[journal_idx]
        # Check if the data is the ones needed
        if (data_name in used_column_mapping):
          adjusted_data_name = used_column_mapping[data_name]
          # Iterate it the column of rows
          rows_values = rows.find("div", {"class": "values-C9MdAMrq"})
          values = rows_values.find_all("div", {"class" : "value-OxVAcLqi"})
          used_length = len(values)
          # Contain all values in a list
          value_container= list()
          # Exclude TTM data
          if (is_any_ttm):
            values = values[:-1]
            used_length -= 1
          for value in values:
            int_value = adjust_number_val_to_num(value.text)
            value_container.append(int_value)
          # Insert to consisting dictionary
          data_dict[adjusted_data_name] = value_container


      # Handle period data
      used_period_list = period_list[-used_length:]
      period_length = len(used_period_list)
      for i in range(period_length):
        period = used_period_list[i]
        if ("Q" in period):
          # Handle Quarter
          period_vals = period.split(" ")
          quarter = period_vals[0]
          period_year = period_vals[1].replace("\'", '')
          if (quarter == "Q1"):
            result_period = f"20{period_year}-03-31"
          elif (quarter == "Q2"):
            result_period = f"20{period_year}-06-30"
          elif (quarter == "Q3"):
            result_period = f"20{period_year}-09-30"
          else: # (quarter == "Q4"):
            result_period = f"20{period_year}-12-31"
        else:
          # Handle Annual
          result_period = f"{period}-12-31"
        used_period_list[i] = result_period
      data_dict['date'] = used_period_list

      # Handle symbol data
      data_dict['symbol'] = [f"{symbol}.JK" for _ in range(period_length)]

      # Handle Null data
      data_dict = adjust_dictionary_columns(data_dict, journal_idx)

      # Make dataframe
      dataframe = pd.DataFrame(data_dict)
      print(f"[SUCCESS] Successfully scrape page for stock {symbol}\n")
      return dataframe
    except Exception as e:
      print(f"[FAILED] Failed to scrape page {url}: {e}\n")
      return None
  else:
    print(f"[FAILED] Failed to open page {url}\n")
    return None
  
def iterate_scrape(symbol_list: list, process: int):
  annual_final_df = pd.DataFrame()
  quarter_final_df = pd.DataFrame()

  success_count = 0
  for symbol in symbol_list:
    for period_idx in range(2): # Iterate (0,1)
      
      # Adjusting
      if (".JK" in symbol):
        symbol = symbol.replace(".JK", "")

      is_data = get_page_data(symbol, 0, period_idx)
      bs_data = get_page_data(symbol, 1, period_idx)
      cf_data = get_page_data(symbol, 2, period_idx)

      if (is_data is not None and bs_data is not None and cf_data is not None):
        temp_df = pd.merge(is_data, bs_data, on=['symbol', 'date'], how='inner')
        stock_df = pd.merge(temp_df, cf_data, on=['symbol', 'date'], how='inner')

        if (success_count == 0):
          if (period_idx == 0):
            annual_final_df = stock_df
          else: # period_idx == 1
            quarter_final_df = stock_df
        else:
          if (period_idx == 0):
            annual_final_df = pd.concat([annual_final_df, stock_df], ignore_index = True)
          else: # period_idx == 1
            quarter_final_df = pd.concat([quarter_final_df, stock_df], ignore_index = True)
        print(f"[SUCCESS] Successfully combine data from {symbol} page")
        success_count += 1
      else:
        print(f"[FAILED] One or more page of {symbol} cannot be scrapped")
          
    print(f"[PROGRESS] Finished checking for {symbol} data\n")
    
  annual_final_df.to_csv(os.path.join(DATA_DIR, f"financials_annual_P{process}.csv"), index=False)
  quarter_final_df.to_csv(os.path.join(DATA_DIR, f"financials_quarter_P{process}.csv"), index=False)


# if __name__ == "__main__":
#   temp_dict = get_page_data('NICE', 0, 1)
#   for k, v in temp_dict.items():
#     print(k)
#     print(v)
  

