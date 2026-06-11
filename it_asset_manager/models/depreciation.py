from datetime import datetime, date
from typing import Optional, Dict, Any
from ..core.database import db


DEPRECIATION_METHODS = ['straight_line', 'declining_balance']


class AssetDepreciation(db.Model):
    __tablename__ = 'asset_depreciation'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False, unique=True, index=True)
    method = db.Column(db.String(30), nullable=False, default='straight_line')
    purchase_cost = db.Column(db.Float, nullable=False)
    salvage_value = db.Column(db.Float, default=0.0)
    useful_life_years = db.Column(db.Integer, nullable=False)
    current_book_value = db.Column(db.Float, nullable=False)
    accumulated_depreciation = db.Column(db.Float, default=0.0)
    last_depreciation_date = db.Column(db.Date)
    purchase_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = db.relationship('Asset', backref=db.backref('depreciation', uselist=False))

    def __repr__(self):
        return f'<AssetDepreciation asset_id={self.asset_id}: {self.method}>'

    @property
    def depreciated_value(self) -> float:
        return self.purchase_cost - self.current_book_value

    @property
    def depreciation_percent(self) -> float:
        if self.purchase_cost <= 0:
            return 0.0
        return round((self.depreciated_value / self.purchase_cost) * 100, 1)

    def calculate_annual_depreciation(self) -> float:
        if self.method == 'straight_line':
            return (self.purchase_cost - self.salvage_value) / max(self.useful_life_years, 1)
        elif self.method == 'declining_balance':
            rate = 2.0 / max(self.useful_life_years, 1)
            return self.current_book_value * rate
        return 0.0

    def apply_depreciation(self) -> float:
        annual = self.calculate_annual_depreciation()
        monthly = annual / 12.0
        self.current_book_value = max(self.current_book_value - monthly, self.salvage_value)
        self.accumulated_depreciation = self.purchase_cost - self.current_book_value
        self.last_depreciation_date = date.today()
        return monthly

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'method': self.method,
            'purchase_cost': self.purchase_cost,
            'salvage_value': self.salvage_value,
            'useful_life_years': self.useful_life_years,
            'current_book_value': self.current_book_value,
            'accumulated_depreciation': self.accumulated_depreciation,
            'last_depreciation_date': self.last_depreciation_date.isoformat() if self.last_depreciation_date else None,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'depreciated_value': self.depreciated_value,
            'depreciation_percent': self.depreciation_percent,
            'annual_depreciation': self.calculate_annual_depreciation()
        }
