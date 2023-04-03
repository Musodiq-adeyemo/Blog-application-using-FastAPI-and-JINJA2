from pydantic import BaseModel,Field
from typing import List,Optional
from datetime import datetime

class CreateUser(BaseModel):
    id : int
    email: str
    username : str
    password : str
    class Config():
        orm_mode = True 

class UserProfile(BaseModel):
    lastname : str
    firstname : str
    othername : str
    bio : str
    location : str
    gender : str
    created_at : datetime
    user_id : int

class ShowProfile(BaseModel):
    lastname : str
    firstname : str
    gender : str
    class Config():
        orm_mode = True

class ProfileImage(BaseModel):
    id : int
    name : str
    user_id : int

class CreateBlog(BaseModel):
    id :  int
    title: str
    content : str
    author : str
    posted_at : datetime
    user_id : int
    class Config():
        orm_mode = True

class UserBlog(BaseModel):
    username : str
    email: str
    class Config():
        orm_mode = True
    
class UpdateBlog(BaseModel):
    title: str
    content : str
    updated_at : datetime

class BlogUser(BaseModel):
    id : str
    title: str
    class Config():
        orm_mode = True

class BlogImage(BaseModel):
    id : int
    name : str
    post_id :  int
    

class ShowBlogImage(BaseModel):
    name : str
    class Config():
        orm_mode = True

class ShowBlog(BaseModel):
    id :  int
    title: str
    content : str
    author : str
    posted_at : datetime
    updated_at : datetime
    user_id : int
    #creator : UserBlog
    #post_image :ShowBlogImage

    class Config():
        orm_mode = True

class ShowUser(BaseModel):
    id : int
    username : str
    email: str
    #user_profile :ShowProfile
    #profile_image :ProfileImage
    #blogs : List[BlogUser]=[]

    class Config():
        orm_mode = True

class UserImage(BaseModel):
    name : str
    owner : UserBlog
    class Config():
        orm_mode = True

class UserLogin(BaseModel):
    id : int
    username : str
    password:str
    class Config():
        orm_mode = True


class Token(BaseModel):
    access_token : str
    token_type : str
    class Config():
        orm_mode = True

class TokenData(BaseModel):
    username:Optional[str] = None

class PasswordReset(BaseModel):
    email : str
    username :str

class NewPassword(BaseModel):
    token : str
    password : str
class VerifyToken(BaseModel):
    token : str

class Settings(BaseModel):
    authjwt_secret_key : str = "b6d504d64dd31e3d5eb1"
    authjwt_decode_algorithms : set = {"HS384","HS512"}
    #authjwt_denylist_enabled: bool = True
    #authjwt_denylist_token_checks: set = {"access","refresh"}
    authjwt_token_location : set = {"cookies"}
    auth_jwt_cookies_csrf_protect : bool = False
class CreateComment(BaseModel):
    comment: str
    user_id : int
    post_id : int

class ShowComment (BaseModel):
    comment : str
    #user :UserBlog
    #blog: BlogUser
    class Config():
        orm_mode = True

class CreateMessage(BaseModel):
    email : str
    username : str
    message : str
    class Config():
        orm_mode = True

class Setting(BaseModel):
   authjwt_secret_key : str = "b6d504d64dd31e3d5eb1"
   #authjwt_decode_algorithms : set = {"HS384","HS512"}
   authjwt_token_location : set = {"cookies"}
   auth_jwt_cookies_csrf_protect : bool = False 