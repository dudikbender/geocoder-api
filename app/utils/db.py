import os
from dotenv import find_dotenv, load_dotenv
import requests
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

def get_airtable_table(table_name: str):
    url = f'https://api.airtable.com/v0/appe7KAdke2PXikpW/{table_name}'
    