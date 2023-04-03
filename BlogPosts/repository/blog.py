from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from BlogPosts.models import BlogPost,Comment,Message
from BlogPosts.schemas import UpdateBlog,CreateBlog,CreateComment,CreateMessage
from typing import List
from BlogPosts.security.get_current_user import get_current_user 

current_user = get_current_user

def get_all(db:Session):
    blogs = db.query(BlogPost).all()
    return blogs

def create_post(request:CreateBlog,db:Session):
    new_blog = BlogPost(title=request.title,content=request.content,author=request.author,user_id = request.user_id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

def delete_post(id:int,db:Session):
    
    post_delete = db.query(BlogPost).filter(BlogPost.id == id).first()

    if post_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    else:
        db.delete(post_delete)
        db.commit()
    
    return f"Blog Post with id {id} has been successfully deleted."
    
def update_post(id:int,request:UpdateBlog,db:Session):
   
    post_update = db.query(BlogPost).filter(BlogPost.id == id).first()

    post_update.title = request.title
    post_update.content = request.content

    if post_update  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    else:
        db.commit()
        
    return post_update
    
def show_post(id:int,db:Session):
    blog = db.query(BlogPost).filter(BlogPost.id==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with id {id} not found")
    
    return blog

def get_title(blog_title:str,db:Session):
    blogs = db.query(BlogPost).all()
    for blog in blogs :
        if blog.title == blog_title : 
            return blog
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with title {blog_title} not found")

def get_title_author(title:str,author:str,db:Session):
    blogs = db.query(BlogPost).all()
    for blog in blogs :
        if blog.title == title and blog.author==author: 
            return blog
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with title {title} and author {author}  not found")

def create_comment(request:CreateComment,db:Session):
    new_comment = Comment(comment=request.comment,user_id = request.user_id,post_id=request.post_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def delete_comment(id:int,db:Session):
    
    comment_delete = db.query(Comment).filter(Comment.id == id).first()

    if comment_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    if current_user.id == comment_delete.user_id :
        db.delete(comment_delete)
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to delete this comment")

    return f"Comment with id {id} has been successfully deleted."
    
def update_comment(id:int,request:CreateComment,db:Session):
   
    comment_update = db.query(Comment).filter(Comment.id == id).first()

    comment_update.comment = request.comment
    comment_update.user_id = request.user_id
    comment_update.post_id

    if comment_update  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    if current_user.id == comment_update.user_id :
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to edit this comment")

    return comment_update

def show_comment(id:int,db:Session):
    Comment = db.query(Comment).filter(Comment.id==id).first()
    if not Comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Comment with id {id} not found")
    
    return Comment

def create_message(request:CreateMessage,db:Session):
    new_message = Message(message=request.message,username=request.username,email=request.email)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message