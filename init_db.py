# init_db.py
"""Database initialization script for SpeedChart"""

from app import create_app
from models import db, Spingitore
from datetime import datetime

def main():
    """Initialize the database with sample data"""
    app = create_app()

    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Add sample drivers (spingitori)
        print("Adding sample data...")
        
        spingitori = [
            Spingitore(nome="Mario", cognome="Rossi", ruolo="Capitano", attivo=True),
            Spingitore(nome="Luigi", cognome="Verdi", ruolo="Spingitore principale", attivo=True),
            Spingitore(nome="Giovanni", cognome="Bianchi", ruolo="Spingitore di riserva", attivo=True),
            Spingitore(nome="Paolo", cognome="Neri", ruolo="", attivo=False)
        ]
        
        for spingitore in spingitori:
            db.session.add(spingitore)
        
        db.session.commit()
        
        print(f"Added {len(spingitori)} sample spingitori")
        
        # Verify tables creation
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    main()