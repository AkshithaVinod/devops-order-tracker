from app.database import db
from datetime import datetime

class Order(db.Model):
    """Order model with database persistence"""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    product = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'product': self.product,
            'quantity': self.quantity,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Order {self.id}: {self.customer_name}>'