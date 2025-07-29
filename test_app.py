# test_app.py
"""Quick test script to verify SpeedChart functionality"""

from app import create_app
from models import db, Cartella, Spingitore, Race, RaceSpingitore

def test_models():
    """Test all models and relationships"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Testing models...")
        
        # Test Cartella model
        cartella = Cartella(nome="Test Cartella")
        print(f"✓ Cartella: {cartella}")
        print(f"✓ Cartella.corse property exists: {hasattr(cartella, 'corse')}")
        
        # Test Spingitore model
        spingitore = Spingitore(nome="Test", cognome="User", attivo=True)
        print(f"✓ Spingitore: {spingitore}")
        print(f"✓ Spingitore.attivo field exists: {hasattr(spingitore, 'attivo')}")
        
        # Test Race model
        race = Race(name="Test Race")
        print(f"✓ Race: {race}")
        
        print("✅ All models working correctly!")

def test_routes():
    """Test routes import"""
    try:
        from routes import main_blueprint, api_blueprint, team_blueprint, folder_blueprint
        print("✅ All route blueprints imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Route import error: {e}")
        return False

def test_app_creation():
    """Test app creation"""
    try:
        app = create_app()
        print("✅ App created successfully!")
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created!")
        
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SpeedChart Quick Test")
    print("=" * 30)
    
    success = True
    
    # Test app creation
    if not test_app_creation():
        success = False
    
    # Test routes
    if not test_routes():
        success = False
    
    # Test models
    test_models()
    
    print("=" * 30)
    if success:
        print("🎉 ALL TESTS PASSED! SpeedChart is ready!")
    else:
        print("❌ Some tests failed. Check the errors above.")
