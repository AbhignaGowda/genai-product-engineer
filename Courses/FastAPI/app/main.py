from http.client import HTTPException
from importlib.resources import contents
from pyexpat import model
from fastapi import FastAPI ,Response , status,HTTPException,Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from  psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine ,get_db


models.Base.metadata.create_all(bind=engine) 

app = FastAPI()



class post(BaseModel):
    title: str
    content: str
    published:bool = True

while True:
    try:
       conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='password',cursor_factory=RealDictCursor)
       cursor=conn.cursor()
       print("database connection was successfull")
       break

    except Exception as error:
       print("connecting to datbase faild ",error)
       time.sleep(2)





@app.get("/")
def root():
    return {"message": "bingoo"}


@app.get("/posts")
def get_posts(db:Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts """)
    # posts=cursor.fetchall()
    posts=db.query(models.Post).all()
    return {"data":posts}

@app.post("/posts",status_code= status.HTTP_201_CREATED)
def post_pic(post: post,db:Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts(title,content,published) VALUES (%s,%s,%s) RETURNING *""",
    # (post.title,post.content,post.published)) 
    # new_post = cursor.fetchone() 
    # conn.commit()

    new_post= models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data":new_post}

@app.get("/posts/{id}")
def get_posts(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """,(str(id)))
    p=cursor.fetchone()
    return{"data_detail" : f"here is post of id  {p}"}

@app.delete("/deletepost/{id}")
def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""",(str(id)))
    del_post=cursor.fetchone()

    conn.commit()
    return {"data":f"post   {del_post} was deleted"}

@app.put("/posts/{id}")
def update_post(id: int,post:post):
    cursor.execute(""" UPDATE posts SET title = %s , content = %s , published = %s WHERE id = %s RETURNING *""",(post.title,post.content,post.published,str(id)))
    up_post=cursor.fetchone()
    print(up_post)
    conn.commit()
    
    if up_post ==None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id :{id} was not found")
                
    return {"data":f"post   {up_post} was updated"}

   

