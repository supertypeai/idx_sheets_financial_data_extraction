import os
import pandas as pd
import numpy as np
import json

DATA_DIR = os.path.join(os.getcwd(), "data")

if __name__ == "__main__":

  df = pd.read_csv(os.path.join(DATA_DIR, "data_quarter_2023_audit"))