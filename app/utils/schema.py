from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Authorisation response models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User response models
class User(BaseModel):
    id: str
    username: str
    admin: Optional[bool] = None

class UserInDB(User):
    hashed_password: str