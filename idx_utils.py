import os
import random
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

DATA_IDX_SHEETS_DIR = os.path.join(os.getcwd(), "data_idx_sheets")
DATA_DIR = os.path.join(os.getcwd(), "data")
BASE_URL = "https://www.idx.co.id"
PERIOD_LIST = ["tw1", "tw2", "tw3", "audit"]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
USER_AGENT_ALT_1 = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0"
)
USER_AGENT_ALT_2 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
USER_AGENT_LIST = [USER_AGENT, USER_AGENT_ALT_1, USER_AGENT_ALT_2]

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


# Use randomizer for user-agent to create various header's user agent for each call
def create_headers():
    used_user_agent = random.choice(USER_AGENT_LIST)
    used_headers = HEADERS
    used_headers["User-Agent"] = used_user_agent
    # print(used_headers)
    return used_headers


# Connection to Supabase
_SUPABASE_URL = os.getenv("SUPABASE_URL")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = create_client(_SUPABASE_URL, _SUPABASE_KEY)

# Change period and year to date format
def date_format(period: str, year: str):
    # period value = ['tw1', 'tw2', 'tw3', 'tw4']
    period_map = {"tw1": "-03-31", "tw2": "-06-30", "tw3": "-09-30", "tw4": "-12-31"}
    return f"{str(year)}{period_map[period]}"
