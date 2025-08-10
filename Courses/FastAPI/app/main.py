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
def get_posts(id:int ,db:Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """,(str(id)))
    # p=cursor.fetchone()
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    return post

@app.delete("/deletepost/{id}")
def delete_post(id:int ,db:Session = Depends(get_db)):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""",(str(id)))
    # del_post=cursor.fetchone()
    # conn.commit()
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    db.delete(post)
    db.commit()
    return {"deleted":post} 

@app.put("/posts/{id}")
def update_post(id: int, post: post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

   

