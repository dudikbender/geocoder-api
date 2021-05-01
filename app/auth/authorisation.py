from fastapi import Depends, APIRouter, HTTPException, Security, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from dotenv import find_dotenv, load_dotenv
import pandas as pd
from pandas import json_normalize
import json
import requests
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.utils.schema import Token, TokenData, User, UserInDB
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

api_key = os.environ.get('AIRTABLE_API_KEY')
app_auth = APIRouter()

# Define the auth scheme and access token URL
# token_schema = HTTPBearer(scheme_name='Authorization Bearer Token') For API TOKEN option
auth_security = HTTPBasic()
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Settings for encryption
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))

def create_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)

def get_all_users():
    url = f'https://api.airtable.com/v0/appe7KAdke2PXikpW/Users'
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers).json()
    user_list = []
    for record in response['records']:
        fields = record['fields']
        fields['id'] = record['id']
        user_list.append(fields)
    df = json_normalize(user_list)
    return df

def get_user(username: str):
    user_df = get_all_users()
    user = user_df[user_df.username == username]
    if len(user) == 0:
        print('Username either does not exist or is misspelled.')
        return False
    else:
        user_data = json.loads(user.to_json(orient='records'))[0]
        return UserInDB(**user_data)

def authenticate_user(username, password):
    # First, retrieve the user by the email provided
    user = get_user(username)
    if not user:
        return False
    # If present, verify password against password hash in database
    password_hash = user.hashed_password
    if not verify_password(password, password_hash):
        return False
    return user

# Deprecated token authorization flow - keeping for reference
'''@app_auth.post('/')
async def login(token: HTTPAuthorizationCredentials = Security(api_key_schema)):
    if token.dict()['credentials'] != app_key:
        raise HTTPException(status_code=401, detail='Api key is not correct.')
    else:
        return token.dict()['credentials']'''

# Create access token, required for OAuth2 flow
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2 Scheme - Decrypt the token and retrieve the username from payload
'''async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user'''

# HTTP Basic scheme
async def get_current_user(credentials: str = Depends(auth_security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = credentials.username
        password = credentials.password
        user = authenticate_user(username, password)
        if username is None:
            raise credentials_exception
    except:
        raise credentials_exception
    return user

# Endpoint for token authorisation
@app_auth.post("/token")
async def login_for_access_token(form_data: HTTPBasicCredentials = Depends(auth_security)):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}