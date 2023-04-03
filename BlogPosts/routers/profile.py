from fastapi import APIRouter,Depends,status,UploadFile,File
from  BlogPosts.schemas import ShowProfile,UserProfile
from typing import List
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.routers import verify_token
from BlogPosts.repository import profile
from BlogPosts.models import User,ProfileImage
import shutil
from werkzeug.utils import secure_filename




router = APIRouter(
    tags=["Users Profile"],
    prefix = "/profile"
)

@router.get('/get_all',response_model=List[ShowProfile], status_code = status.HTTP_200_OK,summary="Get All Users profile")
def get_all_profile(db:Session = Depends(get_db)):
    return profile.get_all_profile(db)

@router.get('/{id}',response_model=ShowProfile, status_code = status.HTTP_200_OK,summary="Get Profile by Id")
def show_profile(id,db:Session = Depends(get_db)):
    return profile.show_profile(id,db)

@router.post('/create',response_model=ShowProfile, status_code = status.HTTP_201_CREATED,summary="Create User Profile")
def create_profile(request:UserProfile,db:Session = Depends(get_db)):
    return profile.create_profile(request,db)

@router.put('/update/{id}',response_model=ShowProfile, status_code = status.HTTP_202_ACCEPTED,summary="Update User Profile")
def update_profile(id,request:UserProfile,db:Session = Depends(get_db)):
    return profile.update_profile(id,request,db)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete User Profile")
def delete_profile(id,db:Session = Depends(get_db)):
    return profile.delete_profile(id,db)

@router.post("/upload",summary="Upload your Profile picture")
def upload(profile_id:int,db:Session = Depends(get_db),file:UploadFile = File(...)):
    with open(f"BlogPosts/static/profileimages/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    name = secure_filename(file.filename)
    mimetype = file.content_type

    image_upload = ProfileImage(img = file.file.read(),minetype=mimetype, name=name,profile_id=profile_id)
    db.add(image_upload)
    db.commit()
    return f"{name} has been Successfully Uploaded"