from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv, path

load_dotenv()

from typing import Dict, List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from models import *
from database import *

from manager import manager, NotAuthenticatedException

app = FastAPI()

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
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@app.get("/login/form/")
async def login_form(request: Request):
    return templates.TemplateResponse("subpages/loginForm.html", {"request": request, "user": None})

@app.get("/login/error/")
async def login_error(request: Request, message: str = "", canContinue: str = None):
    return templates.TemplateResponse("subpages/loginError.html", {
        "request": request, 
        "user": None,
        "message": message,
        "GIS": canContinue
    })

@app.post("/login/")
async def login(response: Response, data: OAuth2PasswordRequestForm = Depends()):
    user_id = data.username
    password = data.password

    user = await get_user_by_id(user_id)
    if not user or user["password"] != password:
        return {"error": "Invalid credentials"}
    
    print("User", user_id, "has valid credentials")
    
    access_token = manager.create_access_token(data={"sub": user_id}, expires=timedelta(days=1))
    manager.set_cookie(response, access_token)

    log = Logs(user_id=user_id, name=user["name"], activity="Login", time=str(datetime.now()), admin=user['is_admin'])
    log_collection.insert_one(log.model_dump(mode="json"))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/logout/")
async def logout(request: Request, response: Response, user: User = Depends(manager)):
    log = Logs(user_id=user["user_id"], name=user["name"], activity="Logout", time=str(datetime.now()), admin=user["is_admin"])
    log_collection.insert_one(log.model_dump(mode="json"))

    manager.set_cookie(response, "deleted")
    return {"access_token": "", "token_type": "bearer"}

@app.get("/preferences/")
async def preferences(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("userPreferences.html", {"request": request, "user": user})

@app.get("/dashboard/")
async def dashboard(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/subpages/mainDashboard/")
async def mainDashboard(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("subpages/mainDashboard.html", {"request": request, "user": user})

@app.get("/subpages/citiesDashboard/")
async def citiesDashboard(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("subpages/citiesDashboard.html", {"request": request, "user": user})

@app.get("/alerts/")
async def alerts(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("alerts.html", {"request": request, "user": user})

@app.post("/alerts/")
async def alerts(alert : Alert, user: User = Depends(manager)):
    await alert_collection.delete_many({})
    try:
        _ = await alert_collection.insert_one(alert.model_dump(mode="json"))
        return {"success": "Alert was successfully created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not create alert")

@app.get("/scenarios/")
async def scenarios(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("scenarios.html", {"request" : request, "user": user})

@app.get("/subpages/scenarioInformation/")
async def scenarioInformation(request: Request, user: User = Depends(manager)):
    check_alert: dict = await alert_collection.find_one({})
    taxpayers : list = taxpayer_collection.find({})
    if not check_alert or not taxpayers:
        return templates.TemplateResponse("subpages/scenarioInformation.html", {
            "request" : request,
            "user": user,
            "error": "No alerts or taxpayers found"
        })
    
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
        "user": user,
        "insufficient_taxpayers": set([tp.company for tp in insufficient_taxpayers]),
        "sufficient_taxpayers": set([tp.company for tp in sufficient_taxpayers]),
        "revenue": revenue,
        "minimum_revenue": minimum_revenue,
        "sufficient_count": len(sufficient_taxpayers)
    })

@app.get("/report/")
async def report(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("scenarioReport.html", {"request": request, "user": user})

@app.get("/recon/")
async def recon(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("recon.html", {"request": request, "user": user})

@app.get("/recon/view_local_statement")
async def view_local_statement(request: Request, user: User = Depends(manager)):
    taxpayers = []

    async for taxpayer in taxpayer_collection.find():
        tp = TaxPayer(**taxpayer)
        taxpayers.append(tp)

    return templates.TemplateResponse("subpages/queryReport.html", {"request": request, "user": user, "taxpayers": taxpayers, "totalRecords": len(taxpayers)})

@app.get("/query/")
async def query(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("query.html", {"request": request, "user": user})

@app.get("/subpages/queryMenu/")
async def queryMenu(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("subpages/queryMenu.html", {"request": request, "user": user})

@app.get("/subpages/guidedQuery/")
async def guidedQuery(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("subpages/guidedQuery.html", {"request": request, "user": user})

@app.get("/subpages/adhocQuery/")
async def adhocQuery(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("subpages/adhocQuery.html", {"request": request, "user": user})

@app.get("/xml/")
async def xml(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("dataReload.html", {"request": request, "user": user})

@app.get("/logs/")
async def logs(request: Request, user: User = Depends(manager)):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    
    logs = []

    async for log in log_collection.find():
        logs.append(log)

    return templates.TemplateResponse("logs.html", {"request": request, "user": user, "logs": logs})

@app.get("/logs/clear/")
async def clear_logs(request: Request, user: User = Depends(manager)):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    
    await log_collection.delete_many({})
    return "<h2 class='subtitle'>Logs have been Cleared</h2>"

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
async def query_taxpayers(company: str | None = None, country: str | None = None, tax: str | None = None, report: bool = False, user: User = Depends(manager)):
    if not any([company, country, tax]):
        raise HTTPException(status_code=400, detail="Invalid query")
    
    query_key, query_value = ("company", company) if company else ("country", country) if country else ("tax", tax)

    results : List[dict]= []
    async for taxpayer in taxpayer_collection.find({query_key: {"$regex": rf"{query_value}", "$options": "i"}}):
        results.append(taxpayer)

    if results and not report:
        return results
    if results and report:
        filename = "static/reports/" + user['user_id'] + "_report.txt"
        
        with open(filename, "w") as fp:
            keys = list(results[0].keys())[1:]
            for key in keys:
                fp.write(key + ", ")
            fp.write("\n")

            for result in results:
                for key in keys:
                    fp.write(str(result[key]) + ", ")
                fp.write('\n')

        return FileResponse(filename, 200, {"Content-Disposition": "attachment; filename=" + filename}, filename="report.txt")

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
    return RedirectResponse(f"/login/")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse("error.html", {"request": request, "status_code": exc.status_code, "detail": exc.detail}, status_code=exc.status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)