import pandas as pd
import os
import time
from multiprocessing import Process
from idx_process import process_dataframe
from idx_scrape_url import fetch_url, get_data
import sys
from idx_utils import (
    PERIOD_LIST,
    DATA_IDX_URL_DIR,
    DATA_PROCESSED_DIR,
    DATA_RESULT_DIR,
    supabase_client,
)
from datetime import datetime, timedelta

"""
HOW TO START:
## 1
=> For automatic start:
Command:
python main.py {BATCH}

Description:
Automatically scrape and extract based on current time
Interveral (3*30 + 7) for Annual
Interval (30 + 7) for Quarter

if it runs in:
  Month 3: 
  -> get annual and Q4 of last year
  Month 4:
  -> get Q1 of current year
  Month 7:
  -> get Q2 of current year
  Month 10: 
  -> get Q3 of current year

BATCH = [1, 2, 3, 4, all]
  1 => First quarter
  2 => Second quarter
  3 => Third quarter
  4 => Last quarter
  all => scrape for all in the database

## 2
=> For manual start:
Command:
python main.py {BATCH} {YEAR} {PERIOD}
e.g.: python main.py 1 2024 tw1   #Scrape and extract Q1 of 2024 for batch 1

Description:
program requires two parameters: {year} and {PERIOD}
YEAR => year to be scrapped
PERIOD => see PERIOD_LIST in idx_utils.py
BATCH = [1, 2, 3, 4, all]
  1 => First quarter
  2 => Second quarter
  3 => Third quarter
  4 => Last quarter
  all => scrape for all in the database
PREVIOUS_PERIOD_DATA => data of previous period for quarterly data

"""


# Combine scrapped data from the csv files
def combine_url_data(year: str, period: str):
    failed_file_path = [
        os.path.join(DATA_IDX_URL_DIR, f"failed_list_P{i}.csv") for i in range(1, 5)
    ]
    data_file_path = [
        os.path.join(DATA_IDX_URL_DIR, f"scrapped_list_P{i}.csv") for i in range(1, 5)
    ]

    # Combine data
    all_data = pd.DataFrame()
    failed_data = pd.DataFrame()

    for i in range(len(data_file_path)):
        try:
            file_path = data_file_path[i]
            df = pd.read_csv(file_path)
            if i == 0:
                all_data = df
            else:
                all_data = pd.concat([all_data, df])
        except Exception as e:
            print(f"[FAILED] Failed to process DataFrame on {file_path}")

    # Combine failed data
    for i in range(len(failed_file_path)):
        try:
            file_path = failed_file_path[i]
            df = pd.read_csv(file_path)
            if i == 0:
                failed_data = df
            else:
                failed_data = pd.concat([failed_data, df])
            os.remove(file_path)
        except Exception as e:
            print(f"[FAILED] There is no failed data: {file_path}")
    failed_data.to_csv(
        os.path.join(DATA_RESULT_DIR, f"data_failed_{year}_{period}.csv"), index=False
    )

    return all_data


def combine_processed_data(year: str, period: str):

    data_quarter_path = [
        os.path.join(DATA_PROCESSED_DIR, f"data_quarter_P{i}.csv") for i in range(1, 5)
    ]
    data_annual_path = [
        os.path.join(DATA_PROCESSED_DIR, f"data_annual_P{i}.csv") for i in range(1, 5)
    ]

    quater_data = None
    annual_data = None

    for i in range(len(data_quarter_path)):
        try:
            file_path = data_quarter_path[i]
            df = pd.read_csv(file_path)
            if i == 0:
                quarter_data = df
            else:
                quarter_data = pd.concat([quarter_data, df])
        except Exception as e:
            print(f"[FAILED] Failed to process DataFrame on {file_path}: {e}")

    # Save
    if quarter_data is not None:
        quarter_data = quarter_data.drop(["industry_code"], axis=1)
        quarter_data.to_csv(
            os.path.join(DATA_RESULT_DIR, f"data_quarter_result_{year}_{period}.csv"),
            index=False,
        )

    for i in range(len(data_annual_path)):
        try:
            file_path = data_annual_path[i]
            df = pd.read_csv(file_path)
            if i == 0:
                annual_data = df
            else:
                annual_data = pd.concat([annual_data, df])
        except Exception as e:
            print(f"[FAILED] Failed to process DataFrame on {file_path}: {e}")

    # Save
    if annual_data is not None:
        annual_data = annual_data.drop(["industry_code"], axis=1)
        annual_data.to_csv(
            os.path.join(DATA_RESULT_DIR, f"data_annual_result_{year}_{period}.csv"),
            index=False,
        )

    return quater_data, annual_data


if __name__ == "__main__":

    if len(sys.argv) > 2:
        assert len(sys.argv) >= 4, "[ERROR] Invalid argument input!"

        # Read running argument
        batch_arg = sys.argv[1]
        year_arg = int(sys.argv[2])
        period_arg = sys.argv[3]

        assert period_arg in PERIOD_LIST, "[ERROR] Invalid period argument!"

        prev_period_data = None
        try:
            # Load previous period data for quarterly data
            prev_period_data = pd.read_csv(sys.argv[4])
            prev_period_data.set_index("symbol", inplace=True)
        except IndexError:
            pass

    else:

        current_time = datetime.now()
        current_month = int(current_time.month)
        batch_arg = sys.argv[1]
        if current_month == 3:  # Get Annual and Q4 last year
            period_arg = "audit"
            year_arg = int(current_time.year) - 1
        elif current_month in [5, 8, 11]:  # 5, 8, 11 # Get Q1, Q2, Q3 this year
            last_quarter = current_time - timedelta(30)
            month = int(last_quarter.month)
            month_arg_idx = max((month - 1) // 3, 0)
            period_arg = PERIOD_LIST[month_arg_idx]
            year_arg = int(current_time.year)

    ## SCRAPE URL PROCESS
    ######################

    # Get the table
    current_year_end = datetime(year_arg + 1, 1, 1).isoformat()
    db_data = (
        supabase_client.table("idx_active_company_profile")
        .select("symbol")
        .lt("listing_date", current_year_end)
        .execute()
    )
    df_db_data = pd.DataFrame(db_data.data)
    symbol_list: list = df_db_data["symbol"].unique().tolist()
    print(f"[DATABASE] Get {len(symbol_list)} data from database")

    start_idx = 0
    length_list = len(symbol_list)
    if batch_arg != "all":
        # ignore if it is all
        length_list = length_list // 4
        start_idx += (int(batch_arg) - 1) * length_list
        print(
            f"[BATCH PROCESS] Finding batch process for company index {start_idx} to {start_idx+length_list}"
        )
    i1 = length_list // 4
    i2 = 2 * i1
    i3 = 3 * i1

    # Start time
    start = time.time()

    # Scraper Program
    # [LOOK] idx_scrape_url.py
    p1 = Process(
        target=get_data,
        args=(symbol_list[start_idx : start_idx + i1], 1, year_arg, period_arg),
    )
    p2 = Process(
        target=get_data,
        args=(symbol_list[start_idx + i1 : start_idx + i2], 2, year_arg, period_arg),
    )
    p3 = Process(
        target=get_data,
        args=(symbol_list[start_idx + i2 : start_idx + i3], 3, year_arg, period_arg),
    )
    p4 = Process(
        target=get_data,
        args=(
            symbol_list[start_idx + i3 : start_idx + length_list],
            4,
            year_arg,
            period_arg,
        ),
    )

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
    scraping_duration = int(end_scraping - start)
    print(
        f"The scraping execution time: {time.strftime('%H:%M:%S', time.gmtime(scraping_duration))}"
    )

    # DOWNLOAD AND EXCEL PROCESS
    ##############################

    # Combine scrapped data
    all_data = combine_url_data(year_arg, period_arg)

    # Use multiprocess to increase efficiency
    length_list = len(all_data)
    i1 = int(length_list / 4)
    i2 = 2 * i1
    i3 = 3 * i1

    # Process Program
    # [LOOK] idx_process.py
    p1 = Process(
        target=process_dataframe,
        args=(all_data[:i1], period_arg, year_arg, prev_period_data, 1),
    )
    p2 = Process(
        target=process_dataframe,
        args=(all_data[i1:i2], period_arg, year_arg, prev_period_data, 2),
    )
    p3 = Process(
        target=process_dataframe,
        args=(all_data[i2:i3], period_arg, year_arg, prev_period_data, 3),
    )
    p4 = Process(
        target=process_dataframe,
        args=(all_data[i3:], period_arg, year_arg, prev_period_data, 4),
    )

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
    processing_duration = int(end_processing - end_scraping)
    print(
        f"The processing execution time: {time.strftime('%H:%M:%S', time.gmtime(processing_duration))}"
    )

    # Combine processed data
    data = combine_processed_data(year_arg, period_arg)
