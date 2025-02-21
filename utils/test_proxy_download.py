import random
import urllib.request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "https://www.idx.co.id"
PROXY_URL = os.getenv("proxy")
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}


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


def download_excel_file(url: str, filename: str, use_proxy: bool = False):
    try:
        print(f"[DOWNLOAD] Downloading from {url}")

        if not use_proxy:
            # Construct the request
            req = urllib.request.Request(url, headers=create_headers())

            # Open the request and write the response to a file
            response = urllib.request.urlopen(req)
            out_file = open(filename, "wb")

            if (int(response.getcode()) == 200):
                data = response.read()  # Read the response data
                out_file.write(data)  # Write the data to a file
            else:
                print(f"[FAILED] Failed to get data with Status code: {response.getcode()}")

        else:
            response = requests.get(url, allow_redirects=True, proxies=PROXIES, verify=False)
            
            if (int(response.status_code) == 200):
              # Write the response content to a file
              with open(filename, "wb") as out_file:
                  for chunk in response.iter_content(chunk_size=8192):
                      out_file.write(chunk)
            else:
                print(f"[FAILED] Failed to get data with Status code: {response.status_code}")

        return True
    except Exception as e:
        print(f"[FAILED] Failed to download excel file: {e}")
        return False

suffix = "/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan Keuangan Tahun 2023/TW1/ULTJ/FinancialStatement-2023-I-ULTJ.xlsx"

if __name__ == "__main__":
    url = f"{BASE_URL}{suffix}".replace(" ", "%20")
    print(url)
    download_excel_file(
        url,
        "test.xlsx",
        True
    )