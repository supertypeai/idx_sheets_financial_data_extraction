import pandas as pd
import os


DATA_DIR = os.path.join(os.getcwd(), "data")

def combine_data(keywords:str, output_path:str, sort_columns: list, sort_ascending : list):

  data_files = os.listdir(DATA_DIR)
  data_files = [os.path.join(DATA_DIR, path) for path in data_files if keywords in path]

  # Print files
  for file in data_files:
    print(file)

  # Combine data
  all_data = pd.DataFrame()

  for i in range(len(data_files)):
    try:
      file_path = data_files[i]
      df = pd.read_csv(file_path)
      if (i == 0):
        all_data = df
      else:
        all_data = pd.concat([all_data, df])
    except Exception as e:
      print(f"[FAILED] Failed to process DataFrame on {file_path}")

  all_data = all_data.sort_values(sort_columns, ascending=sort_ascending)
  all_data.to_csv(output_path, index=False)

# keywords = "failed_list"
# output = os.path.join(DATA_DIR, f"{keywords}.csv")
# if __name__ == "__main__":
#   combine_data(keywords, output, ['symbol', 'year', 'period'], [True, True, True])

keywords = "data_quarter"
output = os.path.join(DATA_DIR, f"{keywords}.csv")
if __name__ == "__main__":
  combine_data(keywords, output, ['symbol', 'date'], [True, True])

# keywords = "data_annual"
# output = os.path.join(DATA_DIR, f"{keywords}.csv")
# if __name__ == "__main__":
#   combine_data(keywords, output, ['symbol', 'date'], [True, True])