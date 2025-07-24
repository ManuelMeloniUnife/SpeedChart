#!/usr/bin/env python3
"""
Migrazione per aggiornare le foreign key con CASCADE
"""

import sqlite3
import shutil
import os
from datetime import datetime

def migrate_database():
    """Migra il database per aggiungere CASCADE alle foreign key"""
    
    db_path = 'data/speedchart.db'
    backup_path = f'data/speedchart_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print(f"Iniziando migrazione del database...")
    
    # Backup del database
    print(f"Creando backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prima controlliamo cosa c'è nel database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tabelle presenti: {[t[0] for t in tables]}")
        
        # Disabilita foreign key constraints per la migrazione
        cursor.execute("PRAGMA foreign_keys=OFF;")
        
        # Inizia la transazione
        cursor.execute("BEGIN TRANSACTION;")
        
        # 1. Ricreiamo la tabella race_spingitore con le foreign key corrette
        print("Ricreando tabella race_spingitore...")
        
        # Salva i dati esistenti
        cursor.execute("SELECT * FROM race_spingitore;")
        existing_data = cursor.fetchall()
        print(f"Trovati {len(existing_data)} record in race_spingitore")
        
        # Elimina la tabella esistente
        cursor.execute("DROP TABLE IF EXISTS race_spingitore;")
        
        # Ricrea la tabella con le foreign key corrette
        cursor.execute("""
        CREATE TABLE race_spingitore (
            id INTEGER PRIMARY KEY,
            race_id INTEGER NOT NULL,
            spingitore_id INTEGER NOT NULL,
            ordine_esecuzione INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (race_id) REFERENCES race (id) ON DELETE CASCADE,
            FOREIGN KEY (spingitore_id) REFERENCES spingitore (id) ON DELETE CASCADE
        );
        """)
        
        # Reinserisce i dati
        if existing_data:
            cursor.executemany(
                "INSERT INTO race_spingitore (id, race_id, spingitore_id, ordine_esecuzione) VALUES (?, ?, ?, ?)",
                existing_data
            )
            print(f"Reinseriti {len(existing_data)} record in race_spingitore")
        
        # 2. Ricreiamo la tabella data_point con foreign key corretta
        print("Ricreando tabella data_point...")
        
        # Salva i dati esistenti
        cursor.execute("SELECT * FROM data_point;")
        existing_data_points = cursor.fetchall()
        print(f"Trovati {len(existing_data_points)} record in data_point")
        
        # Elimina la tabella esistente
        cursor.execute("DROP TABLE IF EXISTS data_point;")
        
        # Ricrea la tabella con foreign key corretta
        cursor.execute("""
        CREATE TABLE data_point (
            id INTEGER PRIMARY KEY,
            race_id INTEGER NOT NULL,
            distance REAL NOT NULL,
            speed REAL NOT NULL,
            acceleration REAL,
            time REAL,
            FOREIGN KEY (race_id) REFERENCES race (id) ON DELETE CASCADE
        );
        """)
        
        # Reinserisce i dati
        if existing_data_points:
            cursor.executemany(
                "INSERT INTO data_point (id, race_id, distance, speed, acceleration, time) VALUES (?, ?, ?, ?, ?, ?)",
                existing_data_points
            )
            print(f"Reinseriti {len(existing_data_points)} record in data_point")
        
        # Commit della transazione
        cursor.execute("COMMIT;")
        
        # Riabilita foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON;")
        
        # Verifica l'integrità
        cursor.execute("PRAGMA foreign_key_check;")
        fk_errors = cursor.fetchall()
        
        if fk_errors:
            print(f"ERRORI di foreign key trovati: {fk_errors}")
            raise Exception("Errori di integrità delle foreign key")
        
        print("Migrazione completata con successo!")
        print(f"Backup salvato in: {backup_path}")
        
    except Exception as e:
        print(f"ERRORE durante la migrazione: {e}")
        cursor.execute("ROLLBACK;")
        
        # Ripristina il backup
        print("Ripristinando il backup...")
        shutil.copy2(backup_path, db_path)
        raise
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
