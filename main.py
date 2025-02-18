import pandas as pd
import os
import time
from multiprocessing import Process, Manager
from idx_process import process_dataframe
from idx_scrape_url import fetch_url, get_data
import sys
from idx_utils import (
    PERIOD_LIST,
    DATA_DIR,
    supabase_client,
    date_format
)
from datetime import datetime, timedelta
import logging
from imp import reload

"""
HOW TO START:
## 1
=> For automatic start:
Command:
python main.py {BATCH}

Description:
Automatically scrape and extract based on current time
Interval (3*30 + 7) for Annual
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

"""


def initiate_logging(LOG_FILENAME):
    reload(logging)

    formatLOG = '%(asctime)s - %(levelname)s: %(message)s'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO, format=formatLOG)



if __name__ == "__main__":

    if len(sys.argv) > 2:
        assert len(sys.argv) >= 4, "[ERROR] Invalid argument input!"

        # Read running argument
        batch_arg = sys.argv[1]
        year_arg = int(sys.argv[2])
        period_arg = sys.argv[3]

        assert period_arg in PERIOD_LIST, "[ERROR] Invalid period argument!"

    else:

        current_time = datetime.now()
        current_month = int(current_time.month)
        batch_arg = sys.argv[1]
        if current_month <= 3:  # Get Annual and Q4 last year 
            # Should only be run when current_month == 3
            # But can also run when current_month == 1 and current_month == 2
            period_arg = "audit"
            year_arg = int(current_time.year) - 1
        elif current_month in [5, 8, 11]:  # Get Q1, Q2, Q3 this year
            # Should only run when current_month == [5,8,11] 
            # But can also run for the rest
            # Current_month 4,5,6 => Getting Q1
            # Current_month 7,8,9 => Getting Q2
            # Current_month 10,11,12 => Getting Q3
            last_quarter = current_time - timedelta(30)
            month = int(last_quarter.month)
            month_arg_idx = max((month - 1) // 3, 0)
            period_arg = PERIOD_LIST[month_arg_idx]
            year_arg = int(current_time.year)

    LOG_FILENAME = 'process.log'
    initiate_logging(LOG_FILENAME)
    logging.info(f"[INITIATE] The program has started to extract quarter {period_arg} and year {year_arg} data")

    ## SCRAPE URL PROCESS
    ######################

    # Get the table
    # current_year_end = datetime(year_arg + 1, 1, 1).isoformat()
    # db_data = (
    #     supabase_client.table("idx_active_company_profile")
    #     .select("symbol")
    #     .lt("listing_date", current_year_end)
    #     .execute()
    # )
    db_data = (
        supabase_client.table("idx_active_company_profile")
        .select("symbol")
        .execute()
    )
    df_db_data = pd.DataFrame(db_data.data)
    symbol_list: list = df_db_data["symbol"].unique().tolist()
    print(f"[DATABASE] Get {len(symbol_list)} data from database")

    # Handle for batches
    start_idx = 0
    length_list = len(symbol_list)
    if batch_arg != "all":
        # ignore if it is all
        length_list = length_list // 4
        start_idx += (int(batch_arg) - 1) * length_list
        symbol_list = symbol_list[start_idx : start_idx + length_list]


    print(f"[BATCH PROCESS] Finding batch process (arg: {batch_arg}) for company index {start_idx} to {start_idx+length_list}")
    logging.info(f"[BATCH PROCESS] Finding batch process (arg: {batch_arg}) for company index {start_idx} to {start_idx+length_list}")

    # # SELECTIVE FETCHING
    # # Implement selection only for data that does not exist in DB
    # period_date = date_format(period_arg if period_arg != "audit" else "tw4", year_arg)
    # already_in_db_data = (supabase_client.table("idx_financial_sheets_quarterly").select("symbol").eq("date", period_date).execute()).data
    # already_in_db_list = [data['symbol'] for data in already_in_db_data]
    # for symbol in already_in_db_list:
    #     if (symbol in symbol_list):
    #         symbol_list.remove(symbol)

    print(f"[SELECTION PROCESS] After selection process, amount of companies that will be scraped is {len(symbol_list)}")
    logging.info(f"[SELECTION PROCESS] After selection process, amount of companies that will be scraped is {len(symbol_list)}")            

    # Divide to 4 parts for multiprocess
    length_list = len(symbol_list)
    i1 = length_list // 4
    i2 = 2 * i1
    i3 = 3 * i1


    # Start time
    start = time.time()

    # Initiate manager for shared_list
    manager = Manager()

    # Using multiprocessing sharedlist
    shared_list = manager.list()

    # Scraper Program
    # [LOOK] idx_scrape_url.py
    p1 = Process(
        target=get_data,
        args=(symbol_list[:i1], 1, year_arg, period_arg, shared_list),
    )
    p2 = Process(
        target=get_data,
        args=(symbol_list[i1:i2], 2, year_arg, period_arg, shared_list),
    )
    p3 = Process(
        target=get_data,
        args=(symbol_list[i2:i3], 3, year_arg, period_arg, shared_list),
    )
    p4 = Process(
        target=get_data,
        args=(symbol_list[i3:], 4, year_arg, period_arg, shared_list),
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

    # Combine the result from all the multiprocesses
    scraping_results = []
    failed_results = []
    for data in shared_list:
        scraping_results.extend(data[0])
        failed_results.extend(data[1])

    # Save url and failed csv
    if len(scraping_results) > 0:
        dataframe = pd.DataFrame(scraping_results)
        filename_store = os.path.join(DATA_DIR, f"url_list.csv")
        dataframe.to_csv(filename_store, index=False)
        print(f"[COMPLETED] The file data has been stored in {filename_store}")
    if len(failed_results) > 0:
        failed_datafrane = pd.DataFrame(failed_results)
        failed_filename = os.path.join(DATA_DIR, f"failed_list.csv")
        failed_datafrane.to_csv(failed_filename, index=False)
        print(f"[COMPLETED] The failed data has been stored in {failed_filename}")


    # End time
    end_scraping = time.time()
    scraping_duration = int(end_scraping - start)
    scraping_duration_str = time.strftime('%H:%M:%S', time.gmtime(scraping_duration))
    print(f"The scraping execution time: {scraping_duration_str}")
    logging.info(f"[PROGRESS] Scraping execution has finished taking duration of {scraping_duration_str}.")
    logging.info(f"[FAILED REPORT] {len(failed_results)} data are failed to be scrapped.")



    # # DOWNLOAD AND EXCEL PROCESS
    # ##############################

    # Use multiprocess to increase efficiency
    all_data = pd.read_csv(os.path.join("data", "url_list.csv"))
    length_list = len(all_data)
    i1 = int(length_list / 4)
    i2 = 2 * i1
    i3 = 3 * i1

    # Using multiprocessing sharedlist
    shared_list = manager.list()

    # Process Program
    # [LOOK] idx_process.py
    p1 = Process(
        target=process_dataframe,
        args=(all_data[:i1], period_arg, year_arg, shared_list, 1),
    )
    p2 = Process(
        target=process_dataframe,
        args=(all_data[i1:i2], period_arg, year_arg, shared_list, 2),
    )
    p3 = Process(
        target=process_dataframe,
        args=(all_data[i2:i3], period_arg, year_arg, shared_list, 3),
    )
    p4 = Process(
        target=process_dataframe,
        args=(all_data[i3:], period_arg, year_arg, shared_list, 4),
    )

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

    # Combine the result from all the multiprocesses
    results = []
    quarter_results = []
    annual_results = []
    for data in shared_list:
        quarter_results.extend(data[0])
        annual_results.extend(data[1])

    # Save quarter data
    if len(quarter_results) != 0:
        dataframe_quarter = pd.DataFrame(quarter_results)
        filename_store_quarter = os.path.join(
            DATA_DIR, f"data_quarter.csv"
        )
        dataframe_quarter.to_csv(filename_store_quarter, index=False)
        print(f"[COMPLETED] Quarter data has been stored in {filename_store_quarter}")
    # Save annual data
    if len(annual_results) != 0:
        dataframe_annual = pd.DataFrame(annual_results)
        filename_store_annual = os.path.join(
            DATA_DIR, f"data_annual.csv"
        )
        dataframe_annual.to_csv(filename_store_annual, index=False)
        print(f"[COMPLETED] Annual data has been stored in {filename_store_annual}")

    # End time
    end_processing = time.time()
    processing_duration = int(end_processing - end_scraping)
    processing_duration_str = time.strftime('%H:%M:%S', time.gmtime(processing_duration))
    print(f"The processing execution time: {processing_duration_str}")
    logging.info(f"[PROGRESS] Processing execution has finished taking duration of {processing_duration_str}.")

