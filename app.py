from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import *
from database import *

app = FastAPI()

app.include_router(db_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

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

@app.get("/scenarios/")
async def scenarios(request: Request):
    return templates.TemplateResponse("scenarios.html", {"request" : request})

@app.get("/subpages/scenarioInformation/")
async def scenarioInformation(request: Request):
    return templates.TemplateResponse("subpages/scenarioInformation.html", {"request" : request})

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
    
@app.get("/api/v1/taxpayers/")
async def get_all_taxpayers():
    all_taxpayers = []
    async for taxpayer in taxpayer_collection.find():
        all_taxpayers.append(taxpayer)
    return all_taxpayers

# @app.get("/users/{user_id}", response_model=User)
# async def get_user(user_id: int):
#     user = await user_collection.find_one({"id": user_id})
#     if user:
#         return user
#     raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)