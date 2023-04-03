from fastapi import Depends,APIRouter,Request,FastAPI,Form
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from BlogPosts.schemas import VerifyToken
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from fastapi.responses import HTMLResponse
from BlogPosts.models import BlogPost,User,ProfileImage,PostImage,Comment
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from BlogPosts.message import get_flashed_messages
from flask import flash

router = APIRouter(
    tags=["Templates Display"]
)
