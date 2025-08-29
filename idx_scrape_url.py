from dotenv import load_dotenv
import warnings

load_dotenv()

warnings.simplefilter(action="ignore", category=UserWarning)

_FILE_PERIOD_MAP = {
    "tw1": "I",
    "tw2": "II",
    "tw3": "III",
    "audit": "Tahunan"
}

def generate_url(symbol: str, year: int, period: str):
    symbol = symbol.replace(".JK", "")
    formatted_period = period  # Keep original format (tw1, tw2, tw3, audit)
    file_period = _FILE_PERIOD_MAP[period]
    return f"/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan Keuangan Tahun {year}/{formatted_period}/{symbol}/FinancialStatement-{year}-{file_period}-{symbol}.xlsx"

def generate_filename(symbol: str, year: int, period: str):
    symbol = symbol.replace(".JK", "")
    file_period = _FILE_PERIOD_MAP[period]
    return f"FinancialStatement-{year}-{file_period}-{symbol}.xlsx"
