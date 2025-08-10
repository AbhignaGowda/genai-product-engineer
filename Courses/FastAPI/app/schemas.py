from pydantic import BaseModel
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

