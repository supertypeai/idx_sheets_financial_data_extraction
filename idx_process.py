import os
import pandas as pd
import numpy as np
import time
import urllib
from idx_mapping_constant import ROUNDING_LEVEL_MAPPING, UNIVERSAL_MAPPING, BALANCE_SHEET_METRICS, INCOME_STATEMENT_METRICS, CASH_FLOW_METRICS
from idx_utils import DATA_IDX_SHEETS_DIR, DATA_IDX_URL_DIR, DATA_RESULT_DIR, BASE_URL, create_headers
import warnings
import urllib.request
import openpyxl as xl 

warnings.simplefilter(action='ignore', category=UserWarning)


# Make general function to be used in adding None
# none_to_zero == True -> assuming None is equal to 0 -> None (operation) num = num
# none_to_zero == False -> None (operation) num = None
def none_handling_operation(num1: float, num2: float, operation: str, none_to_zero : bool = False):
  # Generalize None type
  none_num1 = False
  none_num2 = False
  if (num1 is None or np.isnan(num1)):
    none_num1 = True
  if (num2 is None or np.isnan(num2)):
    none_num2 = True
  
  # Check and Calculate
  if (none_num1 and none_num2):
    return None
  else:
    if (none_num1):
      return num2 if none_to_zero else None
    elif (none_num2):
      return num1 if none_to_zero else None
    else:
      # Correct condition
      if (operation == "+"):
        return num1 + num2
      elif (operation == "-"):
        return num1 - num2
      elif (operation == "/"):
        return num1 / num2
      elif (operation == "*"):
        return num1 * num2

# Combine scrapped data from the csv files
def combine_technical_data ():
  data_file_path = [os.path.join(DATA_IDX_URL_DIR,f'idx_url_scrapped_list_P{i}.csv') for i in range(1,5)]

  # Combine data
  all_data = pd.DataFrame()
  for i in range(len(data_file_path)):
    file_path = data_file_path[i]
    df = pd.read_csv(file_path)
    if (i == 0):
      all_data = df
    else:
      all_data = pd.concat([all_data, df])

  return all_data



# Call the API to download the Excel file data
def download_excel_file(url: str, filename:str):
  try:
    print(f"[DOWNLOAD] Downloading from {url}")

    # Construct the request
    req = urllib.request.Request(url, headers=create_headers())

    # Open the request and write the response to a file
    with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
        data = response.read()  # Read the response data
        out_file.write(data)    # Write the data to a file
    return True
  except Exception as e:
    print(f"[FAILED] Failed to download excel file: {e}")
    return False



# Main function to process the combined data (as a dataframe)
def process_dataframe(df: pd.DataFrame, process: int = 1):
  scrapped_symbol_list = df['symbol'].unique()
  data_length = len(df)
  symbol_data_length = len(scrapped_symbol_list)

  print(f"[PROGRESS] {data_length} data of {symbol_data_length} stocks are available to be scraped")

  start_idx = 0
  range_limit = 3
  result_data_list_quarter = list()
  result_data_list_annual = list()
  while (start_idx < symbol_data_length):
    range_idx = min(symbol_data_length - start_idx, range_limit)

    # Iterate each symbol based on the range_limit
    for symbol in scrapped_symbol_list[start_idx:start_idx+range_idx]:
      curr_symbol_df = df[df['symbol'] == symbol]
      
      # # Download excel file
      # for _, row in curr_symbol_df.iterrows():
      #   # File name to be saved
      #   filename = os.path.join(DATA_IDX_SHEETS_DIR, f"{row['symbol']}_{row['year']}_{row['period']}.xlsx")
      #   url = f"{BASE_URL}{row['file_url']}".replace(" ", "%20")
    
      #   # Make 3 attempts to download the file
      #   attempt = 1
      #   limit_attempts = 3
      #   download_return = False
      #   while (attempt <= limit_attempts and not download_return):
      #     download_return = download_excel_file(url, filename)
      #     attempt += 1
      #     if (not download_return):
      #       if (attempt > limit_attempts):
      #         print(f"[COMPLETE FAILED] Failed to download excel file from {url} after {limit_attempts} attempts")
      #       else:
      #         print(f"[FAILED] Failed to download excel file from {url} after {attempt} attempts. Retrying...")
    
      #   time.sleep(1)

      # Check the industry of the company the code of the balance sheet
      # Check the code of the Balance Sheet to determine the industry
      first_row = curr_symbol_df.iloc[0]
      filename = os.path.join(DATA_IDX_SHEETS_DIR, f"{first_row['symbol']}_{first_row['year']}_{first_row['period']}.xlsx")
      # Open work book, try to get the industry code
      wb = xl.load_workbook(filename)
      balance_sheet_code = wb.sheetnames[3]
      industry_key_idx = int(balance_sheet_code[0])

      # Check if the industry is detected
      if (industry_key_idx is not None):
        # Proceed if industry is detected
        # Process each excel data
        current_symbol_list_data = list()
        for _, row in curr_symbol_df.iterrows():
          data = process_excel(row['symbol'], row['period'], row['year'], industry_key_idx)
          if (data is not None):
            current_symbol_list_data.append(data)

            # For quarter data, needs further handling. 
            # On the other side, for annual data, we can directly insert into the store
            if (row['symbol'] == "tw4"):
              result_data_list_annual.append(data)

            print(f"[SUCCESS] Successfully get the data for {symbol} period {row['period']} year {row['year']}")

          # # Delete the excel file if the data has been processed
          # filename = os.path.join(DATA_IDX_SHEETS_DIR, f"{symbol}_{row['year']}_{row['period']}.xlsx")
          # os.remove(filename)

        # Further handling for quarter data
        # TO DO

      
        # Insert all the data in current_symbol_list_data to result_data_list
        for data in current_symbol_list_data:
          result_data_list_quarter.append(data)

      else:
        print(f"[FAILED] Failed to detect the industry of {symbol}")
        # Files that are failed to be processed will not be deleted (in order to make it easier to notice)

      
    break # for testing
    # Incremental
    start_idx += range_idx

  # # Save quarter data
  # dataframe_quarter = pd.DataFrame(result_data_list_quarter)
  # filename_store_quarter = os.path.join(DATA_RESULT_DIR, f"idx_result_data_quarter_P{process}.csv")
  # dataframe_quarter.to_csv(filename_store_quarter, index = False)   

  # # Save annual data
  # dataframe_annual = pd.DataFrame(result_data_list_annual)
  # filename_store_annual = os.path.join(DATA_RESULT_DIR, f"idx_result_data_annual_P{process}.csv")
  # dataframe_annual.to_csv(filename_store_annual, index = False)   
  # print(f"[COMPLETED] The file data has been stored in {filename_store_annual} and {filename_store_quarter}")


# Tries to open Excel File, return None if fails
def open_excel_file(filename: str, sheetname: str):
  try:
    df = pd.read_excel(filename, sheet_name=sheetname)
    return df
  except Exception as e:
    print(f'[WRONG FILE/ SHEET] Failed to open file {filename}: {e}')
    return None
  



# Checking the first sheet => Information Sheet of the excel
# Return the rounding level if success, otherwise None
def check_information_sheet(filename: str):
  try:
    df = open_excel_file(filename, "1000000")
    if (df is not None):
      for _, row in df.iterrows():
        # Cast row['Unnamed: 2'] to string
        if ("Level of rounding" in str(row['Unnamed: 2'])):
          rounding = str(row['Unnamed: 1']).upper()
          for k, v in ROUNDING_LEVEL_MAPPING.items():
            if (k in rounding):
              rounding_val = v
      return rounding_val
    else:
      print(f'[FAILED] Cannot open file {filename}. Make sure to input the right file name and sheet name')
      return None
    
  except Exception as e:
    print(f"[FAILED] Failed to open Information Sheet: {e}")
    return None




# Used to get the data value where the column name is contained within the list
def sum_value_equal(df : pd.DataFrame, column_list: list, rounding_val : float):
  result_val = None
  for _, row in df.iterrows():
    if (row['Unnamed: 3'] in column_list):
      data_val = None if (row['Unnamed: 1'] is None or np.isnan(row['Unnamed: 1'])) else float(row['Unnamed: 1'] * rounding_val)
      result_val = none_handling_operation(result_val, data_val, "+", True)

  return result_val



# Used to get the data value where the starting from column_start iterated to column_end, can be optionally specified to select only contains a certain key word
# contain_keyword = None -> all column will be selected. contain_keyword != None -> only select column that contains the 'keyword'
def sum_value_range(df : pd.DataFrame, column_start: str, column_end: str, rounding_val : float, contain_keyword : str = None):
  result_val = None
  continue_process = False
  for _, row in df.iterrows():
    # Only start process when find column_start and end process when find column_end
    if (row['Unnamed: 3'] == column_start):
      continue_process = True
      starting_point = True
    if (continue_process):
      #  Check if the column contains the keyword if the contain_keyword is not None
      #  Default check_found = True
      #  Case : contain_keyword is None, then every column will be selected -> check_found is True
      #  Case : contain_keyword is not None, if the column contains keyword -> check_found is still True, otherwise, check_found becomes False
      check_found = True
      if (contain_keyword is not None and not contain_keyword in row['Unnamed: 3']):
        check_found = False
      
      # Only select if check_found is True
      if (check_found):
        data_val = None if (row['Unnamed: 1'] is None or np.isnan(row['Unnamed: 1'])) else float(row['Unnamed: 1'] * rounding_val)
        result_val = none_handling_operation(result_val, data_val, "+", True)
      starting_point = False
      
    if (row['Unnamed: 3'] == column_end and not starting_point):
      continue_process = False
      break

  if (continue_process):
    print(f'[ERROR] Column end {column_end} is not found!')

  return result_val





# Process balance sheet 
def process_balance_sheet(filename: str, sheet_code_list: list, column_mapping: dict, rounding_val: float, industry_key_idx: int):
  # Balance Sheet
  try:
    # Create dict using metrics template
    balance_sheet_dict = dict()
    for metric in BALANCE_SHEET_METRICS:
      balance_sheet_dict[metric] = None

    for sheet_name in sheet_code_list:
      df = open_excel_file(filename, sheet_name)
      if (df is not None):
        break

    if (df is not None):
      # Iterate for data that can be directly selected
      for _, row in df.iterrows():
        if (row['Unnamed: 3'] in column_mapping):
          data_val = None if (row['Unnamed: 1'] is None or np.isnan(row['Unnamed: 1'])) else float(row['Unnamed: 1'] * rounding_val) 
          if (type(column_mapping[row['Unnamed: 3']])) == list:
            for metric in column_mapping[row['Unnamed: 3']]:
              balance_sheet_dict[metric] = data_val
          else:
            balance_sheet_dict[column_mapping[row['Unnamed: 3']]] == data_val
          
          
      # Dividing companies based on industries
      # Doing Calculations and Adjustments
      if (industry_key_idx == 1): # General
        balance_sheet_dict['cash_and_short_term_investments'] = sum_value_equal(df, ['Cash and cash equivalents', 'Short-term investments'], rounding_val)
        balance_sheet_dict['total_debt'] = none_handling_operation(
          none_handling_operation(sum_value_equal(df, ['Short term bank loans', 'Trust receipts payables'], rounding_val),  sum_value_range(df, "Current maturities of long-term liabilities", "Current maturities of other borrowings", rounding_val), "+", True), 
          sum_value_range(df, "Long-term liabilities net of current maturities", "Long-term other borrowings", rounding_val), "+", True)

      elif (industry_key_idx == 2): # Property
        balance_sheet_dict['cash_and_short_term_investments'] = sum_value_equal(df, ['Cash and cash equivalents', 'Short-term investments'], rounding_val)
        balance_sheet_dict['total_debt'] = none_handling_operation(
          none_handling_operation(sum_value_equal(df, ['Short term bank loans', 'Trust receipts payables'], rounding_val),  sum_value_range(df, "Current maturities of long-term liabilities", "Current maturities of other borrowings", rounding_val), "+", True), 
          sum_value_range(df, "Long-term liabilities net of current maturities", "Long-term other borrowings", rounding_val), "+", True)

      elif (industry_key_idx == 3): # Infrastructure
        balance_sheet_dict['cash_and_short_term_investments'] = sum_value_equal(df, ['Cash and cash equivalents', 'Short-term investments'], rounding_val)
        balance_sheet_dict['total_debt'] = none_handling_operation(
          none_handling_operation(sum_value_equal(df, ['Short term bank loans', 'Trust receipts payables'], rounding_val),  sum_value_range(df, "Current maturities of long-term liabilities", "Current maturities of other borrowings", rounding_val), "+", True), 
          sum_value_range(df, "Long-term liabilities net of current maturities", "Long-term other borrowings", rounding_val), "+", True)

      elif (industry_key_idx == 4): # Finance and Sharia
        balance_sheet_dict['gross_loan'] = sum_value_equal(df, ['Loans third parties', 'Loans related parties'], rounding_val)
        balance_sheet_dict['net_loan'] = balance_sheet_dict['gross_loan'] + balance_sheet_dict['allowance_for_loans']
        balance_sheet_dict['non_loan_assets'] = balance_sheet_dict['total_assets'] - balance_sheet_dict['net_loan']
        balance_sheet_dict['total_cash_and_due_from_banks'] = sum_value_equal(df, ['Cash', 'Current accounts with bank Indonesia'], rounding_val) + sum_value_range(df, "Current accounts with other banks", "Allowance for impairment losses for current accounts with other bank", rounding_val)
        balance_sheet_dict['current_account'] = sum_value_range(df, 'Current accounts', "Current accounts related parties", rounding_val)
        balance_sheet_dict['savings_account'] = sum_value_range(df, 'Savings', "Savings related parties", rounding_val)
        balance_sheet_dict['time_deposits'] = sum_value_range(df, 'Time deposits', "Time deposits related parties", rounding_val)
        balance_sheet_dict['total_deposits'] = balance_sheet_dict['current_account'] + balance_sheet_dict['savings_account'] + balance_sheet_dict['time_deposits']

      elif (industry_key_idx == 5): # Securities
        balance_sheet_dict['cash_only'] = sum_value_equal(df, ['Cash and cash equivalents', 'Restricted funds'], rounding_val)

      elif (industry_key_idx == 6): # Insurance
        'TODO: waiting unfinalized metrics'

      else : # (industry_key_idx == 8): # Financing
        'TODO: waiting unfinalized metrics'

      return balance_sheet_dict
    
    else:
      print(f'[FAILED] Cannot open file {filename}. Make sure to input the right file name and sheet name')
      return None
  except Exception as e:
    print(f"[FAILED] Failed to process Balance Sheet data of {filename}: {e}")
    return None





# Process income statement
def process_income_statement(filename: str, sheet_code_list: list, column_mapping: dict, rounding_val: float, industry_key_idx: int):
  # Income Statement
  try:
    # Create dict using metrics template
    income_statement_dict = dict()
    for metric in INCOME_STATEMENT_METRICS:
      income_statement_dict[metric] = None

    for sheet_name in sheet_code_list:
      df = open_excel_file(filename, sheet_name)
      if (df is not None):
        break

    if (df is not None):
      for _, row in df.iterrows():
        if (row['Unnamed: 3'] in column_mapping):
          data_val = None if (row['Unnamed: 1'] is None or np.isnan(row['Unnamed: 1'])) else float(row['Unnamed: 1'] * rounding_val) 
          if (type(column_mapping[row['Unnamed: 3']])) == list:
            for metric in column_mapping[row['Unnamed: 3']]:
              income_statement_dict[metric] = data_val
          else:
            income_statement_dict[column_mapping[row['Unnamed: 3']]] == data_val

      # Dividing companies based on industries
      # Doing Calculations and Adjustments
      if (industry_key_idx == 1): # General
        income_statement_dict['operating_expenses'] = sum_value_equal(df, ['Selling expenses', 'General and administrative expenses'], rounding_val)
        income_statement_dict['operating_income'] = none_handling_operation(income_statement_dict['gross_income'], income_statement_dict['operating_expenses'], "+", True)
        income_statement_dict['non_operating_income'] = none_handling_operation(income_statement_dict['pretax_income'],  income_statement_dict['operating_income'], "-", False)
        income_statement_dict['ebit'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['interest_expense_non_operating'], "+", False)
        income_statement_dict['ebitda'] = None #TODO
        income_statement_dict['diluted_shares_outstanding'] = (sum_value_equal(df, ['Profit (loss) attributable to parent entity'], rounding_val) /  sum_value_equal(df, ['Basic earnings (loss) per share from continuing operations'], rounding_val))

      elif (industry_key_idx == 2): # Property
        income_statement_dict['operating_expenses'] = sum_value_equal(df, ['Selling expenses', 'General and administrative expenses'], rounding_val)
        income_statement_dict['operating_income'] = none_handling_operation(income_statement_dict['gross_income'], income_statement_dict['operating_expenses'], "+", True)
        income_statement_dict['non_operating_income'] = none_handling_operation(income_statement_dict['pretax_income'],  income_statement_dict['operating_income'], "-", False)
        income_statement_dict['ebit'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['interest_expense_non_operating'], "+", False)
        income_statement_dict['ebitda'] = None #TODO
        income_statement_dict['diluted_shares_outstanding'] = (sum_value_equal(df, ['Profit (loss) attributable to parent entity'], rounding_val) /  sum_value_equal(df, ['Basic earnings (loss) per share from continuing operations'], rounding_val))

      elif (industry_key_idx == 3): # Infrastructure
        income_statement_dict['operating_expenses'] = sum_value_equal(df, ['Selling expenses', 'General and administrative expenses'], rounding_val)
        income_statement_dict['operating_income'] = none_handling_operation(income_statement_dict['gross_income'], income_statement_dict['operating_expenses'], "+", True)
        income_statement_dict['non_operating_income'] = none_handling_operation(income_statement_dict['pretax_income'],  income_statement_dict['operating_income'], "-", False)
        income_statement_dict['ebit'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['interest_expense_non_operating'], "+", False)
        income_statement_dict['ebitda'] = None #TODO
        income_statement_dict['diluted_shares_outstanding'] = (sum_value_equal(df, ['Profit (loss) attributable to parent entity'], rounding_val) /  sum_value_equal(df, ['Basic earnings (loss) per share from continuing operations'], rounding_val))

      elif (industry_key_idx == 4): # Finance and Sharia
        income_statement_dict['net_interest_income'] = none_handling_operation(income_statement_dict['interest_income'], income_statement_dict['interest_expenses'], '+', False)
        income_statement_dict['net_premium_income'] = none_handling_operation(income_statement_dict['premium_income'], income_statement_dict['premium_expenses'], '+', False)
        income_statement_dict['non_interest_income'] = sum_value_range(df, 'Other operating income', "Other operating income", rounding_val)
        income_statement_dict['total_revenue'] = none_handling_operation(none_handling_operation(income_statement_dict['net_interest_income'], income_statement_dict['net_premium_income'], '+', False), income_statement_dict['non_interest_income'], '+', False)
        income_statement_dict['operating_expenses'] = sum_value_range(df, 'Other operating expenses', "Other operating expenses", rounding_val)
        income_statement_dict['provision_for_impairment'] = sum_value_range(df, "Recovery of impairment loss", "Recovery of estimated loss of commitments and contingency", rounding_val) + sum_value_range(df, "Allowances for impairment losses", "Reversal (expense) of estimated losses on commitments and contingencies", rounding_val)
        income_statement_dict['non_operating_income'] = sum_value_range(df, "Non-operating income and expense", "Share of profit (loss) of joint ventures accounted for using equity method", rounding_val)
        income_statement_dict['net_income'] = none_handling_operation(sum_value_equal(df, ['Total profit (loss)']), income_statement_dict['minorities'], '+', True)
        income_statement_dict['diluted_shares_outstanding'] = (sum_value_equal(df, ['Profit (loss) attributable to parent entity'], rounding_val) /  sum_value_equal(df, ['Basic earnings (loss) per share from continuing operations'], rounding_val))

      elif (industry_key_idx == 5): # Securities
        income_statement_dict['total_revenue'] = sum_value_range(df, "Statement of profit or loss and other comprehensive income", "Gains (losses) on changes in fair value of marketable securities", rounding_val)
        income_statement_dict['operating_expenses'] = sum_value_equal(df, ['Selling expenses', 'General and administrative expenses'], rounding_val)
        income_statement_dict['operating_income'] = None #TODO
        # income_statement_dict['non_operating_income'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['operating_income'], '-', False) 
        income_statement_dict['ebit'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['interest_expense_non_operating'], "+", False)
        income_statement_dict['ebitda'] = None #TODO
        income_statement_dict['diluted_shares_outstanding'] = (sum_value_equal(df, ['Profit (loss) attributable to parent entity'], rounding_val) /  sum_value_equal(df, ['Basic earnings (loss) per share from continuing operations'], rounding_val))

      elif (industry_key_idx == 6): # Insurance
        'TODO: waiting unfinalized metrics'
        income_statement_dict['diluted_shares_outstanding'] = (sum_value_equal(df, ['Profit (loss) attributable to parent entity'], rounding_val) /  sum_value_equal(df, ['Basic earnings (loss) per share from continuing operations'], rounding_val))

      else : # (industry_key_idx == 8): # Financing
        'TODO: waiting unfinalized metrics'
        income_statement_dict['operating_expenses'] = sum_value_range(df, "Selling expenses", "Other losses", rounding_val)
        income_statement_dict['gross_income'] = none_handling_operation(income_statement_dict['non_operating_income'], income_statement_dict['operating_expenses'], "+", True)
        income_statement_dict['operating_income'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['non_operating_income'], "-", True)
        income_statement_dict['total_revenue'] = none_handling_operation(income_statement_dict['gross_income'], income_statement_dict['cost_of_revenue'], "+", True)
        income_statement_dict['ebit'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['interest_expense_non_operating'], "+", False)
        income_statement_dict['ebitda'] = None #TODO
        income_statement_dict['diluted_shares_outstanding'] = (sum_value_equal(df, ['Profit (loss) attributable to parent entity'], rounding_val) /  sum_value_equal(df, ['Basic earnings (loss) per share from continuing operations'], rounding_val))

      return income_statement_dict
    
    else:
      print(f'[FAILED] Cannot open file {filename}. Make sure to input the right file name and sheet name')
      return None
  except Exception as e:
    print(f"[FAILED] Failed to process Income Statement data of {filename}: {e}")
    print(income_statement_dict)
    return None  



# Process cash flow
def process_cash_flow(filename: str, sheet_code_list: list, column_mapping: dict, rounding_val: float, industry_key_idx: int):
  # Cash flow
  try:
    # Create dict using metrics template
    cash_flow_dict = dict()
    for metric in CASH_FLOW_METRICS:
      cash_flow_dict[metric] = None

    for sheet_name in sheet_code_list:
      df = open_excel_file(filename, sheet_name)
      if (df is not None):
        break

    if (df is not None):
      for _, row in df.iterrows():
        if (row['Unnamed: 3'] in column_mapping):
          data_val = None if (row['Unnamed: 1'] is None or np.isnan(row['Unnamed: 1'])) else float(row['Unnamed: 1'] * rounding_val) 
          if (type(column_mapping[row['Unnamed: 3']])) == list:
            for metric in column_mapping[row['Unnamed: 3']]:
              cash_flow_dict[metric] = data_val
          else:
            cash_flow_dict[column_mapping[row['Unnamed: 3']]] == data_val
      
      # Dividing companies based on industries
      # Doing Calculations and Adjustments
      if (industry_key_idx in [1, 2, 3, 5, 6, 8]):
        cash_flow_dict['capital_expenditure'] = sum_value_range(df, "Cash flows from investing activities", "Other cash inflows (outflows) from investing activities", rounding_val, "Payments") 
        cash_flow_dict['free_cash_flow'] = none_handling_operation(cash_flow_dict['net_operating_cash_flow'], cash_flow_dict['capital_expenditure'], "+", False)
      else: # (industry_key == 4)
        cash_flow_dict['total_high_quality_liquid_asset'] = None #TODO
        cash_flow_dict['cash_outflow'] = None #TODO
        cash_flow_dict['cash_inflow'] = None #TODO
        cash_flow_dict['total_net_cash_outflow'] = None #TODO
        cash_flow_dict['realized_capital_goods_investment'] = None #TODO
        cash_flow_dict['total_net_cash_flow'] = None #TODO

      return cash_flow_dict
    
    else:
      print(f'[FAILED] Cannot open file {filename}. Make sure to input the right file name and sheet name')
      return None
    
  except Exception as e:
    print(f"[FAILED] Failed to process Cash Flow data of {filename}: {e}")
    return None




# Change period and year to date format
def date_format (period: str, year: str):
  # period value = ['tw1', 'tw2', 'tw3', 'tw4']
  period_map = {
    "tw1" : "-03-31",
    "tw2" : "-06-30",
    "tw3" : "-09-30",
    "tw4" : "-12-31"
  }
  return f"{str(year)}{period_map[period]}"





def process_excel(symbol: str, period: str, year : int, industry_key_idx: int):
  try:
    # File name to be saved
    filename = os.path.join(DATA_IDX_SHEETS_DIR, f"{symbol}_{year}_{period}.xlsx")

    # Check Information Sheet
    rounding_val = check_information_sheet(filename)
    mapping_dict = UNIVERSAL_MAPPING[industry_key_idx]
    date = date_format(period, year)
    result_dict = {
      "symbol" : symbol,
      "date" : date,
      "industry_code" : industry_key_idx
    }

    print(f"[PROCESS] Processing {symbol} date {date} industry_key {industry_key_idx}...")

    # Process each data
    print(f"[BS] Processing Balance Sheet ...")
    balance_sheet_data = process_balance_sheet(filename, mapping_dict['bs_sheet_code'], mapping_dict['bs_column_mapping'], rounding_val, industry_key_idx)
    print(f"[IS] Processing Income Statement ...")
    income_statement_data = process_income_statement(filename, mapping_dict['is_sheet_code'], mapping_dict['is_column_mapping'], rounding_val, industry_key_idx)
    print(f"[CF] Processing Cash Flow ...")
    cash_flow_data = process_cash_flow(filename, mapping_dict['cf_sheet_code'], mapping_dict['cf_column_mapping'], rounding_val, industry_key_idx)

    # Update and combine dictionary
    result_dict.update(balance_sheet_data)
    result_dict.update(income_statement_data)
    result_dict.update(cash_flow_data) 

    # for printing only
    for k, v in result_dict.items():
      print(f"\t[{k} => {v}]")
    
    print(f'[SUCCESS] Successfully processed {filename}!')
    
    return result_dict
  except Exception as e:
    print(f'[FAILED] Cannot get the data of {symbol} period {period} year {year}: {e}')
    return None

if __name__ == "__main__":
  all_data = combine_technical_data()
  process_dataframe(all_data)