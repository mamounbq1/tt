"""
Database Manager for Cahier de Texte
Handles all database operations and schema management
"""

import sqlite3
import logging
import os
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, database_path):
        self.db_path = database_path
        self.connection = None
        self.ensure_database_exists()
        self.create_schema()
        self.populate_initial_data()
    
    def ensure_database_exists(self):
        """Create database directory and file if needed"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logging.info(f"Created database directory: {db_dir}")
        
        if not os.path.exists(self.db_path):
            open(self.db_path, 'a').close()
            logging.info(f"Created database file: {self.db_path}")
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_schema(self):
        """Create all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Teachers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Classes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                level TEXT,
                school_year TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Days table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_order INTEGER
            )
        """)
        
        # Time slots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                period TEXT NOT NULL,
                is_lunch BOOLEAN DEFAULT 0,
                display_order INTEGER
            )
        """)
        
        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                class_id INTEGER,
                subject TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
        """)
        
        # Homework entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS homework_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                content TEXT NOT NULL,
                homework TEXT,
                exam TEXT,
                teacher_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            )
        """)
        
        # Schedule data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER NOT NULL,
                day_id INTEGER NOT NULL,
                slot_id INTEGER NOT NULL,
                content TEXT,
                class_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(week_number, day_id, slot_id),
                FOREIGN KEY (day_id) REFERENCES days(id),
                FOREIGN KEY (slot_id) REFERENCES time_slots(id),
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
        """)
        
        # Holidays table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                label TEXT NOT NULL,
                holiday_type TEXT DEFAULT 'public'
            )
        """)
        
        # Vacations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                label TEXT NOT NULL
            )
        """)
        
        # Teacher absences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS absences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                teacher_id INTEGER,
                reason TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            )
        """)
        
        # Modules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Course progress tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                last_course_id INTEGER,
                last_week INTEGER,
                school_year TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (last_course_id) REFERENCES courses(id),
                UNIQUE(class_id, school_year)
            )
        """)
        
        conn.commit()
        logging.info("Database schema created successfully")
    
    def populate_initial_data(self):
        """Add initial required data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Add default admin teacher
        cursor.execute("SELECT COUNT(*) FROM teachers")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO teachers (name, subject, username, password)
                VALUES (?, ?, ?, ?)
            """, ('Administrateur', 'Administration', 'admin', 'admin123'))
            logging.info("Default admin account created")
        
        # Add days of week
        cursor.execute("SELECT COUNT(*) FROM days")
        if cursor.fetchone()[0] == 0:
            days = [
                ('Lundi', 1), ('Mardi', 2), ('Mercredi', 3),
                ('Jeudi', 4), ('Vendredi', 5), ('Samedi', 6)
            ]
            cursor.executemany("""
                INSERT INTO days (name, display_order) VALUES (?, ?)
            """, days)
            logging.info(f"Added {len(days)} days of week")
        
        # Add time slots
        cursor.execute("SELECT COUNT(*) FROM time_slots")
        if cursor.fetchone()[0] == 0:
            slots = [
                ('08:30', '09:30', 'morning', 0, 1),
                ('09:30', '10:30', 'morning', 0, 2),
                ('10:30', '11:30', 'morning', 0, 3),
                ('11:30', '12:30', 'morning', 0, 4),
                ('12:30', '14:30', 'lunch', 1, 5),
                ('14:30', '15:30', 'afternoon', 0, 6),
                ('15:30', '16:30', 'afternoon', 0, 7),
                ('16:30', '17:30', 'afternoon', 0, 8),
                ('17:30', '18:30', 'afternoon', 0, 9),
            ]
            cursor.executemany("""
                INSERT INTO time_slots (start_time, end_time, period, is_lunch, display_order)
                VALUES (?, ?, ?, ?, ?)
            """, slots)
            logging.info(f"Added {len(slots)} time slots")
        
        conn.commit()
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    
    def execute_update(self, query, params=None):
        """Execute an update/insert/delete query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid
    
    def get_all_tables(self):
        """Get list of all tables in database"""
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.execute_query(query)
        return [row[0] for row in results]
    
    def verify_schema(self):
        """Verify all required tables exist"""
        required_tables = [
            'teachers', 'classes', 'days', 'time_slots', 'courses',
            'homework_entries', 'schedule_data', 'holidays', 'vacations',
            'absences', 'modules', 'course_progress'
        ]
        
        existing_tables = self.get_all_tables()
        missing = [t for t in required_tables if t not in existing_tables]
        
        if missing:
            logging.error(f"Missing tables: {missing}")
            return False
        
        logging.info("All required tables exist")
        return True
