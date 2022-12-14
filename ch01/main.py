from enum import Enum
from os import uname
import profile
from typing import Optional, List, Dict
from uuid import UUID, uuid1

from fastapi import FastAPI, Form, Cookie, Header, Response
from pydantic import BaseModel 

from bcrypt import checkpw, hashpw, gensalt
from datetime import date, datetime

from string import ascii_lowercase
from random import random


app = FastAPI()

valid_users = dict()
valid_profiles = dict()
pending_users = dict()
discussion_posts = dict()
request_headers = dict()
cookies = dict()

class User(BaseModel):
    username: str
    password: str


class ValidUser(BaseModel):
    id: UUID
    username: str
    password: str
    passphrase: str


class UserType(str, Enum):
    admin = "admin"
    teacher = "teacher"
    alumni = "alumni"
    student = "student"


class UserProfile(BaseModel):
    firstname: str
    lastname: str
    middle_initial: str
    age: Optional[int] = 0
    salary: Optional[int] = 0
    birthday: date
    user_type: UserType


class PostType(str, Enum):
    information = "information"
    inquiry = "inquiry"
    quote = "quote"
    twit = "twit"


class Post(BaseModel):
    topic: Optional[str] = None
    message: str
    date_posted: datetime


class ForumPost(BaseModel):
    id: UUID
    topic: Optional[str] = None
    message: str
    post_type: PostType 
    date_posted: datetime 
    username: str


class ForumDiscussion(BaseModel):
    id: UUID
    main_post: ForumPost
    replies: Optional[List[ForumPost]] = None 
    author: UserProfile

@app.get("/ch01/index")
def index():
    return {"message": "Welcome FastAPI Nerds"}


# /ch01/login?username=ivan&password=123
@app.get("/ch01/login")
def login(username: str, password: str):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        user = valid_users.get(username)
        if checkpw(password.encode(), user.passphrase.encode()):
            return user 
        else:
            return {"message": "invalid user"}


@app.post("/ch01/login/signup")
def signup(username: str, password: str):
    if (username == None and password == None):
        return {"message": "Invalid user"}
    elif not valid_users.get(username) == None:
        return {"message": "user exists"}
    else:
        user = User(username=username, password=password)
        pending_users[username] = user
        return user


@app.put("/ch01/account/profile/update/{username}")
def update_profile(username: str, id: UUID, new_profile: UserProfile):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            valid_profiles[username] = new_profile
            return {"message": "successfully updated"}
        else:
            return {"message": "user does not exist"}


@app.patch("/ch01/account/profile/update/names/{username}")
def update_profile_names(username: str, id: UUID, new_names: Dict[str, str]):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif new_names == None:
        return {"message": "new names are required"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            profile = valid_profiles[username]
            profile.firstname = new_names["firstname"]
            profile.lastname = new_names["lastname"]
            profile.middle_initial = new_names["mi"]
            valid_profiles[username] = profile
            return {"message": "successfully updated"}
        else:
            return {"message": "user does not exist"}


@app.delete("/ch01/discussion/posts/remove/{username}")
def delete_discussion(username: str, id: UUID):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif discussion_posts.get(id) == None:
        return {"message": "post does not exist"}
    else:
        del discussion_posts[id]
        return {"message": "main post deleted"}


# Path parameters
@app.delete("/ch01/login/remove/{username}")
def delete_user(username: str):
    if username == None:
        return {"message": "invalid user"}
    else:
        del valid_users[username]
        return {"message": "deleted user"}


@app.get("/ch01/login/{username}/{password}")
def login_with_token(username: str, password: str, id: UUID):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        user = valid_users[username]
        if user.id == id and checkpw(password.encode(), user.passphrase):
            return user
        else:
            return {"message": "invalid user"}


@app.get("/ch01/login")
def login(username: str, password: str):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        user = valid_users.get(username)
        if checkpw(password.encode(), user.passphrase.encode()):
            return user
        else:
            return {"message": "invalid user"}


# Query parameters
# ?skip=0&limit=10
@app.get("/ch01/login")
def login(username: str, password: str):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        user = valid_users.get(username)
        if checkpw(password.encode(), user.passphrase.encode()):
            return user
        else:
            return {"message": "invalid user"}


@app.delete("/ch01/login/remove/all")
def delete_users(usernames: List[str]):
    for user in usernames:
        del valid_users[user]
    return {"message": "deleted users"}


@app.patch("/ch01/account/profile/update/names/{username}")
def update_profile_names(username: str, id: UUID, new_names: Dict[str, str]):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif new_names == None:
        return {"message": "new names are required"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            profile = valid_profiles[username]
            profile.firstname = new_names["firstname"]
            profile.lastname = new_names["lastname"]
            profile.middle_initial = new_names["mi"]
            valid_profiles[username] = profile
            return {"message": "successfully updated"}
        else:
            return {"message": "user does not exist"}


# Default parameters
@app.delete("/ch01/delete/users/pending")
def delete_pending_users(accounts: List[str] = []):
    for user in accounts:
        del pending_users[user]
    return {"message": "deleted pending users"}


@app.get("/ch01/login/password/change")
def change_password(username: str, old_password: str = "", new_password: str = ""):
    password_len = 8
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif old_password == "" or new_password == "":
        characters = ascii_lowercase
        temporary_password = "".join(
            random.choice(characters) for i in range(password_len)
        )
        user = valid_users.get(username)
        user.password = temporary_password
        user.passphrase = hashpw(temporary_password.encode(), gensalt())
        return user
    else:
        user = valid_users.get(username)
        if user.password == old_password:
            user.password = new_password
            user.passphrase = hashpw(new_password.encode(), gensalt())
            return user 
        else:
            return {"message": "invalid user"}


# Optional parameters
@app.post("/ch01/login/username/unlock")
def unlock_username(id: Optional[UUID] = None):
    if id == None:
        return {"message": "token needed"}
    else:
        for key, val in valid_users.items():
            if val.id == id:
                return {"username": val.username}
            return {"message": "user does not exist"}


@app.post("/ch01/login/password/unlock")
def unlock_password(username: Optional[str] = None, id: Optional[UUID] = None):
    if username == None:
        return {"message": "username is required"}
    elif valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        if id == None:
            return {"message": "token needed"}
        else:
            user = valid_users.get(username)
            if user.id == id:
                return {"password": user.password}
            else:
                return {"message": "invalid token"}


# Mixing all types of parameters
@app.patch("/ch01/account/profile/update/names/{username}")
def update_profile_names(id: UUID, username: str = "", new_names: Optional[Dict[str, str]] = None):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif new_names == None:
        return {"message": "new names are required"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            profile = valid_profiles[username]
            profile.firstname = new_names["firstname"]
            profile.lastname = new_names["lastname"]
            profile.middle_initial = new_names["mi"]
            valid_profiles[username] = profile
            return {"message": "successfully updated"}
        else:
            return {"message": "user does not exist"}


# Request body
@app.post("/ch01/login/validate", response_model=ValidUser)
def approve_user(user: User):
    if not valid_users.get(user.username) == None:
        return ValidUser(id=None, username=None, password=None, passphrase=None)
    else:
        valid_user = ValidUser(
            id=uuid1(),
            username=user.username,
            password=user.password,
            passphrase=hashpw(user.password.encode(), gensalt()),
            )
        valid_users[user.username]=valid_user
        del pending_users[user.username]
        return valid_user


@app.put("/ch01/account/profile/update/{username}")
def update_profile(username: str, id: UUID, new_profile: UserProfile):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            valid_profiles[username] = new_profile
            return {"message": "successfully updated"}
        else:
            return {"message": "user does not exist"}


# Headers
# To access a request header, import first the Header function from the fastapi module. Then, declare
# the variable that has the same name as the header in the method service as str types and initialize
# the variable by calling the Header(None) function. The None argument enables the Header()
# function to declare the variable optionally, which is a best practice.
@app.get("/ch01/headers/verify")
def verify_headers(
    host: Optional[str] = Header(None),
    accept: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None),
    accept_encoding: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    ):
    request_headers["Host"] = host
    request_headers["Accept"] = accept
    request_headers["Accept-Language"] = accept_language
    request_headers["Accept-Encoding"] = accept_encoding
    request_headers["User-Agent"] = user_agent
    return request_headers


# Response data
@app.post("/ch01/discussion/posts/add/{username}")
def post_discussion(username: str, post: Post, post_type: PostType):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif not (discussion_posts.get(id) == None):
        return {"message": "post already exists"}
    else:
        forum_post = ForumPost(
            id=uuid1(),
            topic=post.topic,
            message=post.message,
            post_type=post_type,
            date_posted=post.data_posted,
            username=username,
            )
        user = valid_profiles[username]
        forum = ForumDiscussion(
            id=uuid1(),
            main_post=forum_post,
            author=user,
            replies=list(),
        )
        discussion_posts[forum.id] = forum
        return forum


@app.post("/ch01/login/validate", response_model=ValidUser)
def approve_user(user: User):
    if not valid_users.get(user.username) == None:
        return ValidUser(
            id=None,
            username=None,
            password=None,
            passphrase=None,
        )
    else:
        valid_user = ValidUser(
            id=uuid1(),
            username=user.username,
            password=user.password,
            passphrase=hashpw(user.password.encode(), gensalt()),
        )
        valid_users[user.username] = valid_user
        del pending_users[user.username]
        return valid_user


# Handling Form parameters (x-www-form-urlencoded media type)
# Form-handling services will not work without python-multipart
@app.post("/ch01/account/profile/add", response_model=UserProfile)
def add_profile(
    username: str,
    firstname: str = Form(...),
    lastname: str = Form(...),
    mid_init: str = Form(...),
    user_age: int = Form(...),
    sal: float = Form(...),
    bday: str = Form(...),
    utype: UserType = Form(...)
    ):
    if valid_users.get(username) == None:
        return UserProfile(
            firstname=None,
            lastname=None,
            middle_initial=None,
            age=None,
        )
    else:
        profile = UserProfile(
            firstname=firstname,
            lastname=lastname,
            middle_initial=mid_init,
            age=user_age, 
            birthday=datetime.strptime(bday, "%m/%d/Y"), 
            salary=sal, 
            user_type=utype
        )
        valid_profiles[username] = profile
        return profile


# Managing cookies
# The Cookie() function should always have the None argument to set the
# parameters optionally, ensuring that the API method executes without problems whenever the headers
# are not present in the request transaction. The following access_cookie() service retrieves all
# the remember-me authorization cookies created by the previous service:
@app.post("/ch01/login/rememberme/create")
def create_cookies(resp: Response, id: UUID, username: str = ""):
    resp.set_cookie(key="userkey", value=username)
    resp.set_cookie(key="identity", value=str(id))
    return {"message": "remember-me tokens created"}


@app.get("/ch01/login/cookies")
def access_cookies(userkey: Optional[str] = Cookie(None), identity: Optional[str] = Cookie(None)):
    cookies["userkey"] = userkey
    cookies["identity"] = identity
    return cookies