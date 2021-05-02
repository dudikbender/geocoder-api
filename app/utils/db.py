import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import os
from dotenv import find_dotenv, load_dotenv
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

class Database():
    path = Path('/app/data/database.db')

    def engine(self):
        engine = create_engine(f'sqlite://{self.path}')
        return engine

    def query(self, sql_string: str, **kwargs):
        '''Returns a pandas dataframe of table contained in local Sqlite database.
        Uses Pandas read_sql function, and that function's kwargs can be passed.'''
        with self.engine().connect() as conn:
            df = pd.read_sql(sql=sql_string, con=conn, **kwargs)
        return df