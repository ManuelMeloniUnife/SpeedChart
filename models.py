# models.py
# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Modello per la relazione many-to-many con ordine di esecuzione
class RaceSpingitore(db.Model):
    __tablename__ = 'race_spingitore'
    
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    spingitore_id = db.Column(db.Integer, db.ForeignKey('spingitore.id'), nullable=False)
    ordine_esecuzione = db.Column(db.Integer, nullable=False, default=1)  # Ordine nella staffetta
    
    # Relazioni
    race = db.relationship('Race', backref='race_spingitori_ordered')
    spingitore = db.relationship('Spingitore', backref='spingitore_races_ordered')
    
    def __repr__(self):
        return f"RaceSpingitore(race_id={self.race_id}, spingitore_id={self.spingitore_id}, ordine={self.ordine_esecuzione})"

class Spingitore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100))
    ruolo = db.Column(db.String(100))
    attivo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    wheel_circumference = db.Column(db.Float, default=1.52)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione con DataPoint
    data_points = db.relationship('DataPoint', backref='race', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Race('{self.name}', '{self.date}')"
    
    # Helper per ottenere gli spingitori ordinati
    def get_spingitori_ordered(self):
        """Ritorna gli spingitori ordinati per ordine di esecuzione"""
        return db.session.query(Spingitore).join(RaceSpingitore)\
                         .filter(RaceSpingitore.race_id == self.id)\
                         .order_by(RaceSpingitore.ordine_esecuzione).all()
    
    def get_spingitori_names(self):
        """Ritorna i nomi degli spingitori ordinati come stringa separata da virgole"""
        spingitori_ordinati = self.get_spingitori_ordered()
        return ", ".join([s.nome_completo() for s in spingitori_ordinati])
    
    def get_spingitori_ids_string(self):
        """Ritorna gli ID degli spingitori ordinati come stringa separata da virgole"""
        spingitori_ordinati = self.get_spingitori_ordered()
        return ",".join([str(s.id) for s in spingitori_ordinati])
    
    # Proprietà per compatibilità con il codice esistente
    @property
    def spingitori(self):
        """Proprietà per ottenere gli spingitori (per compatibilità)"""
        return self.get_spingitori_ordered()

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    acceleration = db.Column(db.Float)
    time = db.Column(db.Float)
    
    def __repr__(self):
        return f"DataPoint(distance={self.distance}m, speed={self.speed}km/h)"