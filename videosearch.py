import sqlite3
import os
import pandas as pd


# Use this filename for the database
DF_LIST = ['Animee', 'DailyLife', 'Dance', 'Domestic', 'Entertainment',
           'Fashion', 'Games', 'Kichiku', 'Movies', 'Music', 'Science' ]
CONN = sqlite3.connect('BLData.db')
for cat in DF_LIST:

    cat_df = pd.read_csv('Data/BLData{}.txt'.format(cat), sep = '|', header = 0)

    cat_df.to_sql(name = cat, con = CONN, flavor = 'sqlite')

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'BLData.db')

