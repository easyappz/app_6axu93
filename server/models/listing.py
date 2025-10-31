from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from server.db.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    image_path = Column(String(1000), nullable=True)  # relative to /media/
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
