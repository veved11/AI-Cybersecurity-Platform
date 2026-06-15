from app.models.user import User
from app.models.analysis import Analysis
from app.models.alert import Alert
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.security.jwt_handler import create_access_token
from app.security.jwt_handler import verify_token

from app.database.connection import SessionLocal
from app.models.user import User
import bcrypt
import joblib

model = joblib.load("app/ai/model.pkl")
router = APIRouter()

security = HTTPBearer()


# ===== Schemas =====

class RegisterData(BaseModel):
    username: str
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str
class AnalysisData(BaseModel):
    text: str

# ===== Register =====
@router.post("/register")
def register(
    data: RegisterData
):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = User(
        username=data.username,
        email=data.email,
        password=hashed_password,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully ✅",
        "email": new_user.email,
        "username": new_user.username
    }

# ===== Login =====

@router.post("/login")
def login(
    data: LoginData
):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_ok = bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password.encode("utf-8")
    )

    if not password_ok:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "email": user.email,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ===== Token Check =====

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return payload


# ===== Dashboard =====

@router.get("/dashboard")
def dashboard(
    user=Depends(get_current_user)
):
    return {
        "message": "Welcome Dashboard 🔐",
        "user": user
    }


# ===== Admin =====

@router.get("/admin")
def admin(
    user=Depends(get_current_user)
):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return {
        "message": "Welcome Admin 👑"
    }

@router.get("/users")
def get_users():

    db = SessionLocal()

    users = db.query(User).all()

    return users

@router.delete("/users/{user_id}")
def delete_user(user_id: int):

    db = SessionLocal()

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }
@router.put("/users/{user_id}/role")
def change_role(
    user_id: int
):

    db = SessionLocal()

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role == "admin":
        user.role = "user"
    else:
        user.role = "admin"

    db.commit()

    return {
        "message": "User promoted to admin 👑"
    }
@router.post("/analyze")
def analyze(
    data: AnalysisData
):

    db = SessionLocal()

    text = data.text.lower()

    if "failed login" in text:

        risk = "High"
        score = 75
        result = "Possible Brute Force Attack"

    elif "select" in text or "drop table" in text:

        risk = "Critical"
        score = 100
        result = "Possible SQL Injection"

    elif "port scan" in text:

        risk = "Medium"
        score = 50
        result = "Possible Port Scanning Activity"

    elif "xss" in text or "<script>" in text:

        risk = "High"
        score = 75
        result = "Possible Cross Site Scripting (XSS)"

    elif "nmap" in text:

        risk = "Medium"
        score = 50
        result = "Network Scanning Detected"

    elif "admin" in text and "failed" in text:

        risk = "High"
        score = 75
        result = "Possible Admin Account Attack"

    else:

        risk = "Low"
        score = 25
        result = "No obvious threat detected"

    new_analysis = Analysis(
        text=data.text,
        risk=risk,
        analysis=result
    )

    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return {
        "risk": risk,
        "score": score,
        "analysis": result
    }
@router.get("/analyses")
def get_analyses():

    db = SessionLocal()

    analyses = db.query(Analysis).all()

    return analyses
@router.get("/stats")
def get_stats():

    db = SessionLocal()

    total_users = db.query(User).count()

    total_analyses = db.query(Analysis).count()

    high_risk = db.query(Analysis).filter(
        Analysis.risk == "High"
    ).count()

    critical_risk = db.query(Analysis).filter(
        Analysis.risk == "Critical"
    ).count()

    return {
        "total_users": total_users,
        "total_analyses": total_analyses,
        "high_risk": high_risk,
        "critical_risk": critical_risk
    }
@router.get("/latest-analyses")
def latest_analyses():

    db = SessionLocal()

    analyses = db.query(Analysis)\
        .order_by(Analysis.id.desc())\
        .limit(5)\
        .all()

    return analyses
@router.post("/upload-log")
async def upload_log(
    file: UploadFile = File(...)
):

    db = SessionLocal()

    content = await file.read()

    text = content.decode("utf-8").lower()

    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]

    classes = model.classes_

    threat_scores = {}

    for i in range(len(classes)):
        threat_scores[classes[i]] = round(
            probabilities[i] * 100,
            2
        )
    detected_threats = []

    if "failed login" in text:
        detected_threats.append("Brute Force")

    if "select" in text or "drop table" in text:
        detected_threats.append("SQL Injection")

    if "<script>" in text or "xss" in text:
        detected_threats.append("XSS")

    if "port scan" in text or "nmap" in text:
        detected_threats.append("Port Scan")
    probabilities = model.predict_proba([text])[0]
    confidence = round(max(probabilities) * 100, 2)
    if prediction == "SQL Injection":

        risk = "Critical"
        score = 100


    elif prediction == "Brute Force":

        risk = "High"
        score = 75


    elif prediction == "XSS":

        risk = "High"
        score = 75


    elif prediction == "Port Scan":

        risk = "Medium"
        score = 50


    else:

        risk = "Low"
        score = 25

    if detected_threats:
        result = ", ".join(detected_threats)
    else:
        result = prediction
    new_analysis = Analysis(
        text=text,
        risk=risk,
        analysis=result
    )

    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    if risk in ["High", "Critical"]:

        new_alert = Alert(
            threat_type=result,
            risk=risk,
            message=f"Security Alert: {result}"
        )

        db.add(new_alert)
        db.commit()

    return {
        "filename": file.filename,
        "risk": risk,
        "score": score,
        "confidence": confidence,
        "analysis": result,
        "threat_scores": threat_scores
    }

@router.get("/alerts")
def all_alerts():

    db = SessionLocal()

    alerts = db.query(Alert).all()

    return alerts


@router.get("/risk-score")
def risk_score():

    db = SessionLocal()

    total = db.query(Analysis).count()

    if total == 0:

        return {
            "average_score": 0
        }

    critical = db.query(Analysis).filter(
        Analysis.risk == "Critical"
    ).count()

    high = db.query(Analysis).filter(
        Analysis.risk == "High"
    ).count()

    medium = db.query(Analysis).filter(
        Analysis.risk == "Medium"
    ).count()

    low = db.query(Analysis).filter(
        Analysis.risk == "Low"
    ).count()

    score = (
        critical * 100 +
        high * 75 +
        medium * 50 +
        low * 25
    ) / total

    return {
        "average_score": round(score, 2),
        "total_analyses": total
    }
@router.get("/threat-stats")
def threat_stats():

    db = SessionLocal()

    brute_force = db.query(Analysis).filter(
        Analysis.analysis == "Possible Brute Force Attack"
    ).count()

    sql_injection = db.query(Analysis).filter(
        Analysis.analysis == "Possible SQL Injection"
    ).count()

    xss = db.query(Analysis).filter(
        Analysis.analysis == "Possible Cross Site Scripting (XSS)"
    ).count()

    port_scan = db.query(Analysis).filter(
        Analysis.analysis == "Possible Port Scanning Activity"
    ).count()

    admin_attack = db.query(Analysis).filter(
        Analysis.analysis == "Possible Admin Account Attack"
    ).count()

    return {
        "brute_force": brute_force,
        "sql_injection": sql_injection,
        "xss": xss,
        "port_scan": port_scan,
        "admin_attack": admin_attack
    }
@router.get("/latest-alerts")
def latest_alerts():

    db = SessionLocal()

    alerts = db.query(Alert)\
        .order_by(Alert.id.desc())\
        .limit(5)\
        .all()

    return alerts
@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int):

    db = SessionLocal()

    alert = db.query(Alert).filter(
        Alert.id == alert_id
    ).first()

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    db.delete(alert)
    db.commit()

    return {
        "message": "Alert deleted successfully"
    }
@router.put("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int):

    db = SessionLocal()

    alert = db.query(Alert).filter(
        Alert.id == alert_id
    ).first()

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    alert.status = "Resolved"

    db.commit()

    return {
        "message": "Alert resolved successfully"
    }
