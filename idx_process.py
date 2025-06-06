import os
import pandas as pd
import numpy as np
import time
import urllib
from idx_mapping_constant import ROUNDING_LEVEL_MAPPING, UNIVERSAL_MAPPING
from idx_utils import (
    DATA_IDX_SHEETS_DIR,
    BASE_URL,
    create_headers,
    supabase_client,
    date_format,
    none_handling_operation,
    get_rate
)
import warnings
import urllib.request
import openpyxl as xl
from dotenv import load_dotenv
import requests
import json
import math
from datetime import date


load_dotenv()

PROXY_URL = os.getenv("proxy")
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}

warnings.simplefilter(action="ignore", category=UserWarning)


def rounding_calc_and_check(num: int, rounding_val: float):
    if (rounding_val == 1): return float(num)
    num = str(num)
    power = math.log10(rounding_val)

    idx = len(num) - 1
    count = 0
    while idx >= 0 and num[idx] == "0":
        count += 1
        idx -= 1

    if count >= power:
        # handling double multiplier case
        return float(num)
    else:
        return none_handling_operation(float(num), rounding_val, "*", False)


# Used to get the data value where the column name is contained within the list
def sum_value_equal(df: pd.DataFrame, column_list: list, rounding_val: float):
    result_val = None
    for _, row in df.iterrows():
        if row["Unnamed: 3"] in column_list:
            data_val = (
                None
                if (
                    np.isnan(row["Unnamed: 1"])
                    if row["Unnamed: 1"] is not None
                    else True
                )
                else rounding_calc_and_check(row["Unnamed: 1"], float(rounding_val))
            )
            result_val = none_handling_operation(result_val, data_val, "+", True)

    return result_val


# Used to get the data value where the starting from column_start iterated to column_end, can be optionally specified to select only contains a certain key word
# contain_keyword = None -> all column will be selected. contain_keyword != None -> only select column that contains the 'keyword'
def sum_value_range(
    df: pd.DataFrame,
    column_start: str,
    column_end: str,
    rounding_val: float,
    contain_keyword: str = None,
):
    result_val = None
    continue_process = False
    for _, row in df.iterrows():
        # Only start process when find column_start and end process when find column_end
        if row["Unnamed: 3"] == column_start:
            continue_process = True
            starting_point = True
        if continue_process:
            #  Check if the column contains the keyword if the contain_keyword is not None
            #  Default check_found = True
            #  Case : contain_keyword is None, then every column will be selected -> check_found is True
            #  Case : contain_keyword is not None, if the column contains keyword -> check_found is still True, otherwise, check_found becomes False
            check_found = True
            if contain_keyword is not None and not contain_keyword in row["Unnamed: 3"]:
                check_found = False

            # Only select if check_found is True
            if check_found:
                data_val = (
                    None
                    if (
                        np.isnan(row["Unnamed: 1"])
                        if row["Unnamed: 1"] is not None
                        else True
                    )
                    else rounding_calc_and_check(row["Unnamed: 1"], float(rounding_val))
                )
                result_val = none_handling_operation(result_val, data_val, "+", True)

            if row["Unnamed: 3"] == column_end and not starting_point:
                continue_process = False
                break

            starting_point = False

    if continue_process:
        print(f"[ERROR] Column end {column_end} is not found!")

    return result_val


def load_data_dict(
    filename: str,
    sheet_mapping: list[tuple[list[str], dict[str, list[str]]]],
    rounding_val: float,
):
    # Create dict using metrics template
    combined_dict = dict()
    for sheet_codes, mapping in sheet_mapping:
        data_dict = dict()
        for metric in mapping.keys():
            data_dict[metric] = None

        for sheet_name in sheet_codes:
            df = open_excel_file(filename, sheet_name)
            if df is not None:
                break

        if df is not None:
            # Iterate for data that can be directly selected
            for metric, sheet_rows in mapping.items():
                data_dict[metric] = sum_value_equal(df, sheet_rows, rounding_val)

        combined_dict.update(data_dict)

    return combined_dict


# Process balance sheet
def process_balance_sheet(
    filename: str,
    sheet_code_list: list,
    column_mapping: dict,
    metrics: list,
    rounding_val: float,
    currency_rate: float, 
    industry_key_idx: int,
):
    # Balance Sheet
    try:
        # Create dict using metrics template
        balance_sheet_dict = dict()
        for metric in metrics:
            balance_sheet_dict[metric] = None

        for sheet_name in sheet_code_list:
            df = open_excel_file(filename, sheet_name)
            if df is not None:
                break

        if df is not None:
            # Iterate for data that can be directly selected
            for _, row in df.iterrows():
                sheet_metric_name = row["Unnamed: 3"]
                if sheet_metric_name in column_mapping:
                    sheet_metric_val = row["Unnamed: 1"]
                    data_val = (
                        None
                        if (np.isnan(sheet_metric_val)
                            if sheet_metric_val is not None
                            else True
                        )
                        else rounding_calc_and_check(
                            sheet_metric_val, float(rounding_val)
                        )
                    )
                    if (type(column_mapping[sheet_metric_name])) == list:
                        for metric in column_mapping[sheet_metric_name]:
                            balance_sheet_dict[metric] = data_val
                    else:
                        balance_sheet_dict[column_mapping[sheet_metric_name]] = data_val

            # Dividing companies based on industries
            # Doing Calculations and Adjustments
            if industry_key_idx == 1:  # General
                balance_sheet_dict["cash_and_short_term_investments"] = sum_value_equal(
                    df,
                    ["Cash and cash equivalents", "Short-term investments"],
                    rounding_val,
                )
                balance_sheet_dict["total_debt"] = none_handling_operation(
                    none_handling_operation(
                        sum_value_equal(
                            df,
                            ["Short term bank loans", "Trust receipts payables"],
                            rounding_val,
                        ),
                        sum_value_range(
                            df,
                            "Current maturities of long-term liabilities",
                            "Current maturities of other borrowings",
                            rounding_val,
                        ),
                        "+",
                        True,
                    ),
                    sum_value_range(
                        df,
                        "Long-term liabilities net of current maturities",
                        "Long-term other borrowings",
                        rounding_val,
                    ),
                    "+",
                    True,
                )
                balance_sheet_dict["inventories"] = none_handling_operation(
                    none_handling_operation(
                        sum_value_equal(
                            df,
                            ["Current livestock inventories"],
                            rounding_val,
                        ),
                        sum_value_equal(
                            df,
                            ["Current real estate assets"],
                            rounding_val,
                        ),
                        "+",
                        True,
                    ),
                    sum_value_equal(
                        df,
                        ["Current inventories"],
                        rounding_val,
                    ),
                    "+",
                    True,
                )
                if balance_sheet_dict["prepaid_expenses"] == None:
                    balance_sheet_dict["prepaid_expenses"] = sum_value_equal(
                        df,
                        ["Prepaid expenses"],
                        rounding_val,
                    )

            elif industry_key_idx == 2:  # Property
                balance_sheet_dict["cash_and_short_term_investments"] = sum_value_equal(
                    df,
                    ["Cash and cash equivalents", "Short-term investments"],
                    rounding_val,
                )
                balance_sheet_dict["total_debt"] = none_handling_operation(
                    none_handling_operation(
                        sum_value_equal(
                            df,
                            ["Short term bank loans", "Trust receipts payables"],
                            rounding_val,
                        ),
                        sum_value_range(
                            df,
                            "Current maturities of long-term liabilities",
                            "Current maturities of other borrowings",
                            rounding_val,
                        ),
                        "+",
                        True,
                    ),
                    sum_value_range(
                        df,
                        "Long-term liabilities net of current maturities",
                        "Long-term other borrowings",
                        rounding_val,
                    ),
                    "+",
                    True,
                )
                balance_sheet_dict["inventories"] = none_handling_operation(
                    sum_value_equal(
                        df,
                        ["Current real estate assets"],
                        rounding_val,
                    ),
                    sum_value_equal(
                        df,
                        ["Current inventories"],
                        rounding_val,
                    ),
                    "+",
                    True,
                )
                if balance_sheet_dict["prepaid_expenses"] == None:
                    balance_sheet_dict["prepaid_expenses"] = sum_value_equal(
                        df,
                        ["Prepaid expenses"],
                        rounding_val,
                    )

            elif industry_key_idx == 3:  # Infrastructure
                balance_sheet_dict["cash_and_short_term_investments"] = sum_value_equal(
                    df,
                    ["Cash and cash equivalents", "Short-term investments"],
                    rounding_val,
                )
                balance_sheet_dict["total_debt"] = none_handling_operation(
                    none_handling_operation(
                        sum_value_equal(
                            df,
                            ["Short term bank loans", "Trust receipts payables"],
                            rounding_val,
                        ),
                        sum_value_range(
                            df,
                            "Current maturities of long-term liabilities",
                            "Current maturities of other borrowings",
                            rounding_val,
                        ),
                        "+",
                        True,
                    ),
                    sum_value_range(
                        df,
                        "Long-term liabilities net of current maturities",
                        "Long-term other borrowings",
                        rounding_val,
                    ),
                    "+",
                    True,
                )
                balance_sheet_dict["inventories"] = none_handling_operation(
                    sum_value_equal(
                        df,
                        ["Current real estate assets"],
                        rounding_val,
                    ),
                    sum_value_equal(
                        df,
                        ["Current inventories"],
                        rounding_val,
                    ),
                    "+",
                    True,
                )
                if balance_sheet_dict["prepaid_expenses"] == None:
                    balance_sheet_dict["prepaid_expenses"] = sum_value_equal(
                        df,
                        ["Prepaid expenses"],
                        rounding_val,
                    )

            elif industry_key_idx == 4:  # Finance and Sharia
                balance_sheet_dict["gross_loan"] = sum_value_equal(
                    df, ["Loans third parties", "Loans related parties"], rounding_val
                )
                balance_sheet_dict["net_loan"] = none_handling_operation(
                    balance_sheet_dict["gross_loan"],
                    balance_sheet_dict["allowance_for_loans"],
                    "+",
                    True,
                )
                balance_sheet_dict["non_loan_asset"] = none_handling_operation(
                    balance_sheet_dict["total_asset"],
                    balance_sheet_dict["net_loan"],
                    "-",
                    False,
                )
                balance_sheet_dict["total_earning_asset"] = None  # TODO
                balance_sheet_dict["total_cash_and_due_from_banks"] = (
                    none_handling_operation(
                        sum_value_equal(
                            df,
                            ["Cash", "Current accounts with bank Indonesia"],
                            rounding_val,
                        ),
                        sum_value_range(
                            df,
                            "Current accounts with other banks",
                            "Allowance for impairment losses for current accounts with other bank",
                            rounding_val,
                        ),
                        "+",
                        True,
                    )
                )
                balance_sheet_dict["current_account"] = sum_value_range(
                    df,
                    "Current accounts",
                    "Current accounts related parties",
                    rounding_val,
                )
                balance_sheet_dict["savings_account"] = sum_value_range(
                    df, "Savings", "Savings related parties", rounding_val
                )
                balance_sheet_dict["time_deposit"] = sum_value_range(
                    df, "Time deposits", "Time deposits related parties", rounding_val
                )
                balance_sheet_dict["total_deposit"] = none_handling_operation(
                    none_handling_operation(
                        balance_sheet_dict["current_account"],
                        balance_sheet_dict["savings_account"],
                        "+",
                        True,
                    ),
                    balance_sheet_dict["time_deposit"],
                    "+",
                    True,
                )
                balance_sheet_dict["other_interest_bearing_liabilities"] = None  # TODO
                balance_sheet_dict["non_interest_bearing_liabilities"] = None  # TODO
                balance_sheet_dict["total_debt"] = None  # TODO

            elif industry_key_idx == 5:  # Securities
                balance_sheet_dict["cash_only"] = sum_value_equal(
                    df, ["Cash and cash equivalents", "Restricted funds"], rounding_val
                )
                balance_sheet_dict["cash_and_short_term_investments"] = None  # TODO
                balance_sheet_dict["total_debt"] = None  # TODO

            elif industry_key_idx == 6:  # Insurance
                "TODO: waiting unfinalized metrics"
                balance_sheet_dict["total_cash_and_due_from_banks"] = None  # TODO

            else:  # (industry_key_idx == 8): # Financing
                "TODO: waiting unfinalized metrics"
                balance_sheet_dict["total_debt"] = None  # TODO

            # Calculate the currency rate
            for k, v in balance_sheet_dict.items():
              balance_sheet_dict[k] = (v * currency_rate) if v is not None else None

            return balance_sheet_dict

        else:
            print(
                f"[FAILED] Cannot open balance sheet in file {filename}. Make sure to input the right file name and sheet name"
            )
            return None
    except Exception as e:
        print(f"[FAILED] Failed to process Balance Sheet data of {filename}: {e}")
        return None


# Process income statement
def process_income_statement(
    filename: str,
    sheet_code_list: list,
    column_mapping: dict,
    metrics: list,
    rounding_val: float,
    currency_rate: float, 
    industry_key_idx: int,
):
    # Income Statement
    try:
        # Create dict using metrics template
        income_statement_dict = dict()
        for metric in metrics:
            income_statement_dict[metric] = None

        for sheet_name in sheet_code_list:
            df = open_excel_file(filename, sheet_name)
            if df is not None:
                break

        if df is not None:
            for _, row in df.iterrows():
                sheet_metric_name = row["Unnamed: 3"]
                if sheet_metric_name in column_mapping:
                    sheet_metric_val = row["Unnamed: 1"]
                    if (np.isnan(sheet_metric_val) if sheet_metric_val is not None else True):
                        data_val = None
                    else:
                        if ((sheet_metric_name == "Basic earnings (loss) per share from continuing operations")):
                            # Exception case for Basic earnings
                            threshold = 1e-5 if currency_rate == 1 else 1e-10
                            if (abs(float(sheet_metric_val)) < threshold):
                                # Handling for doesnt make sense value
                                data_val = None
                            else:
                              data_val = float(sheet_metric_val)
                        else:
                            data_val = rounding_calc_and_check(sheet_metric_val, float(rounding_val))

                    # Check if in the type in column mapping is one-to-one or one-to-many
                    if (type(column_mapping[sheet_metric_name])) == list:
                        for metric in column_mapping[sheet_metric_name]:
                            income_statement_dict[metric] = data_val
                    else:
                        income_statement_dict[column_mapping[sheet_metric_name]] = (
                            data_val
                        )

            # Dividing companies based on industries
            # Doing Calculations and Adjustments
            if industry_key_idx == 1:  # General
                income_statement_dict["operating_expense"] = sum_value_equal(
                    df,
                    ["Selling expenses", "General and administrative expenses"],
                    rounding_val,
                )
                income_statement_dict["operating_income"] = none_handling_operation(
                    income_statement_dict["gross_income"],
                    income_statement_dict["operating_expense"],
                    "-",
                    True,
                )
                income_statement_dict["non_operating_income_or_loss"] = (
                    none_handling_operation(
                        income_statement_dict["pretax_income"],
                        income_statement_dict["operating_income"],
                        "-",
                        False,
                    )
                )
                income_statement_dict["ebit"] = none_handling_operation(
                    income_statement_dict["pretax_income"],
                    income_statement_dict["interest_expense_non_operating"],
                    "+",
                    False,
                )
                income_statement_dict["diluted_shares_outstanding"] = (
                    none_handling_operation(
                        income_statement_dict["profit_attributable_to_parent"],
                        income_statement_dict[
                            "basic_earnings_from_continuing_operations"
                        ],
                        "/",
                        False,
                    )
                )

            elif industry_key_idx == 2:  # Property
                income_statement_dict["operating_expense"] = sum_value_equal(
                    df,
                    ["Selling expenses", "General and administrative expenses"],
                    rounding_val,
                )
                income_statement_dict["operating_income"] = none_handling_operation(
                    income_statement_dict["gross_income"],
                    income_statement_dict["operating_expense"],
                    "-",
                    True,
                )
                income_statement_dict["non_operating_income_or_loss"] = (
                    none_handling_operation(
                        income_statement_dict["pretax_income"],
                        income_statement_dict["operating_income"],
                        "-",
                        False,
                    )
                )
                income_statement_dict["ebit"] = none_handling_operation(
                    income_statement_dict["pretax_income"],
                    income_statement_dict["interest_expense_non_operating"],
                    "+",
                    False,
                )
                income_statement_dict["diluted_shares_outstanding"] = (
                    none_handling_operation(
                        income_statement_dict["profit_attributable_to_parent"],
                        income_statement_dict[
                            "basic_earnings_from_continuing_operations"
                        ],
                        "/",
                        False,
                    )
                )

            elif industry_key_idx == 3:  # Infrastructure
                income_statement_dict["operating_expense"] = sum_value_equal(
                    df,
                    ["Selling expenses", "General and administrative expenses"],
                    rounding_val,
                )
                income_statement_dict["operating_income"] = none_handling_operation(
                    income_statement_dict["gross_income"],
                    income_statement_dict["operating_expense"],
                    "-",
                    True,
                )
                income_statement_dict["non_operating_income_or_loss"] = (
                    none_handling_operation(
                        income_statement_dict["pretax_income"],
                        income_statement_dict["operating_income"],
                        "-",
                        False,
                    )
                )
                income_statement_dict["ebit"] = none_handling_operation(
                    income_statement_dict["pretax_income"],
                    income_statement_dict["interest_expense_non_operating"],
                    "+",
                    False,
                )
                income_statement_dict["diluted_shares_outstanding"] = (
                    none_handling_operation(
                        income_statement_dict["profit_attributable_to_parent"],
                        income_statement_dict[
                            "basic_earnings_from_continuing_operations"
                        ],
                        "/",
                        False,
                    )
                )

            elif industry_key_idx == 4:  # Finance and Sharia
                income_statement_dict["net_interest_income"] = none_handling_operation(
                    income_statement_dict["interest_income"],
                    income_statement_dict["interest_expense"],
                    "+",
                    True,
                )
                income_statement_dict["net_premium_income"] = none_handling_operation(
                    income_statement_dict["premium_income"],
                    income_statement_dict["premium_expense"],
                    "+",
                    True,
                )
                income_statement_dict["non_interest_income"] = sum_value_range(
                    df, "Investments income", "Other operating income", rounding_val
                )
                income_statement_dict["total_revenue"] = none_handling_operation(
                    none_handling_operation(
                        income_statement_dict["net_interest_income"],
                        income_statement_dict["net_premium_income"],
                        "+",
                        True,
                    ),
                    income_statement_dict["non_interest_income"],
                    "+",
                    True,
                )
                income_statement_dict["operating_expense"] = sum_value_range(
                    df,
                    "General and administrative expenses",
                    "Other operating expenses",
                    rounding_val,
                )
                income_statement_dict["provision"] = none_handling_operation(
                    sum_value_range(
                        df,
                        "Recovery of impairment loss",
                        "Recovery of estimated loss of commitments and contingency",
                        rounding_val,
                    ),
                    sum_value_range(
                        df,
                        "Allowances for impairment losses",
                        "Reversal (expense) of estimated losses on commitments and contingencies",
                        rounding_val,
                    ),
                    "+",
                    True,
                )
                income_statement_dict["non_operating_income_or_loss"] = sum_value_range(
                    df,
                    "Non-operating income and expense",
                    "Share of profit (loss) of joint ventures accounted for using equity method",
                    rounding_val,
                )
                income_statement_dict["net_income"] = none_handling_operation(
                    sum_value_equal(df, ["Total profit (loss)"], rounding_val),
                    income_statement_dict["minorities"],
                    "+",
                    True,
                )
                income_statement_dict["diluted_shares_outstanding"] = (
                    none_handling_operation(
                        income_statement_dict["profit_attributable_to_parent"],
                        income_statement_dict[
                            "basic_earnings_from_continuing_operations"
                        ],
                        "/",
                        False,
                    )
                )

            elif industry_key_idx == 5:  # Securities
                income_statement_dict["total_revenue"] = sum_value_range(
                    df,
                    "Statement of profit or loss and other comprehensive income",
                    "Gains (losses) on changes in fair value of marketable securities",
                    rounding_val,
                )
                income_statement_dict["operating_expense"] = sum_value_equal(
                    df,
                    ["Selling expenses", "General and administrative expenses"],
                    rounding_val,
                )
                income_statement_dict["operating_income"] = None  # TODO
                # income_statement_dict['non_operating_income_or_loss'] = none_handling_operation(income_statement_dict['pretax_income'], income_statement_dict['operating_income'], '-', False) # TODO
                income_statement_dict["ebit"] = none_handling_operation(
                    income_statement_dict["pretax_income"],
                    income_statement_dict["interest_expense_non_operating"],
                    "+",
                    False,
                )
                income_statement_dict["diluted_shares_outstanding"] = (
                    none_handling_operation(
                        income_statement_dict["profit_attributable_to_parent"],
                        income_statement_dict[
                            "basic_earnings_from_continuing_operations"
                        ],
                        "/",
                        False,
                    )
                )

            elif industry_key_idx == 6:  # Insurance
                "TODO: waiting unfinalized metrics"
                income_statement_dict["cost_of_revenue"] = None  # TODO
                income_statement_dict["operating_expense"] = None  # TODO
                income_statement_dict["non_interest_income"] = None  # TODO

                income_statement_dict["diluted_shares_outstanding"] = (
                    none_handling_operation(
                        income_statement_dict["profit_attributable_to_parent"],
                        income_statement_dict[
                            "basic_earnings_from_continuing_operations"
                        ],
                        "/",
                        False,
                    )
                )

            else:  # (industry_key_idx == 8): # Financing
                "TODO: waiting unfinalized metrics"
                income_statement_dict["operating_expense"] = sum_value_range(
                    df, "Selling expenses", "Other losses", rounding_val
                )
                income_statement_dict["gross_income"] = none_handling_operation(
                    income_statement_dict["non_operating_income_or_loss"],
                    income_statement_dict["operating_expense"],
                    "+",
                    True,
                )
                income_statement_dict["operating_income"] = none_handling_operation(
                    income_statement_dict["pretax_income"],
                    income_statement_dict["non_operating_income_or_loss"],
                    "-",
                    True,
                )
                income_statement_dict["total_revenue"] = none_handling_operation(
                    income_statement_dict["gross_income"],
                    income_statement_dict["cost_of_revenue"],
                    "+",
                    True,
                )
                income_statement_dict["interest_expense_non_operating"] = None  # TODO
                income_statement_dict["ebit"] = none_handling_operation(
                    income_statement_dict["pretax_income"],
                    income_statement_dict["interest_expense_non_operating"],
                    "+",
                    False,
                )
                income_statement_dict["diluted_shares_outstanding"] = (
                    none_handling_operation(
                        income_statement_dict["profit_attributable_to_parent"],
                        income_statement_dict[
                            "basic_earnings_from_continuing_operations"
                        ],
                        "/",
                        False,
                    )
                )

            # All industries
            income_statement_dict["income_taxes"] = none_handling_operation(
                0,
                income_statement_dict["income_taxes"],
                "-",
                True,
            )

            # Calculate the currency rate
            for k, v in income_statement_dict.items():
              if (k != "diluted_shares_outstanding"):
                # Exception for `diluted shares oustanding` should not be multiplied by currency_rate
                income_statement_dict[k] = (v * currency_rate) if v is not None else None

            return income_statement_dict

        else:
            print(
                f"[FAILED] Cannot open income statement in file {filename}. Make sure to input the right file name and sheet name"
            )
            return None
    except Exception as e:
        print(f"[FAILED] Failed to process Income Statement data of {filename}: {e}")
        return None


# Process additional metrics spanning multiple sheets
def process_additional_metrics(
    filename: str,
    sheet_mapping: list[tuple[list[str], dict[str, list[str]]]],
    additional_data: dict,
    rounding_val: float,
    currency_rate: float, 
    industry_key_idx: int,
):
    # Additional metrics
    try:
        loaded_metrics = load_data_dict(filename, sheet_mapping, rounding_val)
        # Create dict using metrics template
        # Needs to be adjusted if a metric is added into additional_metrics_dict
        # TODO 
        additional_metrics_dict = {"ebitda": None}

        # Dividing companies based on industries
        # Doing Calculations and Adjustments
        if industry_key_idx == 1:  # General
            additional_metrics_dict["ebitda"] = none_handling_operation(
                additional_data["ebit"],
                loaded_metrics["depreciation_amortization"],
                "+",
            )

        elif industry_key_idx == 2:  # Property
            additional_metrics_dict["ebitda"] = none_handling_operation(
                additional_data["ebit"],
                loaded_metrics["depreciation_amortization"],
                "+",
            )

        elif industry_key_idx == 3:  # Infrastructure
            additional_metrics_dict["ebitda"] = none_handling_operation(
                additional_data["ebit"],
                loaded_metrics["depreciation_amortization"],
                "+",
            )

        elif industry_key_idx == 5:  # Securities
            additional_metrics_dict["ebitda"] = None  # TODO

        elif industry_key_idx == 8:  # Financing
            additional_metrics_dict["ebitda"] = None  # TODO
        
        # Notes:
        # Bank and Insurance Industries does not have EBITDA

        # Needs to be adjusted if a metric is added into additional_metrics_dict
        # TODO 
        additional_metrics_dict["ebitda"] = additional_metrics_dict["ebitda"] * currency_rate if additional_metrics_dict["ebitda"] is not None else None

        return additional_metrics_dict

    except Exception as e:
        print(f"[FAILED] Failed to process additional metrics of {filename}: {e}")
        return None


# Process cash flow
def process_cash_flow(
    filename: str,
    sheet_code_list: list,
    column_mapping: dict,
    metrics: list,
    rounding_val: float,
    currency_rate: float, 
    industry_key_idx: int,
):
    # Cash flow
    try:
        # Create dict using metrics template
        cash_flow_dict = dict()
        for metric in metrics:
            cash_flow_dict[metric] = None

        for sheet_name in sheet_code_list:
            df = open_excel_file(filename, sheet_name)
            if df is not None:
                break

        if df is not None:
            for _, row in df.iterrows():
                sheet_metric_name = row["Unnamed: 3"]
                if row["Unnamed: 3"] in column_mapping:
                    sheet_metric_val = row["Unnamed: 1"]
                    data_val = (
                        None
                        if (
                            np.isnan(sheet_metric_val)
                            if sheet_metric_val is not None
                            else True
                        )
                        else rounding_calc_and_check(
                            sheet_metric_val, float(rounding_val)
                        )
                    )
                    if (type(column_mapping[sheet_metric_name])) == list:
                        for metric in column_mapping[sheet_metric_name]:
                            cash_flow_dict[metric] = data_val
                    else:
                        cash_flow_dict[column_mapping[sheet_metric_name]] = data_val

            # Dividing companies based on industries
            # Doing Calculations and Adjustments
            if industry_key_idx in [1, 2, 3, 5, 6, 8]:
                cash_flow_dict["capital_expenditure"] = sum_value_range(
                    df,
                    "Cash flows from investing activities",
                    "Other cash inflows (outflows) from investing activities",
                    rounding_val,
                    "Payments",
                )
                cash_flow_dict["free_cash_flow"] = none_handling_operation(
                    cash_flow_dict["operating_cash_flow"],
                    cash_flow_dict["capital_expenditure"],
                    "-",
                    False,
                )
            else:  # (industry_key == 4)
                cash_flow_dict["high_quality_liquid_asset"] = None  # TODO
                cash_flow_dict["cash_outflow"] = None  # TODO
                cash_flow_dict["cash_inflow"] = None  # TODO
                cash_flow_dict["net_cash_flow"] = None  # TODO
                cash_flow_dict["realized_capital_goods_investment"] = None  # TODO
                cash_flow_dict["free_cash_flow"] = None  # TODO

            # Calculate the currency rate
            for k, v in cash_flow_dict.items():
              cash_flow_dict[k] = (v * currency_rate) if v is not None else None

            return cash_flow_dict

        else:
            print(
                f"[FAILED] Cannot open cash flow file {filename}. Make sure to input the right file name and sheet name"
            )
            return None

    except Exception as e:
        print(f"[FAILED] Failed to process Cash Flow data of {filename}: {e}")
        return None


# Call the API to download the Excel file data
def download_excel_file(url: str, filename: str, use_proxy: bool = False):
    try:
        print(f"[DOWNLOAD] Downloading from {url}")

        if not use_proxy:
            # Construct the request
            req = urllib.request.Request(url, headers=create_headers())

            # Open the request and write the response to a file
            response = urllib.request.urlopen(req)
            out_file = open(filename, "wb")

            if int(response.getcode()) == 200:
                data = response.read()  # Read the response data
                out_file.write(data)  # Write the data to a file
            else:
                print(f"[FAILED] Failed to get data status code {response.getcode()}")

        else:
            response = requests.get(
                url, allow_redirects=True, proxies=PROXIES, verify=False
            )

            if int(response.status_code) == 200:
                # Write the response content to a file
                with open(filename, "wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)
            else:
                print(f"[FAILED] Failed to get data status code {response.status_code}")

        return True
    except urllib.request.HTTPError as httper:
        print(f"[FAILED] Failed to download excel file for {filename}: {httper}")
        return httper.getcode() == 404
    except Exception as e:
        print(f"[FAILED] Failed to download excel file for {filename}: {e}")
        return False


# Tries to open Excel File, return None if fails
def open_excel_file(filename: str, sheetname: str):
    try:
        df = pd.read_excel(filename, sheet_name=sheetname)
        return df
    except Exception as e:
        print(f"[WRONG FILE/ SHEET] Failed to open file {filename}: {e}")
        return None


# Checking the first sheet => Information Sheet of the excel
# Return the rounding level if success, otherwise None
def check_information_sheet(filename: str, year_arg: int, period_arg: str):
    try:
        df = open_excel_file(filename, "1000000")
        if df is not None:
            for _, row in df.iterrows():
                # Cast row['Unnamed: 2'] to string
                if "Level of rounding" in str(row["Unnamed: 2"]):
                    rounding = str(row["Unnamed: 1"]).upper()
                    for k, v in ROUNDING_LEVEL_MAPPING.items():
                        if k in rounding:
                            rounding_val = v
                if ("Description of presentation currency" in str(row['Unnamed: 2'])):
                    try:
                      currency_symbol = str(row['Unnamed: 1']).split("/")[1].strip()
                      if (currency_symbol == "USD"):
                        adjusted_period_arg = "tw4" if period_arg == "audit" else period_arg
                        date_param = date_format(adjusted_period_arg, year_arg)
                        currency_rate = get_rate(date_param)
                      else: # Should be IDR
                        currency_rate = 1
                    except Exception as e:
                      print(f"[FAILED] Failed to process currency rate. Assuming using IDR rate.")
                      currency_rate = 1
                      
            return rounding_val, currency_rate
        else:
            print(
                f"[FAILED] Cannot open information sheet in file {filename}. Make sure to input the right file name and sheet name"
            )
            return None, None

    except Exception as e:
        print(f"[FAILED] Failed to open Information Sheet: {e}")
        return None


# Process the data of a certain excel file
def process_excel(
    symbol: str, period: str, year: int, filename: str, rounding_val: int, currency_rate: float,  process: int
):
    try:
        # Get industry_key_idx
        wb = xl.load_workbook(filename)
        balance_sheet_code = wb.sheetnames[3]
        industry_key_idx = int(balance_sheet_code[0])

        # Check Information Sheet
        mapping_dict = UNIVERSAL_MAPPING[industry_key_idx]
        date = date_format(period, year)
        result_dict = {
            "symbol": symbol,
            "date": date,
            "industry_code": industry_key_idx,
        }

        print(
            f"[PROCESS P{process}] Processing {symbol} date {date} industry_key {industry_key_idx}..."
        )

        # Process each data
        print(f"[BS P{process}] Processing Balance Sheet ...")
        balance_sheet_data = process_balance_sheet(
            filename,
            mapping_dict["bs_sheet_code"],
            mapping_dict["bs_column_mapping"],
            mapping_dict["bs_metrics"],
            rounding_val,
            currency_rate, 
            industry_key_idx,
        )
        print(f"[IS P{process}] Processing Income Statement ...")
        income_statement_data = process_income_statement(
            filename,
            mapping_dict["is_sheet_code"],
            mapping_dict["is_column_mapping"],
            mapping_dict["is_metrics"],
            rounding_val,
            currency_rate, 
            industry_key_idx,
        )
        print(f"[CF P{process}] Processing Cash Flow ...")
        cash_flow_data = process_cash_flow(
            filename,
            mapping_dict["cf_sheet_code"],
            mapping_dict["cf_column_mapping"],
            mapping_dict["cf_metrics"],
            rounding_val,
            currency_rate, 
            industry_key_idx,
        )
        print(f"[ADD P{process}] Processing Additional Metrics ...")
        additional_data = process_additional_metrics(
            filename,
            mapping_dict["additional_mapping"],
            income_statement_data,
            rounding_val,
            currency_rate, 
            industry_key_idx,
        )

        try:
            if (industry_key_idx in [1,2,3,5,8]):
              income_statement_data["ebitda"] = additional_data["ebitda"]
        except:
            print(f"[ADD P{process}] Fail to insert Additional Metrics")

        # Update and combine dictionary
        result_dict["balance_sheet_metrics"] = balance_sheet_data
        result_dict["income_stmt_metrics"] = income_statement_data
        result_dict["cash_flow_metrics"] = cash_flow_data

        # # For printing only
        # for k, v in result_dict.items():
        #   print(f"\t[{k} => {v}]")

        return result_dict
    except Exception as e:
        print(
            f"[FAILED P{process}] Cannot get the data of {symbol} period {period} year {year}: {e}"
        )
        return None


# Main function to process the combined data (as a dataframe)
def process_dataframe(
    df: pd.DataFrame,
    period_arg: str,
    year_arg: int,
    shared_list: list,
    process: int = 1,
):
    scrapped_symbol_list = df["symbol"].unique()
    data_length = len(df)
    symbol_data_length = len(scrapped_symbol_list)

    print(
        f"[PROGRESS] {data_length} data of {symbol_data_length} companies are available to be scraped"
    )

    # Container for Data
    result_data_list_quarter = list()
    result_data_list_annual = list()
    failed_list = list()

    # Iterate each symbol based on the range_limit
    for symbol in scrapped_symbol_list:
        curr_symbol_df = df[df["symbol"] == symbol]
        row = curr_symbol_df.iloc[0]
      
        # MARK
        # Download excel file
        filename = os.path.join(
            DATA_IDX_SHEETS_DIR,
            f"{row['symbol']}_{row['year']}_{row['period']}.xlsx",
        )
        url = f"{BASE_URL}{row['file_url']}".replace(" ", "%20")

        # Make 3 attempts to download the file
        attempt = 1
        limit_attempts = 3
        download_return = False
        while attempt <= limit_attempts and not download_return:
            download_return = download_excel_file(url, filename, True)
            attempt += 1
            if not download_return:
                if attempt > limit_attempts:
                    print(
                        f"[COMPLETE FAILED] Failed to download excel file from {url} after {limit_attempts} attempts"
                    )
                    failed_entry = {
                        "symbol": symbol,
                        "year": year_arg,
                        "period": period_arg,
                        "error_message": f"Failed to download excel file from {url}",
                    }
                    failed_list.append(failed_entry)
                else:
                    print(
                        f"[FAILED] Failed to download excel file from {url} after {attempt} attempts. Retrying..."
                    )
            time.sleep(1.5)

        # Give time delay to make sure the file is downloaded
        time.sleep(2.5)

        # Only proceed if the file is successfully downloaded
        if (download_return):
          try:
              # Check the rounding value and the currency rate of the file
              rounding_val, currency_rate = check_information_sheet(filename, year_arg, period_arg)
              # Process each excel data
              data = process_excel(
                  row["symbol"],
                  row["period"],
                  row["year"],
                  filename,
                  rounding_val,
                  currency_rate,
                  process,
              )
              if data is not None:
                  # For quarter data, needs further handling.
                  # On the other side, for annual data, we can directly insert into the store
                  if row["period"] == "tw4":
                      annual_data = data.copy()
                      annual_data["balance_sheet_metrics"] = (
                          json.dumps(annual_data["balance_sheet_metrics"])
                          if (annual_data["balance_sheet_metrics"] is not None)
                          else None
                      )
                      annual_data["income_stmt_metrics"] = (
                          json.dumps(annual_data["income_stmt_metrics"])
                          if (annual_data["income_stmt_metrics"] is not None)
                          else None
                      )
                      annual_data["cash_flow_metrics"] = (
                          json.dumps(annual_data["cash_flow_metrics"])
                          if (annual_data["cash_flow_metrics"] is not None)
                          else None
                      )
                      result_data_list_annual.append(annual_data)

                  print(
                      f"[SUCCESS] Successfully get the data for {symbol} period {row['period']} year {row['year']}"
                  )

                  # # MARK
                  # # Delete the excel file if the data has been processed
                  os.remove(filename)

                  # Further handling for quarter data
                  quarter_data = data.copy()

                  # Save income statement cumulative value as it is
                  quarter_data["income_stmt_metrics_cumulative"] = (
                      json.dumps(quarter_data["income_stmt_metrics"])
                      if (quarter_data["income_stmt_metrics"] is not None)
                      else None
                  )
                  # Save cash flow cumulative value as it is
                  quarter_data["cash_flow_metrics_cumulative"] = (
                      json.dumps(quarter_data["cash_flow_metrics"])
                      if (quarter_data["cash_flow_metrics"] is not None)
                      else None
                  )

                  # Process the difference for income statement data
                  if period_arg != "tw1":
                      prev_period_arg_mapping = {
                          "audit": "tw3",
                          "tw3": "tw2",
                          "tw2": "tw1",
                      }

                      # Doing subtraction since a quarter Q needs to be subtracted with previous Q
                      prev_period_arg = prev_period_arg_mapping[period_arg]
                      prev_period_date = date_format(prev_period_arg, year_arg)
                      prev_quarter_data = (
                          supabase_client.table("idx_financial_sheets_quarterly")
                          .select("income_stmt_metrics_cumulative", "cash_flow_metrics_cumulative")
                          .eq("date", prev_period_date)
                          .eq("symbol", symbol)
                          .execute()
                      ).data


                      # Subtract if the data exist for income statement
                      if (
                          len(prev_quarter_data) > 0
                          and quarter_data["income_stmt_metrics"] is not None
                          and prev_quarter_data[0]['income_stmt_metrics_cumulative'] is not None
                      ):
                          prev_income_statement_data = prev_quarter_data[
                              0
                          ]["income_stmt_metrics_cumulative"]
                          for key, value in quarter_data[
                              "income_stmt_metrics"
                          ].items():
                              if key != "diluted_shares_outstanding":  # Exception
                                  if key in prev_income_statement_data:
                                      prev_val = prev_income_statement_data[key]
                                      quarter_data["income_stmt_metrics"][key] = (
                                          none_handling_operation(
                                              value, prev_val, "-", False
                                          )
                                      )
                      else:
                          quarter_data["income_stmt_metrics"] = None
                          print(
                              f"[NOT FOUND PREVIOUS QUARTER] Income Statement Data for {symbol} with date {prev_period_date} is not found!"
                          )
                      
                      # Subtract if the data exist for cash flow
                      if (
                          len(prev_quarter_data) > 0
                          and quarter_data["cash_flow_metrics"] is not None
                          and prev_quarter_data[0]['cash_flow_metrics_cumulative'] is not None

                      ):
                          prev_cash_flow_data = prev_quarter_data[
                              0
                          ]["cash_flow_metrics_cumulative"]
                          for key, value in quarter_data[
                              "cash_flow_metrics"
                          ].items():
                              if key in prev_cash_flow_data:
                                  prev_val = prev_cash_flow_data[key]
                                  quarter_data["cash_flow_metrics"][key] = (
                                      none_handling_operation(
                                          value, prev_val, "-", False
                                      )
                                  )
                      else:
                          quarter_data["cash_flow_metrics"] = None
                          print(
                              f"[NOT FOUND PREVIOUS QUARTER] Cash Flow Data for {symbol} with date {prev_period_date} is not found!"
                          )

                      

                  # Dumps data to jsonb
                  quarter_data["balance_sheet_metrics"] = (
                      json.dumps(quarter_data["balance_sheet_metrics"])
                      if (quarter_data["balance_sheet_metrics"] is not None)
                      else None
                  )
                  quarter_data["income_stmt_metrics"] = (
                      json.dumps(quarter_data["income_stmt_metrics"])
                      if (quarter_data["income_stmt_metrics"] is not None)
                      else None
                  )
                  quarter_data["cash_flow_metrics"] = (
                      json.dumps(quarter_data["cash_flow_metrics"])
                      if (quarter_data["cash_flow_metrics"] is not None)
                      else None
                  )

                  # Insert all the data in current_symbol_list_data to result_data_list
                  result_data_list_quarter.append(quarter_data)

              else:
                  print(f"[FAILED] Failed to open and process {filename}")
                  failed_entry = {
                      "symbol": symbol,
                      "year": year_arg,
                      "period": period_arg,
                      "error_message": "Unable to open file",
                  }
                  failed_list.append(failed_entry)

          except Exception as e:
              print(f"[FAILED] Failed to open and process {filename} : {e}")
              failed_entry = {
                  "symbol": symbol,
                  "year": year_arg,
                  "period": period_arg,
                  "error_message": e,
              }
              failed_list.append(failed_entry)
        
        # Skip if it does not successfully download the file
        else:
          print(f"[SKIP] {symbol} is skipped! The file is not successfully downloaded!")



    # Put to Shared_List
    shared_list.append((result_data_list_quarter, result_data_list_annual, failed_list))
