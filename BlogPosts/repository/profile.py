from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from BlogPosts.models import Profile
from BlogPosts.schemas import UserProfile,ShowProfile
from typing import List
from BlogPosts.security.get_current_user import get_current_user 

current_user = get_current_user

def get_all_profile(db:Session):
    profiles = db.query(Profile).all()
    return profiles

def create_profile(request:UserProfile,db:Session):
    new_profile = Profile (
        lastname= request.lastname,
        firstname= request.firstname,
        othername= request.othername,
        bio= request.bio,
        gender= request.gender,
        location= request.location,
        user_id = request.user_id
        )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

def delete_profile(id:int,db:Session):
    
    delete_profile = db.query(Profile).filter(Profile.id == id).first()

    if delete_profile  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    if current_user.id == delete_profile.user_id :
        db.delete(delete_profile)
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to delete this post")

    return f"Profile with id {id} has been successfully deleted."
    
def update_profile(id:int,request:UserProfile,db:Session):
   
    update_profile = db.query(Profile).filter(Profile.id == id).first()

    update_profile.lastname= request.lastname,
    update_profile.firstname= request.firstname,
    update_profile.othername= request.othername,
    update_profile.bio= request.bio,
    update_profile.gender= request.gender,
    update_profile.location= request.location

    if update_profile  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    if current_user.id == update_profile.user_id :
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to update this post")

    return update_profile
    
def show_profile(id:int,db:Session):
    profile = db.query(Profile).filter(Profile.id==id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Profile with id {id} not found")
    
    return profile

