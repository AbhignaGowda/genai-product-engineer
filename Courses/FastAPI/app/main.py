from http.client import HTTPException
from fastapi import FastAPI ,Response , status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class post(BaseModel):
    title: str
    content: str
    published:bool = True
    rating: Optional[int] = None



my_posts=[{"title": "title of post 1","content":"content of post 1","id":1},{"title": "title of post 2","content":"i also like pizza","id":2}]

def find_post(id):
    for p in my_posts:
        if p['id']==id:
            return p
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] ==id:
            return i

def update(id):
    for i, p in enumerate(my_posts):
        if p['id'] ==id:
            return i

@app.get("/")
def root():
    return {"message": "bingoo"}

@app.get("/posts")
def get_posts():
    return {"data":my_posts}

@app.post("/posts",status_code= status.HTTP_201_CREATED)
def post_pic(post: post):
    post_dict=post.dict()
    post_dict['id']=randrange(0,100000)
    my_posts.append(post_dict)
    return {"successfull":post_dict }
#title str , content str, category, Bool 
@app.get("/posts/{id}")
def get_posts(id: int, response: Response):
    ypost=find_post(id)
    if not ypost:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id :{id} was not found")
    
    return{"data_detail" : f"here is post of id  {ypost}"}
@app.delete("/deletepost/{id}")
def delete_post(id: int):
    index=find_index_post(id)

    if index ==None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id :{id} was not found")

    my_posts.pop(index)    
    return Response(status_code= status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int,post:post):
    index= find_index_post(id)
    if index ==None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id :{id} was not found")

   
    post_dict=post.dict()
    post_dict['id']=id
    my_posts[index]=post_dict
    return {"data":post_dict}

