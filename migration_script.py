# migration_script.py
from app import create_app
from models import db, Race, Spingitore, race_spingitore

app = create_app()

with app.app_context():
    # Crea la tabella di associazione
    if not db.engine.has_table('race_spingitore'):
        db.create_all()
    
    # Migra i dati esistenti dalla relazione one-to-many alla many-to-many
    races = Race.query.all()
    for race in races:
        # Ottieni lo spingitore vecchio associato
        spingitore_id = getattr(race, 'spingitore_id', None)
        if spingitore_id:
            spingitore = Spingitore.query.get(spingitore_id)
            if spingitore:
                # Aggiungi lo spingitore alla relazione many-to-many
                race.spingitori.append(spingitore)
    
    # Elimina la colonna vecchia se esiste
    if 'spingitore_id' in [c.name for c in Race.__table__.columns]:
        db.engine.execute('ALTER TABLE race DROP COLUMN spingitore_id')
    
    db.session.commit()