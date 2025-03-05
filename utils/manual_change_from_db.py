from supabase import create_client
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv
import json

load_dotenv()


if __name__ == "__main__":
  url_supabase = os.getenv("SUPABASE_URL")
  key = os.getenv("SUPABASE_KEY")
  supabase = create_client(url_supabase, key)