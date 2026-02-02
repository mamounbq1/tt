"""
Configuration module for Cahier de Texte application
Defines global constants and paths
"""

import os

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database configuration
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'cahier_texte.db')

# Logging configuration
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

# Application constants
APP_NAME = "Système de Gestion Scolaire - Cahier de Texte"
APP_VERSION = "2.0.0"

# UI Constants
WINDOW_TITLE = APP_NAME
MIN_WIDTH = 800
MIN_HEIGHT = 600

# Time constants
DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
MORNING_START = '08:30'
MORNING_END = '12:30'
LUNCH_START = '12:30'
LUNCH_END = '14:30'
AFTERNOON_START = '14:30'
AFTERNOON_END = '18:30'

# Time slots definition
TIME_SLOTS = [
    ('08:30', '09:30', 'morning'),
    ('09:30', '10:30', 'morning'),
    ('10:30', '11:30', 'morning'),
    ('11:30', '12:30', 'morning'),
    ('12:30', '14:30', 'lunch'),
    ('14:30', '15:30', 'afternoon'),
    ('15:30', '16:30', 'afternoon'),
    ('16:30', '17:30', 'afternoon'),
    ('17:30', '18:30', 'afternoon'),
]

# Colors
COLORS = {
    'primary': '#1976D2',
    'secondary': '#424242',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'info': '#2196F3',
    'light': '#F5F5F5',
    'dark': '#212121'
}
