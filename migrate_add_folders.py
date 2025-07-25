#!/usr/bin/env python3
"""
Migrazione per aggiungere il sistema di cartelle
"""

import sqlite3
import shutil
import os
from datetime import datetime

def migrate_add_folders():
    """Migra il database per aggiungere il sistema di cartelle"""
    
    db_path = 'data/speedchart.db'
    backup_path = f'data/speedchart_backup_folders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print(f"Iniziando migrazione per aggiungere cartelle...")
    
    # Backup del database
    print(f"Creando backup: {backup_path}")
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Disabilita foreign key constraints per la migrazione
        cursor.execute("PRAGMA foreign_keys=OFF;")
        
        # Inizia la transazione
        cursor.execute("BEGIN TRANSACTION;")
        
        # 1. Crea la tabella cartella
        print("Creando tabella cartella...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cartella (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            colore VARCHAR(7) DEFAULT '#007bff',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 2. Crea la cartella predefinita "Generale"
        print("Creando cartella predefinita 'Generale'...")
        cursor.execute("""
        INSERT OR IGNORE INTO cartella (nome, colore) 
        VALUES ('Generale', '#6c757d');
        """)
        
        # 3. Aggiungi colonna cartella_id alla tabella race
        print("Aggiungendo colonna cartella_id alla tabella race...")
        
        # Controlla se la colonna esiste già
        cursor.execute("PRAGMA table_info(race);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'cartella_id' not in columns:
            cursor.execute("ALTER TABLE race ADD COLUMN cartella_id INTEGER;")
            
            # Assegna tutte le corse esistenti alla cartella "Generale"
            cursor.execute("""
            UPDATE race 
            SET cartella_id = (SELECT id FROM cartella WHERE nome = 'Generale')
            WHERE cartella_id IS NULL;
            """)
            print("Tutte le corse esistenti sono state assegnate alla cartella 'Generale'")
        else:
            print("Colonna cartella_id già presente")
        
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
        
        print("Migrazione cartelle completata con successo!")
        print(f"Backup salvato in: {backup_path}")
        
        # Mostra statistiche
        cursor.execute("SELECT COUNT(*) FROM cartella;")
        num_cartelle = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM race;")
        num_corse = cursor.fetchone()[0]
        
        print(f"Cartelle presenti: {num_cartelle}")
        print(f"Corse presenti: {num_corse}")
        
    except Exception as e:
        print(f"ERRORE durante la migrazione: {e}")
        cursor.execute("ROLLBACK;")
        
        # Ripristina il backup se esiste
        if os.path.exists(backup_path):
            print("Ripristinando il backup...")
            shutil.copy2(backup_path, db_path)
        raise
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_add_folders()
