# routes/__init__.py
from .main import main_blueprint
from .api import api_blueprint  
from .team_management import team_blueprint
from .folder_management import folder_blueprint

__all__ = ['main_blueprint', 'api_blueprint', 'team_blueprint', 'folder_blueprint']
