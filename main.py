from fastapi import FastAPI,Request,Depends,Form,HTTPException,status,Response,UploadFile,File
from BlogPosts.routers import blog
from BlogPosts.routers import user
from BlogPosts.routers import authentication
from BlogPosts.routers import password_reset
from BlogPosts.routers import verify_token
from BlogPosts.routers import templates
from BlogPosts.routers import profile
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from fastapi.responses import HTMLResponse,RedirectResponse
from BlogPosts.models import BlogPost,User,ProfileImage,PostImage,Comment,Message,Profile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from BlogPosts.security.hashing import Hash
from datetime import timedelta
from fastapi_jwt_auth import AuthJWT
from BlogPosts.schemas import Setting
from werkzeug.utils import secure_filename
import shutil



SECRET = "b6d504d64dd31e3d5eb1"

access_token_expire =timedelta(days=30)
refresh_token_expire = timedelta(days=1)
new_access_token_expire = timedelta(days=7)
access_algorithm = "HS384"
refresh_algorithm = "HS512"

@AuthJWT.load_config
def get_config():
    return Setting()

app= FastAPI(
    docs_url = "/docs",
    redoc_url= "/redocs",
    title="SIRMUSO BLOGSITE API",
    description="FRAMEWORK FOR SIRMUSO BLOGSITE API",
    version="4.0",
    openapi_url="/api/v2/openapi.json"
    
)

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(blog.router)
app.include_router(password_reset.router)
app.include_router(templates.router)


templates = Jinja2Templates(directory="BlogPosts/templates")
app.mount("/static",StaticFiles(directory="BlogPosts/static"),name="static")



# Getting all posts and displaying it
@app.get('/',response_class=HTMLResponse,tags=["Template"])
def posts(request: Request, db:Session = Depends(get_db)):
    users = db.query(User).all()
    images = db.query(ProfileImage).all()
    pimages = db.query(PostImage).all()
    blogs = db.query(BlogPost).all()
    comments = db.query(Comment).all()
    

    return templates.TemplateResponse("post.html",{"request":request,"users":users,"comments":comments,"images":images,"pimages":pimages,"blogs":blogs})

# User registration route
@app.get("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request):
    return templates.TemplateResponse("signup.html",{"request":request})

@app.post("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request,username:str=Form(...),email:str=Form(...),password:str=Form(...),password2:str=Form(...), db:Session = Depends(get_db)):
    errors=[]
    if not email :
        errors.append("Not a proper Email")

    if password == password2 and len(password) > 7 :
        new_user = User(username=username,email=email,password=Hash.bcrypt(password))
        db.add(new_user)
        db.commit()
        redirect_url = "user_info"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
    if len(errors) > 0 :
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})
    else:
        errors.append("Password dont match or less than 8 charaters")
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})
        
# User information route
@app.get('/user_info',response_class=HTMLResponse,tags=["Template"])
def users(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    users = db.query(User).all()
    return templates.TemplateResponse("user.html",{"request":request,"current_user":current_user,'users':users})

#LOGIN AUTHENTICATION
@app.get("/signin",tags=["Template"])
def login(request: Request):
    return templates.TemplateResponse("signin.html",{"request":request})


@app.post("/signin",tags=["Template"])
def login(request: Request,response:Response,Authorize:AuthJWT=Depends(),username:str=Form(...),password:str=Form(...),db:Session = Depends(get_db)):
    errors = []
    user = db.query(User).filter(User.username==username).first()

    if user is None:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})
    
    verify_password = Hash.verify_password(password,user.password)

    if (username == user.username and verify_password):
        access_token = Authorize.create_access_token(subject=user.username,expires_time=access_token_expire)
        redirect_url = "/settings"
        resp = RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
        Authorize.set_access_cookies(access_token,resp)
        return resp
    else:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})

        
# Profile Settings route
@app.get("/settings",response_class=HTMLResponse,tags=["Template"])
def settings(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("settings.html",{"request":request})

@app.post("/settings",response_class=HTMLResponse,tags=["Template"])
def settings(request: Request,user_id:int=Form(...),firstname:str=Form(...),lastname:str=Form(...),othername:str=Form(...),bio:str=Form(...),location:str=Form(...),gender:str=Form(...), db:Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        new_profile = Profile(lastname=lastname,user_id=user_id,bio=bio,gender=gender,location=location,firstname=firstname,othername=othername)
        db.add(new_profile)
        db.commit()
        redirect_url = "dashboard"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)    
    else: 
        return templates.TemplateResponse("settings.html",{"request":request,"new_user":new_profile})

# dashboard route
@app.get("/dashboard",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    profiles = db.query(Profile).all()
    users = db.query(User).all()
    images = db.query(ProfileImage).all()
    pro = db.query(Profile).all()
    return templates.TemplateResponse("dashboard.html",{"request":request,"profile":profiles,"users":users,"images":images,"pro":pro,'current_user':current_user})

@app.get("/edit_profile/{profile_id}",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request,profile_id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    return templates.TemplateResponse("dashboard.html",{"request":request,"profile":profile})

@app.post("/edit_profile/{profile_id}",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request,profile_id:int,firstname:str=Form(...),lastname:str=Form(...),othername:str=Form(...),bio:str=Form(...),location:str=Form(...),gender:str=Form(...), db:Session = Depends(get_db)):
    
    update_profile = db.query(Profile).filter(Profile.id == profile_id).first()

    update_profile.lastname = lastname,
    update_profile.firstname = firstname,
    update_profile.othername = othername,
    update_profile.bio = bio,
    update_profile.gender = gender,
    update_profile.location = location
    
    db.commit()
    redirect_url = "profile"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
#Image Upload route
@app.get("/upload_pimage",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("upload_profile.html",{"request":request})

@app.post("/upload_pimage",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,profile_id:int=Form(...),user_id:str=Form(...),file:UploadFile = File(...),db:Session = Depends(get_db)):
    
    with open(f"BlogPosts/static/profileimages/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    name = secure_filename(file.filename)
    mimetype = file.content_type

    image_upload = ProfileImage(img = file.file.read(),minetype=mimetype, name=name,profile_id=profile_id,user_id=user_id)
    db.add(image_upload)
    db.commit()
    redirect_url = "dashboard"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    

# profile page route
@app.get('/profile',response_class=HTMLResponse,tags=["Template"])
def users(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    users = db.query(User).all()
    profiles = db.query(Profile).all()
    images = db.query(ProfileImage).all()

    return templates.TemplateResponse("profile.html",{"request":request,"users":users,"profiles":profiles,"images":images,'current_user':current_user})

# creating Post route
@app.get('/create_post',response_class=HTMLResponse,tags=["Template"])
def create_post(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("new_post.html",{"request":request})

@app.post('/create_post',response_class=HTMLResponse,tags=["Template"])
def create_post(request: Request, db:Session = Depends(get_db),title:str=Form(...),content:str=Form(...),author:str=Form(...),user_id:int=Form(...)):
    errors = []
    try:
        new_blog = BlogPost(title=title,content=content,author=author,user_id = user_id)
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong make sure you are doing the right thing")
        return templates.TemplateResponse("new_post.html",{"request":request,"errors":errors})

# Editing Post route
@app.get('/edit_post/{id}',response_class=HTMLResponse,tags=["Template"])
def update_post(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    blog = db.query(BlogPost).filter(BlogPost.id == id).first()
    return templates.TemplateResponse("edit.html",{"request":request,"blog":blog})

@app.post('/edit_post/{id}',response_class=HTMLResponse,tags=["Template"])
def update_post(request: Request,id:int, db:Session = Depends(get_db),title:str=Form(...),content:str=Form(...)):
    errors = []
    try:
        update_post = db.query(BlogPost).filter(BlogPost.id == id).first()
        update_post.title=title
        update_post.content=content
        db.commit()
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong, You are not authorized to edit this post.")
        return templates.TemplateResponse("edit.html",{"request":request,"errors":errors})

#delete post route
@app.get('/delete_post/{id}',tags=["Template"])
def delete_post(request: Request,id:int, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    errors= []
    try:
        delete_post = db.query(BlogPost).filter(BlogPost.id == id).first()
        db.delete(delete_post)
        db.commit()
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        errors.append("Something went Wrong, You are not authorized to delete this Post.")
        return templates.TemplateResponse("post.html",{"request":request,"errors":errors})

#Post image upload route
@app.get("/upload_postimage",response_class=HTMLResponse,tags=["Template"])
def upload_postimage(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("upload_postimage.html",{"request":request})

@app.post("/upload_postimage",response_class=HTMLResponse,tags=["Template"])
def upload_postimage(request: Request,post_id:int=Form(...),file:UploadFile = File(...),db:Session = Depends(get_db)):
    try:

        with open(f"BlogPosts/static/postimages/{file.filename}","wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        name = secure_filename(file.filename)
        mimetype = file.content_type

        image_post = PostImage(img = file.file.read(),minetype=mimetype, name=name,post_id=post_id)
        db.add(image_post)
        db.commit()
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("upload_postimage.html",{"request":request})
# about Route
@app.get("/about",response_class=HTMLResponse,tags=["Template"])
def about(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("about.html",{"request":request})

# Comment Route
@app.get('/comment',response_class=HTMLResponse,tags=["Template"])
def comment(request: Request):
    return templates.TemplateResponse("comment.html",{"request":request})

@app.post('/comment',response_class=HTMLResponse,tags=["Template"])
def comment(request: Request, db:Session = Depends(get_db),post_id:int=Form(...),comment:str=Form(...),user_id:int=Form(...)):
    errors = []
    try:
        new_comment = Comment(post_id=post_id,comment=comment,user_id = user_id)
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong, you are not authorized to comment on this post.")
        return templates.TemplateResponse("comment.html",{"request":request,"errors":errors})

# Contact page route
@app.get('/contact',response_class=HTMLResponse,tags=["Template"])
def contact(request: Request):
    return templates.TemplateResponse("contact.html",{"request":request})

@app.post('/contact',response_class=HTMLResponse,tags=["Template"])
def contact(request: Request, db:Session = Depends(get_db),username:str=Form(...),email:str=Form(...),message:str=Form(...)):
    errors = []
    try:
        new_message = Message(username=username,email=email,message=message)
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong, you are not authorized to send message.")
        return templates.TemplateResponse("contact.html",{"request":request,"errors":errors})

# Admin message
@app.get('/message',response_class=HTMLResponse,tags=["Template"])
def message(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    messages = db.query(Message).all()
    return templates.TemplateResponse("message.html",{"request":request,"messages":messages,"current_user":current_user})

#LOGOUT 


@app.get("/logout")
def logout(Authorize:AuthJWT=Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies
    
    redirect_url = "/"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

