# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from models import db, Race, DataPoint, Spingitore
from utils.file_parser import parse_race_file
import os
from dash_app import init_dashboard
from comparison_dash import init_comparison_dashboard

def create_app():
    app = Flask(__name__)
    
    # Percorso assoluto alla cartella data
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Assicurati che esista la cartella per il logo
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img'), exist_ok=True)
    
    # Percorso assoluto al database
    database_path = os.path.join(data_dir, 'speedchart.db')
    
    # Stampa per debug
    print(f"Using database at: {database_path}")
    
    # Configurazioni
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Inizializza il database
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Inizializza le dashboard Dash
    init_dashboard(app)
    init_comparison_dashboard(app)
    
    # Registra i blueprint
    from routes import main
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)