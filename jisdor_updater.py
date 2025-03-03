import datetime
import json
import requests
import os

import logging
from imp import reload

def initiate_logging(LOG_FILENAME):
    reload(logging)

    formatLOG = '%(asctime)s - %(levelname)s: %(message)s'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO, format=formatLOG)
    logging.info('[JISDOR START] JISDOR Updater started')

def get_conversion_rate():
    
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    usd_idr_rate = response.json()["rates"]["IDR"]

    dt_now = datetime.datetime.now()
    current_date = dt_now.strftime("%Y-%m-%d")

    return {current_date:  usd_idr_rate}

if __name__ == "__main__":
    LOG_FILENAME = 'scrapper.log'
    JSON_FILENAME = "jisdor.json"

    initiate_logging(LOG_FILENAME)
    f = open(os.path.join(os.getcwd(), JSON_FILENAME), "r")
    data = f.read()
    json_data = json.loads(data)

    conversion_rate = get_conversion_rate()
    json_data.update(conversion_rate)
    logging.info(f"[JISDOR DATA] {conversion_rate}")

    with open(JSON_FILENAME, "w") as outfile:
        outfile.write(json.dumps(json_data, indent=2))

    
    logging.info(f"[JISDOR FINISH] Conversion rate data has been scrapped")