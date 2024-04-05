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
taxpayer_collection = database["taxpayers"]
alert_collection = database['alerts']

async def get_users():
    users = []
    async for user in user_collection.find():
        users.append(User(**user))

    return users

# Secret Routes

@db_router.get("/secret/db/")
async def index(request: Request):
    return db_templates.TemplateResponse("index.html", {"request": request})

@db_router.post("/secret/db/create/user/")
async def create_user(user_id: Annotated[str, Form()], username: Annotated[str, Form()], password: Annotated[str, Form()], is_admin: Annotated[bool, Form()]):
    try:
        user = User(user_id=user_id, name=username, password=password, is_admin=is_admin)
        _ = await user_collection.insert_one(user.model_dump(mode="json"))
        return {"success": "User was successfully created"}
    except Exception as e:
        print(e)
        return {"error": "Could not create user"}
    
@db_router.get("/secret/db/user_page/")
async def create_user_form(request: Request):
    return db_templates.TemplateResponse("addUser.html", {"request": request})
    
@db_router.get("/secret/db/users/")
async def get_users_html(request: Request):
    users = await get_users()

    return db_templates.TemplateResponse("viewUsers.html", {"request": request, "users": users})

@db_router.get("/secret/db/taxpayer_page/")
async def create_taxpayer_form(request: Request):
    return db_templates.TemplateResponse("addTaxpayer.html", {"request": request})

@db_router.post("/secret/db/create/taxpayer/")
async def create_taxpayer( payer_id: Annotated[str, Form()], company: Annotated[str, Form()], street: Annotated[str, Form()], city: Annotated[str, Form()], country: Annotated[str, Form()], tax: Annotated[int, Form()]):
    try:
        taxpayer = TaxPayer( payer_id=payer_id, company=company, street=street, city=city, country=country, tax=tax)
        new_taxpayer = await taxpayer_collection.insert_one(taxpayer.model_dump(mode="json"))
        return {"success": "Taxpayer was successfully created"}
    except Exception as e:
        print(e)
        return {"error": "Could not create taxpayer"}
    
@db_router.get("/secret/db/taxpayers/")
async def get_taxpayers_html(request: Request):
    taxpayers = []

    async for taxpayer in taxpayer_collection.find():
        taxpayers.append(TaxPayer(**taxpayer))

    return db_templates.TemplateResponse("viewTaxpayers.html", {"request": request, "taxpayers": taxpayers})

__all__ = ["db_router", "user_collection", "taxpayer_collection", "alert_collection"]