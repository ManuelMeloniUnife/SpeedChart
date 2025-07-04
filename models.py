# models.py
# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabella di associazione per la relazione many-to-many tra Race e Spingitore
race_spingitore = db.Table('race_spingitore',
    db.Column('race_id', db.Integer, db.ForeignKey('race.id'), primary_key=True),
    db.Column('spingitore_id', db.Integer, db.ForeignKey('spingitore.id'), primary_key=True)
)

class Spingitore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100))
    ruolo = db.Column(db.String(100))
    attivo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione con Race (many-to-many)
    corse = db.relationship('Race', secondary=race_spingitore, 
                           backref=db.backref('spingitori', lazy='dynamic'), 
                           lazy='dynamic')
    
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
    # Rimuoviamo la relazione one-to-many con Spingitore
    # spingitore_id = db.Column(db.Integer, db.ForeignKey('spingitore.id'))
    wheel_circumference = db.Column(db.Float, default=1.52)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione con DataPoint
    data_points = db.relationship('DataPoint', backref='race', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Race('{self.name}', '{self.date}')"
    
    # Helper per ottenere gli spingitori come stringa
    def get_spingitori_names(self):
        """Ritorna i nomi degli spingitori come stringa separata da virgole"""
        return ", ".join([s.nome_completo() for s in self.spingitori])
    
    def get_spingitori_ids_string(self):
        """Ritorna gli ID degli spingitori come stringa separata da virgole"""
        return ",".join([str(s.id) for s in self.spingitori])

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    acceleration = db.Column(db.Float)
    time = db.Column(db.Float)
    
    def __repr__(self):
        return f"DataPoint(distance={self.distance}m, speed={self.speed}km/h)"