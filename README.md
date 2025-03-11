# Table of Contents
- [How To Run](#how-to-run)
- [File Description](#file-description)
- [Folder Description](#folder-description)
- [Generated URL](#generated-url)

# How to Run
There are two ways to run the main program:
1. Automatic start
```py
# Command: 
python main.py {BATCH}

# Example:
python main.py 1
python main.py all
```

Description:
Automatically scrape and extract based on current time
Interval (3*30 + 7) for Annual
Interval (30 + 7) for Quarter

if it runs in:
  - Month 3: get annual and Q4 of last year
  - Month 5: get Q1 of current year
  - Month 8: get Q2 of current year
  - Month 11: get Q3 of current year

BATCH =[1, 2, 3, 4, all]
  - 1 => First quarter of the data in database
  - 2 => Second quarter of the data in database
  - 3 => Third quarter of the data in database
  - 4 => Last quarter of the data in database
  - all => scrape for all in the database

2. For manual start:

```py
# Command: 
python main.py {BATCH} {YEAR} {PERIOD}

# Example:
python main.py 1 2024 tw1 #Scrape and extract Q1 of 2024 for batch 1
```

Description:
program requires two parameters: {year} and {PERIOD}

- YEAR => year to be scrapped
- PERIOD => see PERIOD_LIST in idx_utils.py
- BATCH = [1, 2, 3, 4, all]
  - 1 => First quarter
  - 2 => Second quarter
  - 3 => Third quarter
  - 4 => Last quarter
  - all => scrape for all in the database

# File Description
### IDX
1. `idx_mapping_constant.py`

    Consists of constants and mapping dictionary to map the needed metrics and the one exist in the financial sheets excel file.

2. `idx_process.py`

    Consists of the core functions and algorithms starting from download to process and extract information from the excel files.

3. `idx_scrape_url.py`

    Consists of function to generate URL to IDX's API to download the excel files.

4. `idx_utils.py`

    Consists of utilities and supporting functions.

5. `main.py`

    The main program for the whole process

### JISDOR
1. `jisdor_updater.py`

    The program used to update USD to IDR rate on certain date. The result is stored in `jisdor.json`

2. `jisdor.json`

    The result of stored USD to IDR rate from `jisdor_updater.py`.

# Folder Description

1. `data`
    
    Consist of the extraction and result data in .csv

2. `data_idx_sheets`

    Consist of downloaded excel file from IDX's API. The files in this folder are the one to be processed in `idx_process.py`

3. `data_temp`

    Consist of manual data store (for development only). All the programs inside this folder are not used while the pipeline is running and should not be affecting the running pipeline.

4. `utils`

    Consist of function that are run manually (for development only). All the programs inside this folder are not used while the pipeline is running and should not be affecting the running pipeline.


# Generated URL
This is the generated URL that is used to download excel file from IDX's API. Can be used for manual check

```sh
# Format
https://www.idx.co.id/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan Keuangan Tahun {year}/{formatted_period}/{symbol}/FinancialStatement-{year}-{file_period}-{symbol}.xlsx
```

Description
- {year} : financial year to get
- {formatted_period}: use this list [tw1, tw2, tw3, audit] for Q1, Q2, Q3, and Q4/Annual
- {symbol} : ticker symbol of the company
- {file_period} : use this list [I, II, III, Tahunan] for Q1, Q2, Q3, and Q4/Annual

```sh
# Example, BBCA 2024 Q2
https://www.idx.co.id/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan Keuangan Tahun 2024/tw2/BBCA/FinancialStatement-2024-II-BBCA.xlsx

# Example, TLKM 2023 Q4/Annual
https://www.idx.co.id/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan Keuangan Tahun 2023/audit/TLKM/FinancialStatement-2023-Tahunan-TLKM.xlsx
```

Notes: 
- There is a possibility that the file itself is not available in the IDX, resulting `404 page`