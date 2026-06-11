from datetime import datetime
from typing import Optional, Dict, Any
from ..core.database import db


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), index=True)
    region = db.Column(db.String(100), index=True)
    office = db.Column(db.String(100), index=True)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(50))
    room = db.Column(db.String(50))
    full_path = db.Column(db.String(500), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Location {self.full_path}>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'country': self.country,
            'region': self.region,
            'office': self.office,
            'building': self.building,
            'floor': self.floor,
            'room': self.room,
            'full_path': self.full_path,
            'status': self.status
        }
