#!/usr/bin/env python3
"""
Script di migrazione per aggiungere il supporto alle cartelle annidate
Aggiunge la colonna parent_id alla tabella cartella
"""

import sqlite3
import os
from datetime import datetime

def migrate_nested_folders():
    """Aggiunge il supporto per cartelle annidate"""
    
    # Percorso del database
    db_path = os.path.join('data', 'speedchart.db')
    
    if not os.path.exists(db_path):
        print("❌ Database non trovato!")
        return False
    
    # Backup del database
    backup_name = f"speedchart_backup_nested_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join('data', backup_name)
    
    try:
        print(f"📦 Creazione backup: {backup_name}")
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup creato: {backup_path}")
        
        # Connessione al database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se la colonna parent_id esiste già
        cursor.execute("PRAGMA table_info(cartella)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'parent_id' in columns:
            print("✅ La colonna parent_id esiste già!")
            conn.close()
            return True
        
        print("🔧 Aggiunta colonna parent_id...")
        
        # Aggiungi la colonna parent_id
        cursor.execute("""
            ALTER TABLE cartella 
            ADD COLUMN parent_id INTEGER REFERENCES cartella(id)
        """)
        
        # Commit delle modifiche
        conn.commit()
        
        print("✅ Migrazione completata con successo!")
        print("📁 La colonna parent_id è stata aggiunta alla tabella cartella")
        
        # Verifica finale
        cursor.execute("PRAGMA table_info(cartella)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Colonne attuali: {', '.join(columns)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la migrazione: {e}")
        
        # Ripristina il backup in caso di errore
        if os.path.exists(backup_path):
            print("🔄 Ripristino del backup...")
            shutil.copy2(backup_path, db_path)
            print("✅ Backup ripristinato")
        
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 MIGRAZIONE CARTELLE ANNIDATE")
    print("=" * 50)
    
    success = migrate_nested_folders()
    
    if success:
        print("\n🎉 Migrazione completata!")
        print("🔄 Riavvia l'applicazione per utilizzare le nuove funzionalità")
    else:
        print("\n💥 Migrazione fallita!")
        print("🔍 Controlla i log di errore sopra")
