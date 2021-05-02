import pandas as pd
import numpy
import os
import geopandas as gpd
import requests
from requests.structures import CaseInsensitiveDict
from geojson import Feature, Point, FeatureCollection
from dotenv import find_dotenv, load_dotenv

env_loc = find_dotenv('.env')
load_dotenv(env_loc)

# Credentials
geoapify_key = os.environ.get('GEOAPIFY_KEY')

def geocode_address(api_key: str, address_text: str = 'Finsbury Park Station', country: str = 'uk'):
    url = f'https://api.geoapify.com/v1/geocode/search?text={address_text}&apiKey={api_key}&filter=countrycode:{country}'
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    response = requests.get(url, headers=headers)
    return response.json()

def geojson_to_geodataframe(geojson: dict, crs: int = 4326):
    collection = FeatureCollection(geojson)
    gdf = gpd.GeoDataFrame.from_features(collection['features']).set_crs(epsg=crs)
    return gdf

def address_to_geodataframe(api_key: str, address_text: str = 'Finsbury Park Station', country: str = 'gb', 
                            crs: int = 4326):
    geojson = geocode_address(address_text=address_text, country=country, api_key=api_key)
    gdf = geojson_to_geodataframe(geojson, crs=crs)
    return gdf

def get_isoline(api_key: str, lat: float, lon: float, type: str = 'time', mode: str = 'walk', range: int = 1000):
    url = f'https://api.geoapify.com/v1/isoline?lat={lat}&lon={lon}&type={type}&mode={mode}&range={range}&apiKey={api_key}'
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    response = requests.get(url, headers=headers)
    return response.json()

def get_isoline_from_address(address: str, api_key: str = geoapify_key, country: str = 'gb', crs: int = 4326, 
                             mode: str = 'drive', traveltime_seconds: int = 1800):
    gdf = address_to_geodataframe(address_text=address, country=country, crs=crs, api_key=api_key).iloc[0]
    lat, lon = gdf['lat'], gdf['lon']
    isoline = get_isoline(api_key=api_key, lat=lat, lon=lon, mode=mode, range=traveltime_seconds)
    return isoline

# Address geocoded
# Get isoline
# Get isoline wards + populations
# get isoline property summary