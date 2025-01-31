
# CONSIST OF CONSTANT VALUE FOR IDX SCRAPER

# Rounding Level
ROUNDING_LEVEL_MAPPING = {
  "SATUAN PENUH" : 1,
  "RIBUAN" : 1e3,
  "JUTAAN" : 1e6,
  "MILIARAN" : 1e9,
  "TRILIUNAN" : 1e12
}


# MAPPING FORMAT 
# DICT = {
# [ENGLISH NAME IN IDX SHEETS]:  [NEW NAME]}

# Mapping For General Industry
# Only be used for data that can be directly selected, without calculation
GENERAL_BALANCE_SHEET_SHEET_CODE = ['1210000', '1220000', '1310000']
GENERAL_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total current assets" : "total_current_assets",
  "Total non-current assets" : "total_non_current_assets",
  "Total assets" : "total_assets",
  "Total current liabilities" : "total_current_liabilities",
  "Total non-current liabilities" : "total_non_current_liabilities",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
GENERAL_INCOME_STATEMENT_SHEET_CODE = ['1311000', '1321000']
GENERAL_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Sales and revenue" : "total_revenue",
  "Cost of sales and revenue" : "cost of revenue",
  "Total gross profit" : "gross_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities",
  "Profit (loss) attributable to parent entity" : "net_income",
  "Interest and finance costs" : "interest_expense_non_operating"
}
GENERAL_CASH_FLOW_SHEET_CODE = ['1510000']
GENERAL_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "net_operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "net_investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "net_financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}




# Mapping For Property Industry
# Only be used for data that can be directly selected, without calculation
PROPERTY_BALANCE_SHEET_SHEET_CODE = ['2210000']
PROPERTY_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total current assets" : "total_current_assets",
  "Total non-current assets" : "total_non_current_assets",
  "Total assets" : "total_assets",
  "Total current liabilities" : "total_current_liabilities",
  "Total non-current liabilities" : "total_non_current_liabilities",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
PROPERTY_INCOME_STATEMENT_SHEET_CODE = ['2311000', '1321000']
PROPERTY_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Sales and revenue" : "total_revenue",
  "Cost of sales and revenue" : "cost of revenue",
  "Total gross profit" : "gross_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities",
  "Total profit (loss)" : "net_income",
  "Interest and finance costs" : "interest_expense_non_operating"
}
PROPERTY_CASH_FLOW_SHEET_CODE = ['2510000']
PROPERTY_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "net_operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "net_investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "net_financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}





# Mapping For Infrastructure Industry
# Only be used for data that can be directly selected, without calculation
INFRASTRUCTURE_BALANCE_SHEET_SHEET_CODE = ['3210000', '3220000']
INFRASTRUCTURE_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total current assets" : "total_current_assets",
  "Total non-current assets" : "total_non_current_assets",
  "Total assets" : "total_assets",
  "Total current liabilities" : "total_current_liabilities",
  "Total non-current liabilities" : "total_non_current_liabilities",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
INFRASTRUCTURE_INCOME_STATEMENT_SHEET_CODE = ['3311000', '3312000']
INFRASTRUCTURE_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Sales and revenue" : "total_revenue",
  "Cost of sales and revenue" : "cost of revenue",
  "Total gross profit" : "gross_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities",
  "Profit (loss) attributable to parent entity" : "net_income",
  "Interest and finance costs" : "interest_expense_non_operating"
}
INFRASTRUCTURE_CASH_FLOW_SHEET_CODE = ['3510000']
INFRASTRUCTURE_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "net_operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "net_investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "net_financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}




# Mapping For Finance and Sharia Industry
# Only be used for data that can be directly selected, without calculation
FINANCE_SHARIA_BALANCE_SHEET_SHEET_CODE = ['4220000']
FINANCE_SHARIA_BALANCE_SHEET_COLUMN_MAPPING = {
  "Allowance for impairment losses for loans" : "allowance_for_loans",
  "Total assets" : "total_assets",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
  "Cash" : "cash_only",
}
FINANCE_SHARIA_INCOME_STATEMENT_SHEET_CODE = ['4322000']
FINANCE_SHARIA_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Interest income" : "interest_income",
  "Interest expenses" : "interest_expenses",
  "Revenue from insurance premiums" : "premium_income",
  "Claim expenses" : "premium_expense",
  "Total profit from operation" : "operating_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Profit (loss) attributable to non-controlling interests" : "minorities"
}
FINANCE_SHARIA_CASH_FLOW_SHEET_CODE = ['4510000']
FINANCE_SHARIA_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "net_operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "net_investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "net_financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}



# Mapping For Securities Industry
# Only be used for data that can be directly selected, without calculation
SECURITIES_BALANCE_SHEET_SHEET_CODE = ['5220000']
SECURITIES_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total assets" : "total_assets",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
SECURITIES_INCOME_STATEMENT_SHEET_CODE = ['5311000']
SECURITIES_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Total profit (loss)" : "net_income",
  "Other expenses" : "interest_expense_non_operating"
}
SECURITIES_CASH_FLOW_SHEET_CODE = ['5510000']
SECURITIES_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "net_operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "net_investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "net_financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}




# Mapping For Insurance Industry
# Only be used for data that can be directly selected, without calculation
INSURANCE_BALANCE_SHEET_SHEET_CODE = ['6220000']
INSURANCE_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total assets" : "total_assets",
  "Cash and cash equivalents" : "cash_only",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",
}
INSURANCE_INCOME_STATEMENT_SHEET_CODE = ['6312000']
INSURANCE_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Revenue from insurance premiums" : "total_revenue",
  "Total profit (loss) from continuing operations" : "operating_income",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",
  "Total profit (loss)" : "net_income",
}
INSURANCE_CASH_FLOW_SHEET_CODE = ['6510000']
INSURANCE_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "net_operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "net_investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "net_financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}



# Mapping For Financing Industry
# Only be used for data that can be directly selected, without calculation
FINANCING_BALANCE_SHEET_SHEET_CODE = ['8220000']
FINANCING_BALANCE_SHEET_COLUMN_MAPPING = {
  "Total assets" : "total_assets",
  "Cash and cash equivalents" : "cash_only",
  "Cash and cash equivalents" : "cash_and_short_term_investments",
  "Total liabilities" : "total_liabilities",
  "Total equity" : "total_equity",
  "Total equity attributable to equity owners of parent entity" : "stockholders_equity",

}
FINANCING_INCOME_STATEMENT_SHEET_CODE = ['8312000', '8322000']
FINANCING_INCOME_STATEMENT_COLUMN_MAPPING = {
  "Interest and finance income" : "total_revenue",
  "Total profit (loss) before tax" : "pretax_income",
  "Tax benefit (expenses)" : "income_taxes",

  "Total profit (loss)" : "net_income",
  "Total profit (loss) from continuing operations" : "operating_income"
}
FINANCING_CASH_FLOW_SHEET_CODE = ['8510000']
FINANCING_CASH_FLOW_COLUMN_MAPPING = {
  "Total net cash flows received from (used in) operating activities" : "net_operating_cash_flow",
  "Total net cash flows received from (used in) investing activities" : "net_investing_cash_flow",
  "Total net cash flows received from (used in) financing activities" : "net_financing_cash_flow",
  "Total net increase (decrease) in cash and cash equivalents" : "net_increased_decreased",
}



# UNIVERSAL MAPPING
# bs => Balance Sheet, is => Income Statement, cf => Cash Flow
UNIVERSAL_MAPPING = {
  1 : {
    'bs_sheet_code' : GENERAL_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : GENERAL_BALANCE_SHEET_COLUMN_MAPPING,
    'is_sheet_code' : GENERAL_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : GENERAL_INCOME_STATEMENT_COLUMN_MAPPING,
    'cf_sheet_code' : GENERAL_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : GENERAL_CASH_FLOW_COLUMN_MAPPING
  },
  2 : {
    'bs_sheet_code' : PROPERTY_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : PROPERTY_BALANCE_SHEET_COLUMN_MAPPING,
    'is_sheet_code' : PROPERTY_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : PROPERTY_INCOME_STATEMENT_COLUMN_MAPPING,
    'cf_sheet_code' : PROPERTY_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : PROPERTY_CASH_FLOW_COLUMN_MAPPING
  },
  3 : {
    'bs_sheet_code' : INFRASTRUCTURE_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : INFRASTRUCTURE_BALANCE_SHEET_COLUMN_MAPPING,
    'is_sheet_code' : INFRASTRUCTURE_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : INFRASTRUCTURE_INCOME_STATEMENT_COLUMN_MAPPING,
    'cf_sheet_code' : INFRASTRUCTURE_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : INFRASTRUCTURE_CASH_FLOW_COLUMN_MAPPING
  },
  4 : {
    'bs_sheet_code' : FINANCE_SHARIA_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : FINANCE_SHARIA_BALANCE_SHEET_COLUMN_MAPPING,
    'is_sheet_code' : FINANCE_SHARIA_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : FINANCE_SHARIA_INCOME_STATEMENT_COLUMN_MAPPING,
    'cf_sheet_code' : FINANCE_SHARIA_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : FINANCE_SHARIA_CASH_FLOW_COLUMN_MAPPING
  },
  5 : {
    'bs_sheet_code' : SECURITIES_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : SECURITIES_BALANCE_SHEET_COLUMN_MAPPING,
    'is_sheet_code' : SECURITIES_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : SECURITIES_INCOME_STATEMENT_COLUMN_MAPPING,
    'cf_sheet_code' : SECURITIES_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : SECURITIES_CASH_FLOW_COLUMN_MAPPING
  },
  6 : {
    'bs_sheet_code' : INSURANCE_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : INSURANCE_BALANCE_SHEET_COLUMN_MAPPING,
    'is_sheet_code' : INSURANCE_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : INSURANCE_INCOME_STATEMENT_COLUMN_MAPPING,
    'cf_sheet_code' : INSURANCE_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : INSURANCE_CASH_FLOW_COLUMN_MAPPING
  },
  8 : {
    'bs_sheet_code' : FINANCING_BALANCE_SHEET_SHEET_CODE,
    'bs_column_mapping' : FINANCING_BALANCE_SHEET_COLUMN_MAPPING,
    'is_sheet_code' : FINANCING_INCOME_STATEMENT_SHEET_CODE,
    'is_column_mapping' : FINANCING_INCOME_STATEMENT_COLUMN_MAPPING,
    'cf_sheet_code' : FINANCING_CASH_FLOW_SHEET_CODE,
    'cf_column_mapping' : FINANCING_CASH_FLOW_COLUMN_MAPPING
  },
}