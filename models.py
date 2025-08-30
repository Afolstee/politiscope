from app import db
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False)
    politician_name = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    comments = db.Column(db.Text)
    helpful = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback {self.politician_name}: {self.rating}/5>'

class AnalysisSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    politician_name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100))
    analysis_types = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='started')
    
    def __repr__(self):
        return f'<AnalysisSession {self.politician_name}: {self.status}>'
