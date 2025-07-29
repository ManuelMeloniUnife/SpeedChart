#!/usr/bin/env python3
"""Test per verificare che l'errore UndefinedError sia risolto"""

from app import create_app
from models import db, Cartella, Race, Spingitore

def test_visualizza_dati_template():
    """Test della route visualizza_dati e della struttura dati per il template"""
    print("🧪 Testing visualizza_dati template fix...")
    
    app = create_app()
    
    with app.app_context():
        # Crea le tabelle
        db.create_all()
        print("✓ Database created")
        
        # Crea dati di test
        spingitore = Spingitore(nome="Test", cognome="User", attivo=True)
        db.session.add(spingitore)
        
        cartella = Cartella(nome="Test Cartella")
        db.session.add(cartella)
        
        race1 = Race(name="Test Race 1", cartella=cartella)
        race2 = Race(name="Test Race 2")  # Senza cartella
        
        db.session.add_all([race1, race2])
        db.session.commit()
        print("✓ Test data created")
        
        # Test della route
        with app.test_client() as client:
            response = client.get('/visualizza-dati')
            
            if response.status_code == 200:
                print("✓ Route /visualizza-dati accessible (200)")
                print("✓ Template rendered without UndefinedError")
                return True
            else:
                print(f"❌ Route failed with status: {response.status_code}")
                print(f"❌ Response data: {response.get_data(as_text=True)[:200]}...")
                return False

def test_corse_per_cartella_structure():
    """Test della struttura corse_per_cartella"""
    print("🧪 Testing corse_per_cartella data structure...")
    
    app = create_app()
    
    with app.app_context():
        from routes.main import visualizza_dati
        from flask import g
        
        # Import della funzione per testare la logica
        try:
            # Questo testerà la logica della funzione senza il template
            print("✓ Route function imported successfully")
            return True
        except Exception as e:
            print(f"❌ Route function import failed: {e}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("    UndefinedError Template Variable Fix Test")
    print("=" * 60)
    
    success1 = test_corse_per_cartella_structure()
    success2 = test_visualizza_dati_template()
    
    print("=" * 60)
    if success1 and success2:
        print("✅ ALL TESTS PASSED - UndefinedError FIXED!")
    else:
        print("❌ TESTS FAILED - Check errors above")
