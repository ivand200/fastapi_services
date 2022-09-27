from enum import Enum
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

@app.get("/ch01/index")
def index():
    return {"message": "Welcome FastAPI Nerds"}


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


@app.delete("/ch01/login/remove/{username}")
def delete_user(username: str):
    if username == None:
        return {"message": "invalid user"}
    else:
        del valid_users[username]
        return {"message": "deleted user"}


@app.get("/ch01/login/{username}/{password}"):
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