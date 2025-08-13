from .. import models ,schemas,utils
from ..database import engine ,get_db
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from http.client import HTTPException
from sqlalchemy.orm import Session
from typing import List

router= APIRouter(
        prefix="/posts",
        tags=["Posts"]

)
  


@router.get("/",response_model=List[schemas.Post])
def get_posts(db:Session = Depends(get_db)):
    posts=db.query(models.Post).all()
    return posts

@router.post("/",status_code= status.HTTP_201_CREATED,response_model=schemas.Post)
def post_pic(post: schemas.PostCreate,db:Session = Depends(get_db)):
    new_post= models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}")
def get_posts(id:int ,db:Session = Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    return post

@router.delete("/{id}")
def delete_post(id:int ,db:Session = Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    db.delete(post)
    db.commit()
    return post 

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
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
