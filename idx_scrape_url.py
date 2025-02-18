from idx_utils import (
    BASE_URL,
    PERIOD_LIST,
    create_headers,
)
import urllib.request
import json
import time
import pandas as pd
import os
from dotenv import load_dotenv
import requests
import warnings

load_dotenv()

warnings.simplefilter(action="ignore", category=UserWarning)

PROXY_URL = os.getenv("proxy")
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}


def fetch_url(
    period: str, symbol: str, year: str, process: int, use_proxy: bool = False
):
    # period = ["tw1", "tw2", "tw3", "audit"]
    try:
        url = f"{BASE_URL}/primary/ListedCompany/GetFinancialReport?year={year}&reportType=rdf&EmitenType=s&periode={period}&kodeEmiten={symbol.upper()}&SortColumn=KodeEmiten&SortOrder=asc"

        if not use_proxy:
            req = urllib.request.Request(url, headers=create_headers())
            resp = urllib.request.urlopen(req)
            status_code = resp.getcode()
        else:
            response = requests.get(url, proxies=PROXIES, verify=False)
            status_code = response.status_code

        if status_code == 200:
            if not use_proxy:
                data = resp.read()
                json_data = json.loads(data)
            else:
                json_data = response.json()

            if json_data["ResultCount"] > 0:
                print(
                    f"[SUCCESS P{process}] Successfully get the data from company {symbol}, year {year}, period {period}"
                )
                return json_data, None
            else:
                print(
                    f"[FAILED P{process}] Data is not available for company {symbol}, year {year}, period {period}"
                )
                return None, "Data is not available"
        else:
            print(
                f"[FAILED P{process}] Failed to fetch from {url}. Get status code : {status_code}"
            )
            return None, f"Status: {status_code}"
    except Exception as e:
        print(f"[FAILED P{process}] Failed to fetch from {url} : {e}")
        return None, f"Failed fetch: {e}"


def get_data(symbol_list: list, process: int, year: int, period: str, shared_list: list):
    RESULT_LIST = []
    FAILED_LIST = []
    count = 0

    for symbol in symbol_list:
        adjusted_symbol = symbol.replace(".JK", "")

        json_data, error_msg = fetch_url(period, adjusted_symbol, year, process, False)
        if json_data is not None:
            data_list = json_data["Results"][0]["Attachments"]

            for data in data_list:
                if (
                    data["File_Type"] == ".xlsx"
                    and "FinancialStatement" in data["File_Name"]
                ):

                    data_dict = {
                        "symbol": symbol,
                        "year": year,
                        "period": "tw4" if period == "audit" else period,
                        "file_name": data["File_Name"],
                        "file_url": data["File_Path"],
                    }
                    RESULT_LIST.append(data_dict)

        else:
            data_dict = {
                "symbol": symbol,
                "year": year,
                "period": "tw4" if period == "audit" else period,
                "error_message" : error_msg
            }
            FAILED_LIST.append(data_dict)

        time.sleep(1.5)

        count += 1
        if count % 20 == 0:
            print(f"[CHECKPOINT] P{process} has covered {count} data")

    shared_list.append((RESULT_LIST, FAILED_LIST))
