"""
Configuration settings for Cahier de Texte application
"""
import os

# Get project root directory (go up from src/utils/ to project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Database path
DB_PATH = os.path.join(BASE_DIR, 'data', 'cahier_texte.db')

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
