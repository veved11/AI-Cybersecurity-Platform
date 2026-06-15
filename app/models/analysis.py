from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    text = Column(String, nullable=False)

    risk = Column(String, nullable=False)

    analysis = Column(String, nullable=False)