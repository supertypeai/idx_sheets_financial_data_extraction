
# CONSIST OF CONSTANT VALUE FOR IDX SCRAPER

# Rounding Level
ROUNDING_LEVEL_MAPPING = {
  "SATUAN PENUH" : 1,
  "RIBUAN" : 1e3,
  "JUTAAN" : 1e6,
  "MILIARAN" : 1e9,
  "TRILIUNAN" : 1e12
}

BALANCE_SHEET_METRICS_BANK = ['gross_loan', 
                              "allowance_for_loans",
                              "net_loan",
                              "non_loan_asset",
                              "total_asset",
                              "total_earning_assets",
                              "cash_only",
                              "total_cash_and_due_from_banks",
                              "current_account", 
                              "savings_account", 
                              "time_deposit",
                              "total_deposit",
                              "other_interest_bearing_liabilities",
                              "non_interest_bearing_liabilities",
                              "total_liabilities", 
                              "total_equity",
                              "total_debt", 
                              "stockholders_equity"]

BALANCE_SHEET_METRICS_NON_BANK = ["total_current_asset",
                                  "total_non_current_asset",
                                  "total_asset",
                                  "cash_only",
                                  "total_cash_and_due_from_banks",
                                  "cash_and_short_term_investments",
                                  "total_current_liabilities", 
                                  "total_non_current_liabilities", 
                                  "total_liabilities", 
                                  "total_equity",
                                  "total_debt", 
                                  "stockholders_equity"]

INCOME_STATEMENT_METRICS_BANK = ["interest_income",
                                "interest_expense",
                                "net_interest_income",
                                "premium_income",
                                "premium_expense",
                                "net_premium_income",
                                "non_interest_income",
                                "total_revenue",
                                "operating_income",
                                "operating_expense",
                                "provision",
                                "non_operating_income_or_loss",
                                "pretax_income",
                                "income_taxes",
                                "minorities",
                                "net_income",
                                "diluted_shares_outstanding"]

INCOME_STATEMENT_METRICS_NON_BANK = ["total_revenue",
                                      "cost_of_revenue",
                                      "gross_income",
                                      "operating_expense",
                                      "operating_income",
                                      "non_operating_income_or_loss",
                                      "pretax_income",
                                      "income_taxes",
                                      "minorities",
                                      "net_income",
                                      "interest_expense_non_operating",
                                      "ebit",
                                      "ebitda",
                                      "diluted_shares_outstanding"]

CASH_FLOW_METRICS_BANK = ["high_quality_liquid_asset",
                          "cash_outflow",
                          "cash_inflow",
                          "net_cash_flow",
                          "operating_cash_flow",
                          "investing_cash_flow",
                          "financing_cash_flow",
                          "net_increased_decreased",
                          "realized_capital_goods_investment",
                          "free_cash_flow"]

CASH_FLOW_METRICS_NON_BANK = ["operating_cash_flow",
                              "investing_cash_flow",
                              "financing_cash_flow",
                              "net_increased_decreased",
                              "capital_expenditure",
                              "free_cash_flow"]



# MAPPING FORMAT 
# DICT = {
# [ENGLISH NAME IN IDX SHEETS]:  [NEW NAME]
# }

# Mapping For General Industry
# Only be used for data that can be directly selected, without calculation
GENERAL_BALANCE_SHEET_SHEET_CODE = ['1210000', '1220000', '1310000']
GENERAL_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total current assets" : "total_current_asset",
  "Total non-current assets" : "total_non_current_asset",
  "Total assets" : "total_asset",
  "Total current liabilities" : "total_current_liabilities",
  "Total non-current liabilities" : "total_non_current_liabilities",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
GENERAL_INCOME_STATEMENT_SHEET_CODE = ['1311000', '1321000', '1312000', '1322000']
GENERAL_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Sales and revenue" : "total_revenue",
  "Cost of sales and revenue" : "cost_of_revenue",
  "Total gross profit" : "gross_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities",
  "Profit (loss) attributable to parent entity" : "net_income",
  "Interest and finance costs" : "interest_expense_non_operating"
}
GENERAL_CASH_FLOW_SHEET_CODE = ['1510000']
GENERAL_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}




# Mapping For Property Industry
# Only be used for data that can be directly selected, without calculation
PROPERTY_BALANCE_SHEET_SHEET_CODE = ['2210000', '2220000']
PROPERTY_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total current assets" : "total_current_asset",
  "Total non-current assets" : "total_non_current_asset",
  "Total assets" : "total_asset",
  "Total current liabilities" : "total_current_liabilities",
  "Total non-current liabilities" : "total_non_current_liabilities",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
PROPERTY_INCOME_STATEMENT_SHEET_CODE = ['2311000', '1321000', '2321000', '2312000', '2322000']
PROPERTY_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Sales and revenue" : "total_revenue",
  "Cost of sales and revenue" : "cost_of_revenue",
  "Total gross profit" : "gross_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities",
  "Total profit (loss)" : "net_income",
  "Interest and finance costs" : "interest_expense_non_operating"
}
PROPERTY_CASH_FLOW_SHEET_CODE = ['2510000']
PROPERTY_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}





# Mapping For Infrastructure Industry
# Only be used for data that can be directly selected, without calculation
INFRASTRUCTURE_BALANCE_SHEET_SHEET_CODE = ['3210000', '3220000']
INFRASTRUCTURE_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total current assets" : "total_current_asset",
  "Total non-current assets" : "total_non_current_asset",
  "Total assets" : "total_asset",
  "Total current liabilities" : "total_current_liabilities",
  "Total non-current liabilities" : "total_non_current_liabilities",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
INFRASTRUCTURE_INCOME_STATEMENT_SHEET_CODE = ['3311000', '3312000', '3321000', '3322000']
INFRASTRUCTURE_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Sales and revenue" : "total_revenue",
  "Cost of sales and revenue" : "cost_of_revenue",
  "Total gross profit" : "gross_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities",
  "Profit (loss) attributable to parent entity" : "net_income",
  "Interest and finance costs" : "interest_expense_non_operating"
}
INFRASTRUCTURE_CASH_FLOW_SHEET_CODE = ['3510000']
INFRASTRUCTURE_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}




# Mapping For Finance and Sharia Industry
# Only be used for data that can be directly selected, without calculation
FINANCE_SHARIA_BALANCE_SHEET_SHEET_CODE = ['4220000', '4210000']
FINANCE_SHARIA_BALANCE_SHEET_COLUMN_MAPPING = {
  "Allowance for impairment losses for loans" : "allowance_for_loans",
  "Total assets" : "total_asset",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
  "Cash" : "cash_only",
}
FINANCE_SHARIA_INCOME_STATEMENT_SHEET_CODE = ['4322000', '4312000']
FINANCE_SHARIA_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Interest income" : "interest_income",
  "Interest expenses" : "interest_expense",
  "Revenue from insurance premiums" : "premium_income",
  "Claim expenses" : "premium_expense",
  "Total profit from operation" : "operating_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities"
}
FINANCE_SHARIA_CASH_FLOW_SHEET_CODE = ['4510000']
FINANCE_SHARIA_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}



# Mapping For Securities Industry
# Only be used for data that can be directly selected, without calculation
SECURITIES_BALANCE_SHEET_SHEET_CODE = ['5220000', '5210000']
SECURITIES_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total assets" : "total_asset",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
SECURITIES_INCOME_STATEMENT_SHEET_CODE = ['5311000', '5321000', '5322000', '5312000']
SECURITIES_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Total profit (loss)" : "net_income",
  "Other expenses" : "interest_expense_non_operating"
}
SECURITIES_CASH_FLOW_SHEET_CODE = ['5510000']
SECURITIES_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}




# Mapping For Insurance Industry
# Only be used for data that can be directly selected, without calculation
INSURANCE_BALANCE_SHEET_SHEET_CODE = ['6220000', '6210000']
INSURANCE_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total assets" : "total_asset",
  "Cash and cash equivalents" : "cash_only",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
INSURANCE_INCOME_STATEMENT_SHEET_CODE = ['6312000', '6322000', '6311000', '6321000']
INSURANCE_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Revenue from insurance premiums" : "total_revenue",
  "Total profit (loss) from continuing operations" : "operating_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Total profit (loss)" : "net_income",
}
INSURANCE_CASH_FLOW_SHEET_CODE = ['6510000']
INSURANCE_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}



# Mapping For Financing Industry
# Only be used for data that can be directly selected, without calculation
FINANCING_BALANCE_SHEET_SHEET_CODE = ['8220000', '8210000']
FINANCING_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total assets" : "total_asset",
  "Cash and cash equivalents" : ["cash_only", "cash_and_short_term_investments"],
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",

}
FINANCING_INCOME_STATEMENT_SHEET_CODE = ['8312000', '8322000', '8321000', '8311000']
FINANCING_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Interest and finance income" : "total_revenue",
  "Provision for impairment losses" : "non_operating_income_or_loss",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Total profit (loss)" : "net_income",
  "Total profit (loss) from continuing operations" : "operating_income"
}
FINANCING_CASH_FLOW_SHEET_CODE = ['8510000']
FINANCING_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}



# UNIVERSAL MAPPING
# bs => Balance Sheet, is => Income Statement, cf => Cash Flow
UNIVERSAL_MAPPING = {
  1 : {
    'bs_sheet_code' : GENERAL_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : GENERAL_BALANCE_SHEET_COLUMN_MAPPING,
    'bs_metrics' : BALANCE_SHEET_METRICS_NON_BANK,
    'is_sheet_code' : GENERAL_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : GENERAL_INCOME_STATEMENT_COLUMN_MAPPING,
    'is_metrics' : INCOME_STATEMENT_METRICS_NON_BANK,
    'cf_sheet_code' : GENERAL_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : GENERAL_CASH_FLOW_COLUMN_MAPPING,
    'cf_metrics' : CASH_FLOW_METRICS_NON_BANK
  },
  2 : {
    'bs_sheet_code' : PROPERTY_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : PROPERTY_BALANCE_SHEET_COLUMN_MAPPING,
    'bs_metrics' : BALANCE_SHEET_METRICS_NON_BANK,
    'is_sheet_code' : PROPERTY_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : PROPERTY_INCOME_STATEMENT_COLUMN_MAPPING,
    'is_metrics' : INCOME_STATEMENT_METRICS_NON_BANK,
    'cf_sheet_code' : PROPERTY_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : PROPERTY_CASH_FLOW_COLUMN_MAPPING,
    'cf_metrics' : CASH_FLOW_METRICS_NON_BANK
  },
  3 : {
    'bs_sheet_code' : INFRASTRUCTURE_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : INFRASTRUCTURE_BALANCE_SHEET_COLUMN_MAPPING,
    'bs_metrics' : BALANCE_SHEET_METRICS_NON_BANK,
    'is_sheet_code' : INFRASTRUCTURE_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : INFRASTRUCTURE_INCOME_STATEMENT_COLUMN_MAPPING,
    'is_metrics' : INCOME_STATEMENT_METRICS_NON_BANK,
    'cf_sheet_code' : INFRASTRUCTURE_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : INFRASTRUCTURE_CASH_FLOW_COLUMN_MAPPING,
    'cf_metrics' : CASH_FLOW_METRICS_NON_BANK
  },
  4 : {
    'bs_sheet_code' : FINANCE_SHARIA_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : FINANCE_SHARIA_BALANCE_SHEET_COLUMN_MAPPING,
     'bs_metrics' : BALANCE_SHEET_METRICS_BANK,
    'is_sheet_code' : FINANCE_SHARIA_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : FINANCE_SHARIA_INCOME_STATEMENT_COLUMN_MAPPING,
    'is_metrics' : INCOME_STATEMENT_METRICS_BANK,
    'cf_sheet_code' : FINANCE_SHARIA_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : FINANCE_SHARIA_CASH_FLOW_COLUMN_MAPPING,
    'cf_metrics' : CASH_FLOW_METRICS_BANK
  },
  5 : {
    'bs_sheet_code' : SECURITIES_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : SECURITIES_BALANCE_SHEET_COLUMN_MAPPING,
    'bs_metrics' : BALANCE_SHEET_METRICS_NON_BANK,
    'is_sheet_code' : SECURITIES_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : SECURITIES_INCOME_STATEMENT_COLUMN_MAPPING,
    'is_metrics' : INCOME_STATEMENT_METRICS_NON_BANK,
    'cf_sheet_code' : SECURITIES_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : SECURITIES_CASH_FLOW_COLUMN_MAPPING,
    'cf_metrics' : CASH_FLOW_METRICS_NON_BANK
  },
  6 : {
    'bs_sheet_code' : INSURANCE_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : INSURANCE_BALANCE_SHEET_COLUMN_MAPPING,
    'bs_metrics' : BALANCE_SHEET_METRICS_NON_BANK,
    'is_sheet_code' : INSURANCE_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : INSURANCE_INCOME_STATEMENT_COLUMN_MAPPING,
    'is_metrics' : INCOME_STATEMENT_METRICS_NON_BANK,
    'cf_sheet_code' : INSURANCE_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : INSURANCE_CASH_FLOW_COLUMN_MAPPING,
    'cf_metrics' : CASH_FLOW_METRICS_NON_BANK
  },
  8 : {
    'bs_sheet_code' : FINANCING_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : FINANCING_BALANCE_SHEET_COLUMN_MAPPING,
    'bs_metrics' : BALANCE_SHEET_METRICS_NON_BANK,
    'is_sheet_code' : FINANCING_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : FINANCING_INCOME_STATEMENT_COLUMN_MAPPING,
    'is_metrics' : INCOME_STATEMENT_METRICS_NON_BANK,
    'cf_sheet_code' : FINANCING_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : FINANCING_CASH_FLOW_COLUMN_MAPPING,
    'cf_metrics' : CASH_FLOW_METRICS_NON_BANK
  },
}