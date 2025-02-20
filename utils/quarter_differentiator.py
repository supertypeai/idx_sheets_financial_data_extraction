import os
import pandas as pd
import numpy as np
import json

DATA_DIR = os.path.join(os.getcwd(), "data")

# Make general function to be used in adding None
# none_to_zero == True -> assuming None is equal to 0 -> None (operation) num = num
# none_to_zero == False -> None (operation) num = None
def none_handling_operation(
    num1: float, num2: float, operation: str, none_to_zero: bool = False
):
    # Generalize None type
    none_num1 = False
    none_num2 = False
    if num1 is None or np.isnan(num1):
        none_num1 = True
    if num2 is None or np.isnan(num2):
        none_num2 = True

    # Check and Calculate
    if none_num1 and none_num2:
        return None
    else:
        if none_num1:
            return num2 if none_to_zero else None
        elif none_num2:
            return num1 if none_to_zero else None
        else:
            # Correct condition
            if operation == "+":
                return num1 + num2
            elif operation == "-":
                return num1 - num2
            elif operation == "/":
                return num1 / num2
            elif operation == "*":
                return num1 * num2

def quarter_differentiator(prev_q_path: str, curr_q_path: str, result_path: str):
      prev_q_data = pd.read_csv(prev_q_path)
      curr_q_data = pd.read_csv(curr_q_path)
      for curr_idx, curr_q_row in curr_q_data.iterrows():
        for _, prev_q_row in prev_q_data.iterrows():
          if (curr_q_row['symbol'] == prev_q_row['symbol']):
            print(f"[PROCESS] Processing {curr_q_row['symbol']}")

            if (prev_q_row['income_stmt_metrics_cumulative'] is not None and not pd.isna(prev_q_row['income_stmt_metrics_cumulative'])):
              prev_income_stmt_cumulative = json.loads(prev_q_row['income_stmt_metrics_cumulative'])

              if (curr_q_row['income_stmt_metrics_cumulative'] is not None and not pd.isna(curr_q_row['income_stmt_metrics_cumulative'])):
                curr_quarter_data = json.loads(curr_q_row['income_stmt_metrics_cumulative'])

                current_quarter_data = {}
                # Subtract if the data exist
                for key, value in curr_quarter_data.items():
                    if (key != "diluted_shares_outstanding"): # Exception 
                      if (key in prev_income_stmt_cumulative):
                        prev_val = prev_income_stmt_cumulative[key]
                        current_quarter_data[key] = none_handling_operation(value, prev_val, "-", False)
                    else:
                      # diluted_shares_outstanding is not subtracted
                      current_quarter_data[key] = value


              else:
                print(f"[NONE VALUE CURRENT] None value for current data Ticker {curr_q_row['symbol']}")
            else:
                print(f"[NONE VALUE PREVIOUS] None value for previous data Ticker {prev_q_row['symbol']}")
        
        curr_q_data.at[curr_idx, 'income_stmt_metrics'] = json.dumps(current_quarter_data)
      
      curr_q_data.to_csv(result_path, index=False)
      
      





prev_q_path = os.path.join(DATA_DIR, "data_quarter_2022_tw1.csv")
curr_q_path = os.path.join(DATA_DIR, "data_quarter_2022_tw2.csv")
result_path = os.path.join(DATA_DIR, "data_quarter_2022_tw2_calculated.csv")
quarter_differentiator(prev_q_path, curr_q_path, result_path)