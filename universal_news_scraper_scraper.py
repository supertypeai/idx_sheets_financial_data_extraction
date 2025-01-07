from urllib.request import urlopen
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import time
import logging
import urllib
import os
import json
from datetime import datetime
import ssl

# Set the logging level for the 'websockets' logger
logging.getLogger('websockets').setLevel(logging.WARNING)
# If you need to configure logging for requests-html as well
logging.getLogger('requests_html').setLevel(logging.WARNING)


USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36'
HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        'x-test': 'true',
    }
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S' # Example: 2024-08-12 21:41:32

def save_to_json(data: list, filename: str):
  final_filename = os.path.join(os.getcwd(), "data", filename)
  with open(final_filename, "w") as final:
    json.dump(data, final, indent=2)
      

def convert_datetime_to_datestring(datetime_input: str, datetime_input_format: str):
  date_object = datetime.strptime(datetime_input, datetime_input_format)
  return date_object.strftime(TIMESTAMP_FORMAT)

def is_string_number(num_string: str):
  for num in num_string:
    try:
      int(num)
    except:
      return False
  return True

def sanitize_title(title:str):
  return title.replace("\n", "").strip()

def fetch_url(url : str):
  try: 
    print(f"[PROGRESS] Fetching data from {url}")
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req)
    status_code = resp.getcode()
    if (status_code == 200):
      data = resp.read()
      soup = BeautifulSoup(data, "html.parser")
      return soup
    else:
      print(f"[FAILED] Failed to fetch {url}. Get status code : {status_code}")
      return None
  except Exception as e:
    print(f"[FAILED] Error to fetch {url}: {e}")
    return None
  
def fetch_url_api(url : str):
  try: 
    print(f"[PROGRESS] Fetching data from {url}")
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req)
    status_code = resp.getcode()
    if (status_code == 200):
      data = resp.read()
      json_data = json.loads(data)
      return json_data
    else:
      print(f"[FAILED] Failed to fetch {url}. Get status code : {status_code}")
      return None
  except Exception as e:
    print(f"[FAILED] Error to fetch {url}: {e}")
    return None
  
def fetch_url_session(url : str) -> BeautifulSoup | None:
  try:
    session = HTMLSession()
    response = session.get(url)
    response.html.render(sleep=1, timeout=5)
    soup = BeautifulSoup(response.html.html, "html.parser")

    print(f"[SESSION] Session for {url} is opened")
    return soup
  except Exception as e:
    print(f"[FAILED] Failed to scrape {url}: {e}")
    return None
  finally:
    session.close()
    print(f"[SESSION] Session for {url} is closed")

def fetch_url_proxy(url: str):
    try:
        # Set up SSL context to ignore SSL certificate errors
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Set up proxy support
        proxy = os.environ.get("PROXY")
        if proxy:
            proxy_support = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
        
        # Fetch the URL content
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request) as response:
            status_code = response.getcode()
            print(f"Response status code: {status_code} for {url}")
            
            if status_code == 200:
                data = response.read()
                soup = BeautifulSoup(data, "html.parser")
                return soup
  
            else:
                print(f"Failed to open {url}: Status code {status_code}")
                return None
    except Exception as e:
        print(f"Failed to open {url}: {e}")
        return None



def handle_idn_financials(dict_key: str, dict_url : str) -> list:
  try:
    article_url_list = list()
    LIMIT_PAGE_IDX = 5
    for idx in range(1, LIMIT_PAGE_IDX+1):
        url = dict_url.replace("PAGE_IDX", str(idx))
        soup = fetch_url(url)

        if (soup is not None):
          # Search news_container to eliminate unnecessary href
          news_container = soup.find("div", {"class": "news"})
          href_elms = news_container.findAll("a")
          for elm in href_elms:
            article_url = elm['href']
            url_prefix = "https://www.idnfinancials.com/news/"

            # Check if it is an article url
            # Article url : https://www.idnfinancials.com/news/XXXXX/ => XXXXX is a number. List url if XXXXX == "page"
            if (url_prefix in article_url):
              temp_url = article_url.replace("url_prefix", "")
              if (temp_url.split("/")[0] != "page" and article_url not in article_url_list):
                # Only insert to list if it is valid and not yet inserted (to handle duplicate)
                article_url_list.append(article_url)
        else:
          print(f"[FAILED] None type for Beautiful Soup {url}")
    
    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")
    # Iterate each page
    result_list = list()
    for article_url in article_url_list:
      soup = fetch_url(article_url)
      if (soup is not None):
        try:
          date = soup.find("div", {"class" : "date-published"})['content']
          title = soup.find("h2", {"class" : "title"}).text
          data_dict = {
            "url" : article_url,
            "timestamp" : date,
            "title" : sanitize_title(title)
          }
          result_list.append(data_dict)
        except Exception as e:
          print(f"[FAILED] Failed to get the data from {article_url}: {e}")
      else:
        print(f"[FAILED] None type for Beautiful Soup {article_url}")
      time.sleep(0.5)

    save_to_json(result_list, f"news_{dict_key.lower()}.json")
    print(f"[SUCCESS] Scrapped data for {dict_key} has been saved!")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")




def handle_cnbc(dict_key: str, dict_url : str):
  try:
    article_url_list = list()
    soup = fetch_url(dict_url)

    if (soup is not None):
      # Search for containers to eliminate unnecessary href
      featured_news_container = soup.find("div", {"class": "FeaturedNewsHero-container"})
      href_elms = featured_news_container.findAll("a")
      for elm in href_elms:
        if (elm['href'] not in article_url_list):
          article_url_list.append(elm['href'])

      sidebar_news_container = soup.find("div", {"class": "SidebarArticle-sidebar"})
      href_elms = sidebar_news_container.findAll("a")
      for elm in href_elms:
        if (elm['href'] not in article_url_list):
          article_url_list.append(elm['href'])

      homepage_news_container = soup.find("div", {"class": "RiverPlus-riverPlusContainer"})
      href_elms = homepage_news_container.findAll("a")
      for elm in href_elms:
        if (elm['href'] not in article_url_list):
          article_url_list.append(elm['href'])

      market_news_container = soup.find("section", {"class": "MarketsModule-rightColumn"})
      href_elms = market_news_container.findAll("a")
      for elm in href_elms:
        if (elm['href'] not in article_url_list):
          article_url_list.append(elm['href'])
    else:
      print(f"[FAILED] None type for Beautiful Soup {dict_url}")
    
    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")
    # Iterate each page
    result_list = list()
    for article_url in article_url_list:
      soup = fetch_url(article_url)
      if (soup is not None):
        try:
          date_elm = soup.find("time", {"data-testid" : "published-timestamp"})
          title_elm = soup.find("h1", {"class" : "ArticleHeader-headline"})
          # Adjust date
          date = convert_datetime_to_datestring(date_elm['datetime'], "%Y-%m-%dT%H:%M:%S%z")
          title = title_elm.text
          data_dict = {
            "url" : article_url,
            "timestamp" : date,
            "title" : sanitize_title(title)
          }
          result_list.append(data_dict)
        except Exception as e:
          print(f"[FAILED] Failed to get the data from {article_url}: {e}")
      else:
        print(f"[FAILED] None type for Beautiful Soup {article_url}")
      time.sleep(0.5)

    save_to_json(result_list, f"news_{dict_key.lower()}.json")
    print(f"[SUCCESS] Scrapped data for {dict_key} has been saved!")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")





def handle_yahoo_finance(dict_key: str, dict_url : str):
  try:
    article_url_list = list()
    soup = fetch_url(dict_url)

    if (soup is not None):
      # Search for containers to eliminate unnecessary href
      main_container = soup.find("section", {"class": "main"})
      href_elms = main_container.findAll("a")
      for elm in href_elms:
        article_url = elm['href']
        if ("https://finance.yahoo.com/news/" in article_url and article_url not in article_url_list):
          article_url_list.append(article_url)
    else:
      print(f"[FAILED] None type for Beautiful Soup {dict_url}")

    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")

    # Iterate each page
    result_list = list()
    for article_url in article_url_list:
      soup = fetch_url(article_url)
      if (soup is not None):
        try:
          date_elm = soup.find("time")
          # Adjust date
          date = convert_datetime_to_datestring(date_elm['datetime'], "%Y-%m-%dT%H:%M:%S.000Z")
          title_elm = soup.find("h1", {"id" : "caas-lead-header-undefined"})
          title = title_elm.text
          data_dict = {
            "url" : article_url,
            "timestamp" : date,
            "title" : sanitize_title(title)
          }
          result_list.append(data_dict)
        except Exception as e:
          print(f"[FAILED] Failed to get the data from {article_url}: {e}")
      else:
        print(f"[FAILED] None type for Beautiful Soup {article_url}")
      time.sleep(0.5)

    save_to_json(result_list, f"news_{dict_key.lower()}.json")
    print(f"[SUCCESS] Scrapped data for {dict_key} has been saved!")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")





def handle_idx(dict_key: str, dict_url : str):
  try:
    result_list = list()
    LIMIT_PAGE_IDX = 5
    for idx in range(1, LIMIT_PAGE_IDX+1):
      url = dict_url.replace("PAGE_IDX", str(idx))
      json_data = fetch_url_api(url)
      if (json_data is not None):
        data_items = json_data['Items']
        for item in data_items:
          url_prefix = "https://www.idx.co.id/en/news/news/"
          item_id = item['ItemId']
          item_date = item['PublishedDate']
          title = item['Title']
          # Adjust date
          date = convert_datetime_to_datestring(item_date, "%Y-%m-%dT%H:%M:%S")
          data_dict = {
            "url" : f"{url_prefix}{item_id}",
            "timestamp" : date,
            "title" : sanitize_title(title)
          }
          result_list.append(data_dict)
      else:
        print(f"[FAILED] None type for JSON data {url}")
      time.sleep(0.5)

    save_to_json(result_list, f"news_{dict_key.lower()}.json")
    print(f"[SUCCESS] Scrapped data for {dict_key} has been saved!")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")



def handle_cnn_edition(dict_key: str, dict_url : str):
  try:
    article_url_list = list()
    soup = fetch_url(dict_url)

    if (soup is not None):
      # Search for containers to eliminate unnecessary href
      main_container = soup.find("section", {"class": "layout__main"})
      href_elms = main_container.findAll("a")
      for elm in href_elms:
        article_url = elm['href']
        url_prefix = "https://edition.cnn.com"
        candidate_article_url = f"{url_prefix}{article_url}"
        # Check if it is an article url
        # Article url : https://www.idnfinancials.com/news/YYYY/MM/DD/... => YYYY/MM/DD is a date. 
        article_url_components = article_url.split("/")
        if (is_string_number(article_url_components[1]) and is_string_number(article_url_components[2]) and is_string_number(article_url_components[3]) and candidate_article_url not in article_url_list):
          article_url_list.append(candidate_article_url)
    else:
      print(f"[FAILED] None type for Beautiful Soup {dict_url}")
    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")


    # Iterate each page
    result_list = list()
    for article_url in article_url_list:
      soup = fetch_url(article_url)
      if (soup is not None):
        try:
          # Adjust date
          date_elm = soup.find("div", {"class" : "timestamp"})
          date_string = date_elm.text.replace(",", "").replace("\n", "").replace("Updated", "").strip()
          date_components = date_string.split(" ")
          hour_min = date_components[0]
          am_pm = date_components[1]
          month = date_components[-3]
          day = date_components[-2]
          year = date_components[-1]
          new_date_string = f"{hour_min} {am_pm} {month} {day} {year}"
          date = convert_datetime_to_datestring(new_date_string, "%I:%M %p %B %d %Y")

          title_elm = soup.find("h1", {"id" : "maincontent"})
          title = title_elm.text
          data_dict = {
            "url" : article_url,
            "timestamp" : date,
            "title" : sanitize_title(title)
          }
          result_list.append(data_dict)
        except Exception as e:
          print(f"[FAILED] Failed to get the data from {article_url}: {e}")
      else:
        print(f"[FAILED] None type for Beautiful Soup {article_url}")
      time.sleep(0.5)

    save_to_json(result_list, f"news_{dict_key.lower()}.json")
    print(f"[SUCCESS] Scrapped data for {dict_key} has been saved!")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")




MONTH_ABBREVIATION_ADJUSMENT = {
  "MEI" : "May",
  "AGU" : "Aug",
  "OKT" : "Oct",
  "DES" : "Dec"
}

def handle_finance_detik(dict_key: str, dict_url : str):
  try:
    result_list = list()
    LIMIT_PAGE_IDX = 5
    for idx in range(1, LIMIT_PAGE_IDX+1):
      url = dict_url.replace("PAGE_IDX", str(idx))
      soup = fetch_url(url)

      if (soup is not None):
        # Search news_container to eliminate unnecessary href
        news_container = soup.find("div", {"class": "list-content"})
        news_cards = news_container.findAll("div" , {"class": "media"})
        
        for card in news_cards:
          article_url = card.find("a")['href']
          title_elm = card.find("h3", {"class" : "media__title"})
          date_elm = card.find("div", {"class" : "media__date"}).find("span")
          title = title_elm.text
          date_string = date_elm['title']
          
          # Adjust Date
          date_components : list = date_string.split(" ")
          day : str = date_components[1]
          month : str = date_components[2]
          year : str = date_components[3]
          hour_min : str = date_components[4]
          # Abbreviation Adjustment
          if (month.upper() in MONTH_ABBREVIATION_ADJUSMENT):
            month = MONTH_ABBREVIATION_ADJUSMENT[month.upper()]
          new_date_string : str= f"{hour_min} {month} {day} {year}"
          date = convert_datetime_to_datestring(new_date_string, "%H:%M %b %d %Y")

          data_dict = {
            "url" : article_url,
            "timestamp" : date,
            "title" : sanitize_title(title)
          }
          result_list.append(data_dict)

      else:
        print(f"[FAILED] None type for Beautiful Soup {url}")
    
      time.sleep(0.5)

    save_to_json(result_list, f"news_{dict_key.lower()}.json")
    print(f"[SUCCESS] Scrapped data for {dict_key} has been saved!")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")



MONTH_ID_TO_EN = {
    "Januari": "January",
    "Februari": "February",
    "Maret": "March",
    "April": "April",
    "Mei": "May",
    "Juni": "June",
    "Juli": "July",
    "Agustus": "August",
    "September": "September",
    "Oktober": "October",
    "November": "November",
    "Desember": "December"
}

def handle_ekonomi_bisnis(dict_key: str, dict_url : str):
  try:
    article_url_list = list()
    soup = fetch_url(dict_url)

    if (soup is not None):
      # Search for containers to eliminate unnecessary href
      main_container = soup.find("main", {"class": "main"})
      href_elms = main_container.findAll("a")
      for elm in href_elms:
        article_url = elm['href']
        article_prefix = "https://ekonomi.bisnis.com/"

        # # Check if it is an article url
        if (article_prefix in article_url and article_url not in article_url_list):
          article_url_list.append(article_url)
    else:
      print(f"[FAILED] None type for Beautiful Soup {dict_url}")
    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")


    # Iterate each page
    result_list = list()
    for article_url in article_url_list:
      soup = fetch_url(article_url)
      if (soup is not None):
        try:
          # Adjust date
          date_elm = soup.find("div", {"class" : "detailsAttributeDates"})
          date_string = date_elm.text.replace(",", "").replace("\n", "").strip()
          date_components = date_string.split(" ")
          hour_min = date_components[-1]
          month = MONTH_ID_TO_EN[date_components[2]] # Assuming it will always True
          day = date_components[1]
          year = date_components[3]
          new_date_string = f"{hour_min} {month} {day} {year}"
          date = convert_datetime_to_datestring(new_date_string, "%H:%M %B %d %Y")

          title_elm = soup.find("h1", {"class" : "detailsTitleCaption"})
          title = title_elm.text
          data_dict = {
            "url" : article_url,
            "timestamp" : date,
            "title" : sanitize_title(title)
          }
          result_list.append(data_dict)
        except Exception as e:
          print(f"[FAILED] Failed to get the data from {article_url}: {e}")
      else:
        print(f"[FAILED] None type for Beautiful Soup {article_url}")
      time.sleep(0.5)

    save_to_json(result_list, f"news_{dict_key.lower()}.json")
    print(f"[SUCCESS] Scrapped data for {dict_key} has been saved!")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")







def handle_market_watch(dict_key: str, dict_url : str):
  # Need Proxy
  # 401 Forbidden
  try:
    article_url_list = list()
    soup = fetch_url_proxy(dict_url)

    if (soup is not None):
      # Search for containers to eliminate unnecessary href
      main_container = soup.find("section", {"class": "region"})
      href_elms = main_container.findAll("a")
      for elm in href_elms:
        article_url = elm['href']
        print(article_url)

    else:
      print(f"[FAILED] None type for Beautiful Soup {dict_url}")

    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")





def handle_reuters(dict_key: str, dict_url : str):
  # Need Proxy
  # 401 Forbidden
  try:
    article_url_list = list()
    soup = fetch_url_proxy(dict_url)

    if (soup is not None):
      # Search for containers to eliminate unnecessary href
      main_container = soup.find("section", {"class": "region"})
      href_elms = main_container.findAll("a")
      for elm in href_elms:
        article_url = elm['href']
        print(article_url)

    else:
      print(f"[FAILED] None type for Beautiful Soup {dict_url}")

    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")



def handle_bloomberg(dict_key: str, dict_url : str):
  # Have tried but cannot be scrapped
  # Maybe need proxy
  # 401 Forbidden
  try:
    article_url_list = list()
    soup = fetch_url_session(dict_url)
    print(soup)
    if (soup is not None):
      # Search for containers to eliminate unnecessary href
      main_container = soup.find("section", {"class": "region"})
      href_elms = main_container.findAll("a")
      for elm in href_elms:
        article_url = elm['href']
        print(article_url)

    else:
      print(f"[FAILED] None type for Beautiful Soup {dict_url}")

    print(f"[PROGRESS] Got {len(article_url_list)} articles from {dict_key}")

  except Exception as e:
    print(f"[FAILED] Error in handling data: {e}")
