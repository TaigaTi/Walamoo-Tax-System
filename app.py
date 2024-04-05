from dotenv import load_dotenv
from os import getenv

load_dotenv()

from typing import Dict, List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from models import *
from database import *

app = FastAPI()

SECRET = getenv("SECRET_KEY")
class NotAuthenticatedException(Exception):
    pass

manager = LoginManager(SECRET, "/login", not_authenticated_exception=NotAuthenticatedException)

app.include_router(db_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@manager.user_loader()
async def get_user_by_id(user_id: str):
    user = await user_collection.find_one({"user_id": user_id})
    return user

@app.get("/")
async def index(user: User = Depends(manager.optional)):
    if user is None:
        return RedirectResponse("/login/")
    return RedirectResponse("/dashboard/")

@app.get("/login/")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login/")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    user_id = data.username
    password = data.password

    user = await get_user_by_id(user_id)
    if not user:
        raise InvalidCredentialsException
    print(user, user_id, password)
    if user["password"] != password:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(data={"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/logout/")
async def logout(request: Request):
    return RedirectResponse("/login/")

@app.get("/preferences/")
async def preferences(request: Request):
    return templates.TemplateResponse("userPreferences.html", {"request": request})

@app.get("/dashboard/")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/subpages/mainDashboard/")
async def mainDashboard(request: Request):
    return templates.TemplateResponse("subpages/mainDashboard.html", {"request": request})

@app.get("/subpages/citiesDashboard/")
async def citiesDashboard(request: Request):
    return templates.TemplateResponse("subpages/citiesDashboard.html", {"request": request})

@app.get("/alerts/")
async def alerts(request: Request):
    return templates.TemplateResponse("alerts.html", {"request": request})

@app.post("/alerts/")
async def alerts(alert : Alert):
    await alert_collection.delete_many({})
    try:
        _ = await alert_collection.insert_one(alert.model_dump(mode="json"))
        return {"success": "Alert was successfully created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not create alert")

@app.get("/scenarios/")
async def scenarios(request: Request):
    return templates.TemplateResponse("scenarios.html", {"request" : request})

@app.get("/subpages/scenarioInformation/")
async def scenarioInformation(request: Request):
    check_alert: dict = await alert_collection.find_one({})
    if not check_alert:
        raise HTTPException(status_code=404, detail="No alerts found")
    
    alert: Alert = Alert(**check_alert)

    insufficient_taxpayers = []
    sufficient_taxpayers = []

    async for taxpayer in taxpayer_collection.find():
        tp = TaxPayer(**taxpayer)
        if tp.tax < alert.min_tax:
            insufficient_taxpayers.append(tp)
        elif tp.tax >= alert.min_tax:
            sufficient_taxpayers.append(tp)

    revenue = sum([taxpayer.tax for taxpayer in sufficient_taxpayers])

    minimum_revenue = "Exceeded" if revenue >= alert.min_revenue else "Not Exceeded"

    return templates.TemplateResponse("subpages/scenarioInformation.html", {
        "request" : request,
        "insufficient_taxpayers": set([tp.company for tp in insufficient_taxpayers]),
        "sufficient_taxpayers": set([tp.company for tp in sufficient_taxpayers]),
        "revenue": revenue,
        "minimum_revenue": minimum_revenue,
        "sufficient_count": len(sufficient_taxpayers)
    })

@app.get("/report/")
async def report(request: Request):
    return templates.TemplateResponse("scenarioReport.html", {"request": request})

@app.get("/recon/")
async def recon(request: Request):
    return templates.TemplateResponse("recon.html", {"request": request})

@app.get("/query/")
async def query(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

@app.get("/subpages/queryMenu/")
async def queryMenu(request: Request):
    return templates.TemplateResponse("subpages/queryMenu.html", {"request": request})

@app.get("/subpages/guidedQuery/")
async def guidedQuery(request: Request):
    return templates.TemplateResponse("subpages/guidedQuery.html", {"request": request})

@app.get("/subpages/adhocQuery/")
async def adhocQuery(request: Request):
    return templates.TemplateResponse("subpages/adhocQuery.html", {"request": request})

@app.get("/xml/")
async def xml(request: Request):
    return templates.TemplateResponse("dataReload.html", {"request": request})

@app.get("/logs/")
async def logs(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

@app.post("/api/v1/taxpayers/add/")
async def add_taxpayer(taxpayer: TaxPayer):
    try:
        _ = await taxpayer_collection.insert_one(taxpayer.model_dump(mode="json"))
        return {"success": "Taxpayer was successfully created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not create taxpayer")
    
@app.get("/api/v1/taxpayers/", response_model=List[TaxPayer])
async def get_all_taxpayers():
    all_taxpayers = []
    async for taxpayer in taxpayer_collection.find():
        all_taxpayers.append(taxpayer)
    return all_taxpayers

@app.get("/api/v1/taxpayers/clear/")
async def clear_taxpayers():
    await taxpayer_collection.delete_many({})
    return {"success": "Taxpayers were successfully cleared"}

@app.get("/api/v1/taxpayers/query/", response_model=List[TaxPayer])
async def query_taxpayers(company: str | None = None, country: str | None = None, tax: str | None = None):
    if not any([company, country, tax]):
        raise HTTPException(status_code=400, detail="Invalid query")
    
    query_key, query_value = ("company", company) if company else ("country", country) if country else ("tax", tax)

    results = []
    async for taxpayer in taxpayer_collection.find({query_key: {"$regex": rf"{query_value}", "$options": "i"}}):
        results.append(taxpayer)

    if results:
        return results
    raise HTTPException(status_code=404, detail="No taxpayers found")

@app.get("/api/v1/alerts/", response_model=List[Alert])
async def get_all_alerts():
    all_alerts = []
    async for alert in alert_collection.find():
        all_alerts.append(alert)
    if all_alerts:
        return all_alerts
    raise HTTPException(status_code=404, detail="No alerts found")


# Exceptions
@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_exception_handler(request, exc):
    return RedirectResponse("/login/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)