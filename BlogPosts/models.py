from sqlalchemy import Integer,Column,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func
from BlogPosts.database import Base,engine

class User(Base):
    __tablename__= "user"
    id = Column(Integer(), primary_key=True)
    email = Column(String(200), unique=True)
    username = Column(String(100),unique=True)
    password =Column(String(20))
    blogs= relationship('BlogPost',back_populates = "creator")
    user_profile =relationship('Profile',back_populates = "user")
    u_comments = relationship('Comment',back_populates = "user")
    
    def __repr__(self):
        return f"User {self.username}"
 
class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer(), primary_key=True)
    firstname = Column(String(100),nullable=False)
    lastname = Column(String(100),nullable=False)
    othername = Column(String(100),nullable=False)
    bio = Column(String(500),nullable=False)
    gender = Column(String(100),nullable=False)
    location = Column(String(100),nullable=False)
    created_at =Column(DateTime(timezone=True), server_default = func.now())
    user = relationship('User',back_populates = "user_profile")
    user_id = Column(Integer(), ForeignKey('user.id'))
    profile_image = relationship('ProfileImage',back_populates = "owner")

    def __repr__(self):
        return f"Profile {self.firstname} {self.lastname}"

class ProfileImage(Base):
    __tablename__= "profileimages"
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    img = Column(String(100))
    minetype = Column(String(100))
    profile_id = Column(Integer(), ForeignKey('profile.id'))
    owner = relationship('Profile',back_populates = "profile_image")
    user_id = Column(Integer(), ForeignKey('user.id'))

    def __repr__(self):
        return f"ProfileImage {self.name}"

class BlogPost(Base):
    __tablename__= "blogposts"
    id = Column(Integer(), primary_key=True)
    title = Column(String(100),nullable=False)
    content = Column(String(1000),nullable=False)
    author = Column(String(20),nullable=False)
    posted_at = Column(DateTime(timezone=True), server_default = func.now())
    updated_at = Column(DateTime(timezone=True), server_default = func.now())
    user_id = Column(Integer(), ForeignKey('user.id'))
    creator = relationship('User',back_populates="blogs")
    post_image = relationship('PostImage',back_populates="image_post")
    p_comments = relationship('Comment',back_populates="blog")
    
    def __repr__(self):
        return f"BlogPost {self.title} "

class PostImage(Base):
    __tablename__= "postimages"
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    img = Column(String(100))
    minetype = Column(String(100))
    post_id =Column(Integer(),ForeignKey('blogposts.id'))
    image_post = relationship('BlogPost',back_populates="post_image")

    def __repr__(self):
        return f"PostImage {self.name}"

class Comment(Base):
    __tablename__= "comments"
    id = Column(Integer(), primary_key=True)
    comment = Column(String(200))
    user_id = Column(Integer(), ForeignKey('user.id'))
    post_id = Column(Integer,ForeignKey('blogposts.id'))
    blog = relationship('BlogPost',back_populates = "p_comments")
    user = relationship('User',back_populates = "u_comments")
    commented_at = Column(DateTime(timezone=True), server_default = func.now())
    def __repr__(self):
        return f"Comment {self.id}"

class Message(Base):
    __tablename__= "messages"
    id = Column(Integer(), primary_key=True)
    email = Column(String(200))
    username = Column(String(100))
    message = Column(String(200))

Base.metadata.create_all(bind=engine)