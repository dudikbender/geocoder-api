from fastapi import FastAPI, Depends
import os
from dotenv import find_dotenv, load_dotenv
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

from app.models.models import get_isoline_from_address
from app.models import models
from app.auth import app_auth, get_current_user
from app.users import users

api_key = os.environ.get('GEOAPIFY_KEY')

app = FastAPI(title='Geocoder API',
              description='API for advanced geocoding results, from UK addresses',
              version=0.1,
              docs_url='/docs',
              redoc_url='/redocs')

app.include_router(
    app_auth,
    prefix='/auth',
    tags=['Authorisation']
)

app.include_router(
    models,
    prefix='/models',
    tags=['Models'],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    users,
    prefix='/users',
    tags=['Users'],
    dependencies=[Depends(get_current_user)]
)