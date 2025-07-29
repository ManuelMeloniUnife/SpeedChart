# app.py
from flask import Flask
from flask_migrate import Migrate
from models import db
from dash_app import init_dashboard
from comparison_dash import init_comparison_dashboard
from config import config
import os

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize Dash dashboards
    init_dashboard(app)
    init_comparison_dashboard(app)
    
    # Register blueprints
    from routes import main_blueprint, api_blueprint, team_blueprint, folder_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(team_blueprint)
    app.register_blueprint(folder_blueprint)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)