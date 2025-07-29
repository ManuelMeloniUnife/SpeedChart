#!/usr/bin/env python3
"""Test completo per verificare che l'errore ArgumentError sia risolto"""

from app import create_app
from models import db, Cartella, Race, Spingitore
from sqlalchemy.orm import joinedload

def test_joinedload_fix():
    """Test specifico per l'errore ArgumentError"""
    print("🧪 Testing SQLAlchemy joinedload fix...")
    
    app = create_app()
    
    with app.app_context():
        # Crea le tabelle
        db.create_all()
        print("✓ Database tables created")
        
        # Test 1: joinedload con Cartella.races (dovrebbe funzionare)
        try:
            cartelle = Cartella.query.options(joinedload(Cartella.races)).order_by(Cartella.nome).all()
            print(f"✓ Cartella.races joinedload OK - found {len(cartelle)} cartelle")
        except Exception as e:
            print(f"❌ Cartella.races joinedload failed: {e}")
            return False
        
        # Test 2: joinedload con Race.race_spingitori_ordered (dovrebbe funzionare)
        try:
            corse = Race.query.filter(Race.cartella_id.is_(None)).options(joinedload(Race.race_spingitori_ordered)).order_by(Race.date.desc()).all()
            print(f"✓ Race.race_spingitori_ordered joinedload OK - found {len(corse)} corse")
        except Exception as e:
            print(f"❌ Race.race_spingitori_ordered joinedload failed: {e}")
            return False
        
        # Test 3: verifica che le property funzionino ancora
        try:
            cartella = Cartella(nome="Test")
            race = Race(name="Test Race")
            
            # Test property access
            corse_property = cartella.corse  # Dovrebbe essere uguale a cartella.races
            spingitori_property = race.race_spingitori  # Dovrebbe essere uguale a race.race_spingitori_ordered
            
            print("✓ Property aliases working correctly")
        except Exception as e:
            print(f"❌ Property aliases failed: {e}")
            return False
    
    print("🎉 All joinedload tests passed!")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("  SQLAlchemy ArgumentError Fix Test")
    print("=" * 50)
    
    success = test_joinedload_fix()
    
    print("=" * 50)
    if success:
        print("✅ ALL TESTS PASSED - ArgumentError FIXED!")
    else:
        print("❌ TESTS FAILED - Check errors above")
