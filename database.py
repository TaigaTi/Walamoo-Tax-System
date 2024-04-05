from motor.motor_asyncio import AsyncIOMotorClient

from typing import Annotated

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
from os import getenv

from models import *

load_dotenv()

db_router = APIRouter()

db_templates = Jinja2Templates(directory="templates/db_templates")

client = AsyncIOMotorClient(getenv("MONGO_URL"))
database = client["mydatabase"]

user_collection = database["users"]

async def get_users():
    users = []
    async for user in user_collection.find():
        users.append(User(**user))

    return users

@db_router.get("/secret/db/")
async def index(request: Request):
    return db_templates.TemplateResponse("index.html", {"request": request})

@db_router.post("/secret/db/create/user/")
async def create_user(user_id: Annotated[int, Form()], username: Annotated[str, Form()], password: Annotated[str, Form()]):
    try:
        user = User(user_id=user_id, name=username, password=password)
        new_user = await user_collection.insert_one(user.model_dump(mode="json"))
        return {"success": "User was successfully created"}
    except Exception as e:
        print(e)
        return {"error": "Could not create user"}
    
@db_router.get("/secret/db/user_page/")
async def create_user_form(request: Request):
    return db_templates.TemplateResponse("addUser.html", {"request": request})
    
@db_router.get("/secret/db/users/", response_model=str)
async def get_users_html(request: Request):
    users = await get_users()

    return db_templates.TemplateResponse("viewUsers.html", {"request": request, "users": users})

__all__ = ["db_router", "user_collection"]