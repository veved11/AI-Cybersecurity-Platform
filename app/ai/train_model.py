import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import joblib

data = {
    "text": [

        # Brute Force
        "failed login from admin",
        "multiple failed login attempts",
        "admin failed login",
        "authentication failed",
        "too many login attempts",
        "failed password for root",
        "user locked after login failures",
        "repeated login failures detected",
        "brute force attempt detected",
        "invalid credentials provided",

        # SQL Injection
        "select * from users",
        "drop table users",
        "union select password",
        "sql injection detected",
        "or 1=1 query found",
        "database attack attempt",
        "malicious sql statement",
        "insert into users values",
        "delete from accounts",
        "information_schema query",

        # XSS
        "<script>alert('xss')</script>",
        "xss attack detected",
        "javascript injection",
        "cross site scripting attempt",
        "<script>malicious code</script>",
        "client side script injection",
        "stored xss payload",
        "reflected xss attack",
        "browser script execution",
        "html injection detected",

        # Port Scan
        "nmap scan detected",
        "port scan detected",
        "network scanning",
        "multiple ports probed",
        "host discovery scan",
        "service enumeration attempt",
        "tcp scan activity",
        "udp scan activity",
        "aggressive network scan",
        "suspicious port probing",

        # Normal
        "user logged in successfully",
        "system running normally",
        "file uploaded successfully",
        "backup completed",
        "service started successfully",
        "application deployed",
        "database connection established",
        "user account created",
        "configuration loaded",
        "routine maintenance completed"

    ],

    "label": [

        "Brute Force","Brute Force","Brute Force","Brute Force","Brute Force",
        "Brute Force","Brute Force","Brute Force","Brute Force","Brute Force",

        "SQL Injection","SQL Injection","SQL Injection","SQL Injection","SQL Injection",
        "SQL Injection","SQL Injection","SQL Injection","SQL Injection","SQL Injection",

        "XSS","XSS","XSS","XSS","XSS",
        "XSS","XSS","XSS","XSS","XSS",

        "Port Scan","Port Scan","Port Scan","Port Scan","Port Scan",
        "Port Scan","Port Scan","Port Scan","Port Scan","Port Scan",

        "Normal","Normal","Normal","Normal","Normal",
        "Normal","Normal","Normal","Normal","Normal"
    ]
}

df = pd.DataFrame(data)

model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression())
])

model.fit(df["text"], df["label"])

joblib.dump(model, "app/ai/model.pkl")

print("Model trained successfully")