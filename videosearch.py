import sqlite3
import os
import pandas as pd


# Use this filename for the database
animee_df = pd.read_csv('Data/BLDataAnimee.txt', sep = '|', header = 0)
conn = sqlite3.connect('animee.db')
pd.animee_df.to_sql(name = 'animee_info.sqlite3', flavor = 'sqlite')

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'animee_info.sqlite3')

