from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.models import User
from BlogPosts.security.hashing import Hash
from fastapi_jwt_auth import AuthJWT
from datetime import timedelta
from BlogPosts.schemas import UserLogin,Token,Settings
from typing import List
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    tags=["Login Authentication"]
)

access_token_expire =timedelta(minutes=30)
refresh_token_expire = timedelta(days=1)
new_access_token_expire = timedelta(days=7)
access_algorithm = "HS384"
refresh_algorithm = "HS512"

#denylist =set()

@AuthJWT.load_config
def get_config():
    return Settings()
"""
@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in denylist
"""

@router.post('/login',summary="Login Your Account")
def login(request:OAuth2PasswordRequestForm=Depends(),Authorize:AuthJWT=Depends(), db:Session=Depends(get_db)):
    
    user = db.query(User).filter(User.username==request.username).first()
    
    verify_password = Hash.verify_password(request.password,user.password)
   
    if (request.username == user.username and verify_password):
        access_token = Authorize.create_access_token(subject=request.username,expires_time=access_token_expire, algorithm=access_algorithm)
        refresh_token = Authorize.create_refresh_token(subject=request.username,expires_time=refresh_token_expire,algorithm=refresh_algorithm)
        
        Authorize.set_access_cookies(access_token)
        Authorize.set_refresh_cookies(refresh_token)
        return {"access-token":access_token,"refresh_token":refresh_token}

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Username or Password")
        

@router.get("/login/refresh",summary="Refresh Login Access Token")
def refresh_login(Authorize:AuthJWT=Depends()):
    try:

        Authorize.jwt_refresh_token_required()
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to verify your access token")
    
    current_user = Authorize.get_jwt_subject()
    
    new_access_token = Authorize.create_access_token(subject=current_user,fresh=True,expires_time=new_access_token_expire)
    #Authorize.set_access_cookies(new_access_token)

    return {"new_access_token" : new_access_token}

@router.delete("/logout")
def logout(Authorize:AuthJWT=Depends()):
    try:

        Authorize.jwt_required()

        Authorize.unset_access_cookies()

        return {"successfully logout"}

    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to verify your access token")
    
"""
    jti = Authorize.get_raw_jwt()['jti']
    denylist.add(jti)
    
    Authorize.jwt_refresh_token_required()
    jti = Authorize.get_raw_jwt()['jti']
    denylist.add(jti)
"""
    
@router.get("/protected")
def private(Authorize:AuthJWT=Depends()):
    try:

        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        return {"current_user":current_user.username}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to verify your access token")