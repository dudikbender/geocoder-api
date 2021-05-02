from fastapi import APIRouter
from .geocoding import get_isoline_from_address, geoapify_key

models = APIRouter()

@models.get('/isoline')
async def isoline(address: str = 'Finsbury Park, London', mode: str = 'drive', traveltime_minutes: int = 20):
    response = get_isoline_from_address(api_key=geoapify_key,address=address, country='gb', crs=4326, 
                                        mode=mode, traveltime_seconds=traveltime_minutes * 60)
    return response