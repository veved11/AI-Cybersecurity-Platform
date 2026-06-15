from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas

from app.database.connection import engine, Base
from app.database.connection import SessionLocal
from app.api.user_api import router as user_router

from app.models.analysis import Analysis
from app.models.user import User
from app.models.alert import Alert

app = FastAPI(
    title="AI Cybersecurity Platform",

    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(user_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request
        }
    )
@app.get("/login-page")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )
@app.get("/generate-report")
def generate_report():

    file_name = "security_report.pdf"
    db = SessionLocal()

    total_users = db.query(User).count()

    total_analyses = db.query(Analysis).count()

    high_risk = db.query(Analysis).filter(
        Analysis.risk == "High"
    ).count()
    pdf = canvas.Canvas(file_name)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(
        100,
        800,
        "AI Cybersecurity Report"
    )

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        100,
        760,
        f"Total Users: {total_users}"
    )

    pdf.drawString(
        100,
        730,
        f"Total Analyses: {total_analyses}"

    )

    pdf.drawString(
        100,
        700,
        "Risk Score: 73.53"
    )

    pdf.drawString(
        100,
        670,
        f"High Risk Threats: {high_risk}"

    )

    pdf.drawString(
        100,
        640,
        "Latest Threat: Possible SQL Injection"
    )


    pdf.save()

    return FileResponse(
        file_name,
        media_type="application/pdf",
        filename=file_name
    )