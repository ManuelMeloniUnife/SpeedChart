from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from models import db, Race, DataPoint
from utils.file_parser import parse_race_file
import os
from dash_app import init_dashboard
from comparison_dash import init_comparison_dashboard

def create_app():
    app = Flask(__name__)
    
    # Configurazione
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/speedchart.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inizializza il database
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Crea la cartella data se non esiste
    os.makedirs('data', exist_ok=True)
    
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