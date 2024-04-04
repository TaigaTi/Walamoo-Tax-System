from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

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

@app.get("/scenarios")
async def scenarios(request: Request):
    return templates.TemplateResponse("scenarios.html", {"request" : request})

@app.get("/query/")
async def query(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

@app.get("/xml/")
async def xml(request: Request):
    return templates.TemplateResponse("xml.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)