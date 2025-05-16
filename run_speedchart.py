import webbrowser
import threading
import time
import os
from app import create_app

def open_browser():
    """Apre il browser alla pagina dell'applicazione dopo un piccolo delay"""
    time.sleep(1.5)  # Attende che l'app Flask si avvii
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("Avvio SpeedChart...")
    # Assicurati che la cartella data esista
    os.makedirs('data', exist_ok=True)
    
    # Crea l'app
    app = create_app()
    
    # Avvia il browser in un thread separato
    threading.Thread(target=open_browser).start()
    
    # Avvia l'app Flask con modalità di debug disabilitata
    app.run(debug=False, use_reloader=False)