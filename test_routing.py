#!/usr/bin/env python3
"""Test URL routing per verificare che tutti i blueprint siano configurati correttamente"""

from app import create_app
from flask import url_for

def test_url_routing():
    """Test che tutti gli endpoint blueprint funzionino"""
    print("🧪 Testing URL routing with blueprints...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test main blueprint routes
            print("Testing main blueprint routes:")
            print(f"  ✓ main.index: {url_for('main.index')}")
            print(f"  ✓ main.upload: {url_for('main.upload')}")
            print(f"  ✓ main.visualizza_dati: {url_for('main.visualizza_dati')}")
            print(f"  ✓ main.compare: {url_for('main.compare')}")
            
            # Test team blueprint routes
            print("Testing team blueprint routes:")
            print(f"  ✓ team.gestione_team: {url_for('team.gestione_team')}")
            print(f"  ✓ team.aggiungi_spingitore: {url_for('team.aggiungi_spingitore')}")
            
            # Test folder blueprint routes
            print("Testing folder blueprint routes:")
            print(f"  ✓ folder.crea_cartella: {url_for('folder.crea_cartella')}")
            print(f"  ✓ folder.sposta_corsa: {url_for('folder.sposta_corsa')}")
            
            # Test API blueprint routes
            print("Testing API blueprint routes:")
            print(f"  ✓ api.get_races: {url_for('api.get_races')}")
            print(f"  ✓ api.get_spingitori: {url_for('api.get_spingitori')}")
            
            print("🎉 All URL routing tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ URL routing test failed: {e}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("    URL Routing & Blueprint Configuration Test")
    print("=" * 60)
    
    success = test_url_routing()
    
    print("=" * 60)
    if success:
        print("✅ ALL ROUTING TESTS PASSED - BuildError FIXED!")
    else:
        print("❌ ROUTING TESTS FAILED - Check errors above")
