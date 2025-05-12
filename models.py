# models.py (aggiornato)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Spingitore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100))
    ruolo = db.Column(db.String(100))
    attivo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione con Race
    corse = db.relationship('Race', backref='spingitore', lazy=True)
    
    def __repr__(self):
        return f"Spingitore('{self.nome} {self.cognome}')"
    
    def nome_completo(self):
        if self.cognome:
            return f"{self.nome} {self.cognome}"
        return self.nome

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    spingitore_id = db.Column(db.Integer, db.ForeignKey('spingitore.id'))
    wheel_circumference = db.Column(db.Float, default=1.52)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione con DataPoint
    data_points = db.relationship('DataPoint', backref='race', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Race('{self.name}', '{self.date}')"

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    acceleration = db.Column(db.Float)
    time = db.Column(db.Float)
    
    def __repr__(self):
        return f"DataPoint(distance={self.distance}m, speed={self.speed}km/h)"