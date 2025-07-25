# models.py
# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Cartella(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    colore = db.Column(db.String(7), default='#007bff')  # Colore esadecimale per personalizzazione
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campo per cartelle annidate
    parent_id = db.Column(db.Integer, db.ForeignKey('cartella.id'), nullable=True)
    
    # Relazioni
    parent = db.relationship('Cartella', remote_side=[id], backref='subcartelle')
    races = db.relationship('Race', backref='cartella', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Cartella('{self.nome}')"
    
    @property
    def full_path(self):
        """Restituisce il percorso completo della cartella"""
        if self.parent:
            return f"{self.parent.full_path} > {self.nome}"
        return self.nome
    
    @property
    def level(self):
        """Restituisce il livello di annidamento (0 = radice)"""
        if self.parent:
            return self.parent.level + 1
        return 0
    
    def get_all_races_recursive(self):
        """Ottiene tutte le corse di questa cartella e delle sue sottocartelle"""
        races = list(self.races)
        for subcartella in self.subcartelle:
            races.extend(subcartella.get_all_races_recursive())
        return races
    
    @staticmethod
    def get_default_folder():
        """Ottiene o crea la cartella predefinita 'Generale'"""
        cartella_generale = Cartella.query.filter_by(nome='Generale', parent_id=None).first()
        if not cartella_generale:
            cartella_generale = Cartella(nome='Generale', colore='#6c757d', parent_id=None)
            db.session.add(cartella_generale)
            db.session.commit()
        return cartella_generale

# Modello per la relazione many-to-many con ordine di esecuzione
class RaceSpingitore(db.Model):
    __tablename__ = 'race_spingitore'
    
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id', ondelete='CASCADE'), nullable=False)
    spingitore_id = db.Column(db.Integer, db.ForeignKey('spingitore.id', ondelete='CASCADE'), nullable=False)
    ordine_esecuzione = db.Column(db.Integer, nullable=False, default=1)  # Ordine nella staffetta
    
    # Relazioni
    race = db.relationship('Race', backref=db.backref('race_spingitori_ordered', cascade='all, delete-orphan'))
    spingitore = db.relationship('Spingitore', backref=db.backref('spingitore_races_ordered', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f"RaceSpingitore(race_id={self.race_id}, spingitore_id={self.spingitore_id}, ordine={self.ordine_esecuzione})"

class Spingitore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100))
    ruolo = db.Column(db.String(20), nullable=False, default='Spingitore')  # 'Pilota' o 'Spingitore'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Spingitore('{self.nome} {self.cognome}', ruolo='{self.ruolo}')"
    
    def nome_completo(self):
        if self.cognome:
            return f"{self.nome} {self.cognome}"
        return self.nome
    
    def is_pilota(self):
        """Ritorna True se questo elemento è un pilota"""
        return self.ruolo == 'Pilota'
    
    def is_spingitore(self):
        """Ritorna True se questo elemento è uno spingitore"""
        return self.ruolo == 'Spingitore'

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    wheel_circumference = db.Column(db.Float, default=1.52)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione con cartella
    cartella_id = db.Column(db.Integer, db.ForeignKey('cartella.id'), nullable=True)
    
    # Relazione con DataPoint
    data_points = db.relationship('DataPoint', backref='race', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Race('{self.name}', '{self.date}')"
    
    # Helper per ottenere pilota e spingitori separatamente
    def get_pilota(self):
        """Ritorna il pilota (ordine_esecuzione = 0)"""
        return db.session.query(Spingitore).join(RaceSpingitore)\
                         .filter(RaceSpingitore.race_id == self.id)\
                         .filter(RaceSpingitore.ordine_esecuzione == 0)\
                         .first()
    
    def get_spingitori_only(self):
        """Ritorna solo gli spingitori (ordine_esecuzione > 0) ordinati"""
        return db.session.query(Spingitore).join(RaceSpingitore)\
                         .filter(RaceSpingitore.race_id == self.id)\
                         .filter(RaceSpingitore.ordine_esecuzione > 0)\
                         .order_by(RaceSpingitore.ordine_esecuzione).all()
    
    def get_all_members_ordered(self):
        """Ritorna tutti i membri (pilota + spingitori) ordinati per ordine di esecuzione"""
        return db.session.query(Spingitore).join(RaceSpingitore)\
                         .filter(RaceSpingitore.race_id == self.id)\
                         .order_by(RaceSpingitore.ordine_esecuzione).all()
    
    def get_pilota_name(self):
        """Ritorna il nome del pilota"""
        pilota = self.get_pilota()
        return pilota.nome_completo() if pilota else "N/A"
    
    def get_spingitori_names(self):
        """Ritorna i nomi degli spingitori (solo spingitori, non pilota) come stringa separata da virgole"""
        spingitori = self.get_spingitori_only()
        return ", ".join([s.nome_completo() for s in spingitori]) if spingitori else "Nessuno"
    
    def get_all_names(self):
        """Ritorna tutti i nomi (pilota + spingitori) come stringa separata da virgole - per compatibilità"""
        tutti_membri = self.get_all_members_ordered()
        return ", ".join([s.nome_completo() for s in tutti_membri])
    
    # Proprietà per compatibilità con il codice esistente
    @property
    def spingitori(self):
        """Proprietà per ottenere tutti i membri (per compatibilità)"""
        return self.get_all_members_ordered()

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id', ondelete='CASCADE'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    acceleration = db.Column(db.Float)
    time = db.Column(db.Float)
    
    def __repr__(self):
        return f"DataPoint(distance={self.distance}m, speed={self.speed}km/h)"