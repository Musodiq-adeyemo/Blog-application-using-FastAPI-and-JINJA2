from fastapi import APIRouter,Depends,status,UploadFile,File
from BlogPosts.schemas import ShowBlog,UpdateBlog,CreateBlog,ShowComment,CreateMessage,CreateComment
from typing import List
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.repository import blog
from fastapi_jwt_auth import AuthJWT
import shutil
from werkzeug.utils import secure_filename
from BlogPosts.models import PostImage

router = APIRouter(
    tags=["BlogPosts"],
    prefix = "/blogs"
)

@router.get('',response_model= List[ShowBlog],summary="Get all the Blog Posts")
def get_all(db:Session = Depends(get_db)):
    return blog.get_all(db)

@router.get('blogs/{id}',response_model=ShowBlog, status_code = status.HTTP_200_OK,summary="Get a Blog Posts by Id")
def show_post(id,db:Session = Depends(get_db)):
    return blog.show_post(id,db)

@router.post('/create', response_model=CreateBlog,status_code = status.HTTP_201_CREATED,summary="Create a Blog Posts")
def create_post(request:CreateBlog,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    #Authorize.jwt_required()
    return blog.create_post(request,db)


@router.put('/update/{id}',response_model=CreateBlog, status_code = status.HTTP_202_ACCEPTED,summary="Update a Blog Posts")
def update_post(id,request:UpdateBlog,db:Session = Depends(get_db)):
    return blog.update_post(id,request,db)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete a Blog Posts")
def delete_post(id,db:Session = Depends(get_db)):
    return blog.delete_post(id,db)
"""
@router.get('/{blog_title}',response_model=ShowBlog, status_code = status.HTTP_200_OK,summary="Get a Blog Posts by Title")
def get_title(blog_title:str,db:Session = Depends(get_db)):
    return blog.get_title(blog_title,db)

@router.get('/{title}/{author}',response_model=ShowBlog, status_code = status.HTTP_200_OK,summary="Get a Blog Posts by Title and Author")
def get_title_author(title:str,author:str,db:Session = Depends(get_db)):
    return blog.get_title_author(title,author,db)
"""
@router.post("/upload",summary="Upload your Post picture")
def upload(post_id:str,db:Session = Depends(get_db),file:UploadFile = File(...)):
    with open(f"BlogPosts/static/postimages/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    name = secure_filename(file.filename)
    mimetype = file.content_type

    image_post = PostImage(img = file.file.read(),minetype=mimetype, name=name,post_id=post_id)
    db.add(image_post)
    db.commit()
    return f"{name} has been Successfully Uploaded"

@router.get('comment/{id}',response_model=ShowComment, status_code = status.HTTP_200_OK,summary="Show blog Comment")
def show_comment(id,db:Session = Depends(get_db)):
    return blog.show_comment(id,db)

@router.post('/comment', response_model=ShowComment,status_code = status.HTTP_201_CREATED,summary="Create Comment")
def create_comment(request:CreateComment,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    #Authorize.jwt_required()
    return blog.create_comment(request,db)


@router.put('/update_comment/{id}',response_model=ShowComment, status_code = status.HTTP_202_ACCEPTED,summary="Edit Comment")
def update_comment(id,request:CreateComment,db:Session = Depends(get_db)):
    return blog.update_comment(id,request,db)

@router.delete('/delete_comment/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete Comment")
def delete_comment(id,db:Session = Depends(get_db)):
    return blog.delete_comment(id,db)

@router.post('/message', response_model=CreateMessage,status_code = status.HTTP_201_CREATED,summary="Send Message")
def create_message(request:CreateMessage,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    #Authorize.jwt_required()
    return blog.create_message(request,db)
