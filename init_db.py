# init_db.py
import os
from app import create_app
from models import db

# Crea l'applicazione
app = create_app()

# Verifica e crea la cartella data se non esiste
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Stampa il percorso del database per debug
database_path = app.config.get('SQLALCHEMY_DATABASE_URI', '')
print(f"Database path: {database_path}")

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    
    # Verifica che le tabelle siano state create
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")