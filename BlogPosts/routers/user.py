from fastapi import APIRouter,Depends,status,UploadFile,File
from  BlogPosts.schemas import ShowUser,CreateUser
from typing import List
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.routers import verify_token
from BlogPosts.repository import user
import shutil

router = APIRouter(
    tags=["Users Information"],
    prefix = "/users"
)

@router.post('/create',response_model=CreateUser, status_code = status.HTTP_201_CREATED,summary="Create User Account")
def create_user(request:CreateUser,db:Session = Depends(get_db)):
    return user.create_user(request,db)

@router.get('/get_all',response_model=List[ShowUser], status_code = status.HTTP_200_OK,summary="Get All Users")
def get_all_user(db:Session = Depends(get_db)):
    return user.get_all_user(db)

@router.get('/{id}',response_model=ShowUser, status_code = status.HTTP_200_OK,summary="Get User by Id")
def get_user(id,db:Session = Depends(get_db)):
    return user.get_user(id,db)

@router.get('/{username}',response_model=ShowUser, status_code = status.HTTP_200_OK,summary="Get User by Username")
def get_username(username:str,db:Session = Depends(get_db)):
    return user.get_username(username,db)

@router.post("/upload",summary="Upload your profile picture")
def upload(file:UploadFile = File(...)):
    with open(f"BlogPosts/static/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"{file.filename} has been Successfully Uploaded"