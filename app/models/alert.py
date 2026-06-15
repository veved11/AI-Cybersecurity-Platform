from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    threat_type = Column(String, nullable=False)

    risk = Column(String, nullable=False)

    message = Column(String, nullable=False)
    status = Column(String, default="Open")
    