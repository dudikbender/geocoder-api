from fastapi import APIRouter, Depends, HTTPException, status
import pandas as pd
import json
import requests
import os
from passlib.context import CryptContext
from dotenv import find_dotenv, load_dotenv
from app.auth.authorisation import create_password_hash, get_current_user
from datetime import datetime
from app.utils.schema import User
env_loc = find_dotenv('.env')
load_dotenv(env_loc)
users = APIRouter()

api_key = os.environ.get('AIRTABLE_API_KEY')
user_table_url = 'https://api.airtable.com/v0/appe7KAdke2PXikpW/Users'
authorization_header = {'Authorization':f'Bearer {api_key}',
                        'Content-Type': 'application/json'}

def create_user(username: str, password: str, admin:bool = False):
    hashed_password = create_password_hash(password)
    created_date = datetime.now().strftime('%m-%d-%Y')
    payload = {'fields':{'username':username,
                    'hashed_password':hashed_password,
                    'admin':admin,
                    'created_date':created_date,
                    'last_login':created_date}
        }
    response = requests.post(user_table_url, headers=authorization_header, data=json.dumps(payload)).json()
    response_data = response.copy()['fields']
    response_data['id'] = response['id']

    return User(**response_data)

@users.post('/create')
def create_user_in_app(username: str, password: str, admin: bool = False,
                       current_user: User = Depends(get_current_user)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User does not have correct permissions for to create new user.",
        headers={"WWW-Authenticate": "Bearer"})
    if not current_user.admin:
        raise credentials_exception
    hashed_password = create_password_hash(password)
    created_date = datetime.now().strftime('%m-%d-%Y')
    payload = {'fields':{'username':username,
                    'hashed_password':hashed_password,
                    'admin':admin,
                    'created_date':created_date,
                    'last_login':created_date}
        }
    response = requests.post(user_table_url, headers=authorization_header, data=json.dumps(payload)).json()
    response_data = response.copy()['fields']
    response_data['id'] = response['id']

    return User(**response_data)