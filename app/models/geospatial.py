import geopandas as gpd
import pandas as pd
from airtable import Airtable
import os
from dotenv import find_dotenv, load_dotenv
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

from ..utils import Database

db = Database()
ward_query = '''
                select ward_code, ward_name, total_population, mean_age
                from population_2019
             '''
wards_pop_df = db.query(ward_query)