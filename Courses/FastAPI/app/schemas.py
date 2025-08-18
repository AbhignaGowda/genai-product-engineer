from typing import Optional
from pydantic import BaseModel,EmailStr
from datetime import datetime



class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True

class Post(PostCreate):
    id: int
    created_at: datetime

    model_config = {
    "from_attributes": True
}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    

class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {
        "from_attributes": True  
    }

class GetUser(BaseModel):
    id:int
    email:EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id:Optional[str] =None