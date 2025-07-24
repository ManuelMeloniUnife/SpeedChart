#!/usr/bin/env python3
"""
Script di migrazione per SpeedChart v1.1
Migra da race_spingitore table a RaceSpingitore model con ordine
"""

import sqlite3
import os
from app import create_app
from models import db, RaceSpingitore

def migrate_database():
    """Migra il database alla nuova struttura con ordine spingitori"""
    
    app = create_app()
    
    with app.app_context():
        # Controlla se esiste già la nuova struttura
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'race_spingitore' in tables:
            # Controlla se ha già la colonna ordine_esecuzione
            columns = [col['name'] for col in inspector.get_columns('race_spingitore')]
            
            if 'ordine_esecuzione' not in columns:
                print("Migrazione necessaria...")
                
                # Backup dei dati esistenti
                connection = db.engine.raw_connection()
                cursor = connection.cursor()
                
                try:
                    # Leggi i dati esistenti
                    cursor.execute("SELECT race_id, spingitore_id FROM race_spingitore")
                    existing_data = cursor.fetchall()
                    
                    print(f"Trovate {len(existing_data)} associazioni esistenti")
                    
                    # Drop della vecchia tabella
                    cursor.execute("DROP TABLE race_spingitore")
                    connection.commit()
                    
                    # Crea la nuova struttura
                    db.create_all()
                    
                    # Inserisci i dati con ordine di default (1 per tutti)
                    for race_id, spingitore_id in existing_data:
                        race_spingitore = RaceSpingitore(
                            race_id=race_id,
                            spingitore_id=spingitore_id,
                            ordine_esecuzione=1  # Ordine di default per dati esistenti
                        )
                        db.session.add(race_spingitore)
                    
                    db.session.commit()
                    print(f"Migrazione completata! Inserite {len(existing_data)} associazioni con ordine di default.")
                    
                except Exception as e:
                    print(f"Errore durante la migrazione: {e}")
                    connection.rollback()
                    raise
                finally:
                    connection.close()
            else:
                print("Database già aggiornato!")
        else:
            # Prima installazione
            print("Creazione database...")
            db.create_all()
            print("Database creato con successo!")

if __name__ == '__main__':
    migrate_database()
