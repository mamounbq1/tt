import sqlite3
import logging
from datetime import datetime
import os
from config import DB_PATH  # Import the global database path

class DatabaseManager:
    """Handles database operations for the schedule management system."""

    def __init__(self, db_name=DB_PATH):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._ensure_db_exists()  # Ensure the database file exists
        self.connect()
        self.setup_database()
        self.verify_tables()

    def _ensure_db_exists(self):
        """Create database file if it doesn't exist."""
        # Ensure the directory exists
        directory = os.path.dirname(self.db_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Directory '{directory}' created.")
        # Create the database file if it does not exist
        if not os.path.exists(self.db_name):
            open(self.db_name, 'w').close()
            logging.info(f"Database file '{self.db_name}' was missing and has been created.")

    # =========================
    # 📌 DATABASE CONNECTION
    # =========================
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    # =========================
    # 🔧 DATABASE SETUP
    # =========================
    def setup_database(self):
        """Initialize necessary database tables."""
        tables = [
            """CREATE TABLE IF NOT EXISTS class_distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT,
                week_number INTEGER,
                course_number INTEGER,
                UNIQUE(class_name, week_number)
            )""",
            """CREATE TABLE IF NOT EXISTS schedule_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER,
                day_id INTEGER,
                time_slot_id INTEGER, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id),
                FOREIGN KEY (day_id) REFERENCES days (day_id),
                FOREIGN KEY (time_slot_id) REFERENCES time_slots (slot_id)
            )""",
            """CREATE TABLE IF NOT EXISTS ma_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valeur TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS schedule_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER NOT NULL,
                cell_row INTEGER NOT NULL,
                cell_col INTEGER NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(week_number, cell_row, cell_col)
            )""",
            """CREATE TABLE IF NOT EXISTS days (
                day_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )""",
            # Updated time_slots table with extra columns for is_lunch_break and period
            """CREATE TABLE IF NOT EXISTS time_slots (
                slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                is_lunch_break INTEGER DEFAULT 0,
                period TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level TEXT,
                school_year TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS group_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                day_id INTEGER,
                time_slot_id INTEGER,
                FOREIGN KEY (group_name) REFERENCES classes (name),
                FOREIGN KEY (day_id) REFERENCES days (day_id),
                FOREIGN KEY (time_slot_id) REFERENCES time_slots (slot_id)
            )""",
            """CREATE TABLE IF NOT EXISTS vacances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                label TEXT DEFAULT 'Vacances Scolaires'
            )""",
            """CREATE TABLE IF NOT EXISTS jours_feries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                label TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS absences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                motif TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS enseignants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                matiere TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                classe TEXT NOT NULL,
                matiere TEXT NOT NULL,
                contenu TEXT NOT NULL,
                devoirs TEXT,
                examen TEXT,
                enseignant_id INTEGER NOT NULL,
                FOREIGN KEY (enseignant_id) REFERENCES enseignants(id)
            )""",
            """CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )"""
        ]

        try:
            for table in tables:
                self.cursor.execute(table)
            self.conn.commit()
            logging.info("Database tables set up successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database setup error: {e}")
            raise

        self.create_default_admin()
        self.initialize_time_slots()

    def verify_tables(self):
        """Check if all required tables exist in the database."""
        required_tables = [
            "class_distributions", "schedule_entries", "schedule_data",
            "days", "time_slots", "classes", "group_schedule",
            "vacances", "jours_feries", "absences"
        ]
        missing_tables = []

        for table in required_tables:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not self.cursor.fetchone():
                missing_tables.append(table)

        if missing_tables:
            logging.error(f"Missing tables: {missing_tables}")
            raise sqlite3.Error(f"Missing tables: {missing_tables}")
        else:
            logging.info("All required tables exist.")

    # =========================
    # 📅 SCHEDULE MANAGEMENT
    # =========================
    def get_schedule_entries(self):
        """Retrieve all schedule entries."""
        try:
            self.cursor.execute("""
                SELECT se.day_id, se.time_slot_id, c.name 
                FROM schedule_entries se
                JOIN classes c ON se.class_id = c.id
                ORDER BY se.day_id, se.time_slot_id
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting schedule entries: {e}")
            return []

    def get_saved_schedule(self, week_number):
        """Retrieve saved schedule for a specific week."""
        try:
            self.cursor.execute("""
                SELECT cell_row, cell_col, value 
                FROM schedule_data 
                WHERE week_number = ?
            """, (week_number,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error getting saved schedule: {e}")
            return None

    def save_schedule(self, week_number, schedule_data):
        """Save a schedule for a specific week."""
        try:
            self.cursor.execute("DELETE FROM schedule_data WHERE week_number = ?", (week_number,))
            for row, col, content in schedule_data:
                self.cursor.execute("""
                    INSERT INTO schedule_data (week_number, cell_row, cell_col, value)
                    VALUES (?, ?, ?, ?)
                """, (week_number, row, col, content))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            logging.error(f"Database error saving schedule: {e}")
            return False

    def get_saved_weeks(self):
        """Retrieve unique saved weeks from the schedule entries."""
        try:
            self.cursor.execute("""
                SELECT DISTINCT week_number, strftime('%Y', created_at) as year 
                FROM schedule_entries 
                ORDER BY year DESC, week_number DESC
            """)
            weeks = self.cursor.fetchall()
            logging.debug(f"Fetched weeks: {weeks}")

            # If no rows were returned, return a default tuple.
            if not weeks:
                logging.warning("No saved weeks found in schedule_entries table.")
                return [(0, "Aucune semaine sauvegardée")]

            # Validate each row to ensure it contains at least 2 elements.
            valid_weeks = []
            for row in weeks:
                if isinstance(row, (list, tuple)) and len(row) >= 2:
                    # Replace None values with default values if needed.
                    week_number = row[0] if row[0] is not None else 0
                    year = row[1] if row[1] is not None else "Inconnu"
                    valid_weeks.append((week_number, year))
                else:
                    logging.error(f"Error parsing week: expected 2 values, got {row}")
            return valid_weeks

        except sqlite3.Error as e:
            logging.error(f"Database error fetching saved weeks: {e}")
            return [(0, "Erreur de récupération")]



    # =========================
    # 📆 EVENT & CALENDAR MANAGEMENT
    # =========================
    def get_vacations(self):
        """Retrieve all vacation periods."""
        try:
            self.cursor.execute("SELECT start_date, end_date, label FROM vacances ORDER BY start_date")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting vacations: {e}")
            return []

    def get_jours_feries(self):
        """Retrieve all public holidays."""
        try:
            self.cursor.execute("SELECT date, label FROM jours_feries ORDER BY date")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting public holidays: {e}")
            return []

    def get_absences(self):
        """Retrieve all recorded absences."""
        try:
            self.cursor.execute("SELECT date, motif FROM absences ORDER BY date")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting absences: {e}")
            return []

    def initialize_basic_data(self, columns, morning_slots, afternoon_slots):
        """Initialize basic data in the database including days, and other essential data.
           (Time slots are now initialized separately via initialize_time_slots().)
        """
        try:
            # Initialize days
            days_data = [
                ('Lundi',), ('Mardi',), ('Mercredi',), ('Jeudi',), ('Vendredi',), ('Samedi',)
            ]
            self.cursor.executemany(
                "INSERT OR IGNORE INTO days (name) VALUES (?)", 
                days_data
            )

            self.conn.commit()
            logging.info("Basic data (days) initialized successfully")
            return True

        except sqlite3.Error as e:
            self.conn.rollback()
            logging.error(f"Error initializing basic data: {e}")
            return False

    def initialize_time_slots(self):
        """Initialize the time_slots table with the expected rows if not already present."""
        try:
            # Define the expected time slots.
            expected_time_slots = [
                ("08:30", "09:30", 0, "morning"),
                ("09:30", "10:30", 0, "morning"),
                ("10:30", "11:30", 0, "morning"),
                ("11:30", "12:30", 0, "morning"),
                ("14:30", "15:30", 0, "afternoon"),
                ("15:30", "16:30", 0, "afternoon"),
                ("16:30", "17:30", 0, "afternoon"),
                ("17:30", "18:30", 0, "afternoon"),
                ("12:30", "14:30", 1, "morning")
            ]

            # Query the table for all existing time slots.
            self.cursor.execute("SELECT start_time, end_time, is_lunch_break, period FROM time_slots")
            existing_rows = self.cursor.fetchall()
            logging.debug(f"Existing time slots: {existing_rows}")

            # For each expected time slot, insert it if it is not already present.
            for slot in expected_time_slots:
                if slot not in existing_rows:
                    self.cursor.execute(
                        "INSERT INTO time_slots (start_time, end_time, is_lunch_break, period) VALUES (?, ?, ?, ?)",
                        slot
                    )
                    logging.info(f"Inserted missing time slot: {slot}")

            self.conn.commit()
            logging.info("Time slots checked and initialized successfully")
        except sqlite3.Error as e:
            self.conn.rollback()
            logging.error(f"Error initializing time slots: {e}")

    # =========================
    # 📁 DIRECTORY MANAGEMENT
    # =========================
    @staticmethod
    def ensure_directory_exists(directory):
        """Ensure required directories exist."""
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Ensure directories exist at the time of class definition
    ensure_directory_exists('data')
    ensure_directory_exists('logs')

    # =========================
    # 👤 USER MANAGEMENT
    # =========================
    def create_default_admin(self):
        """Ensure there is a default admin user in the database."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM enseignants WHERE login = 'admin'")
            admin_exists = self.cursor.fetchone()[0]

            if admin_exists == 0:
                self.cursor.execute("""
                    INSERT INTO enseignants (nom, matiere, login, password) 
                    VALUES ('admin', 'admin', 'admin', 'admin')
                """)
                self.conn.commit()
                logging.info("Default admin user created (Username: admin, Password: admin123)")
            else:
                logging.info("Admin user already exists.")
        except sqlite3.Error as e:
            logging.error(f"Error creating default admin: {e}")

    def get_user(self, login, password):
        """Retrieve a user from the database based on login credentials."""
        try:
            self.cursor.execute("SELECT * FROM enseignants WHERE login=? AND password=?", (login, password))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user: {e}")
            return None

    # =========================
    # 🔍 MISSING / UTILITY METHODS (from old code)
    # =========================
    def get_time_slot_id(self, time_slot):
        """Get time slot ID from time slot string (e.g. '08:00 - 09:00')."""
        try:
            self.cursor.execute(
                "SELECT slot_id FROM time_slots WHERE start_time || ' - ' || end_time = ?",
                (time_slot,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logging.error(f"Error getting time slot ID: {e}")
            return None

    def check_events(self, date_str):
        """
        Check for events on a specific date.
        Returns a tuple (event_type, label) where event_type can be 'vacation', 'holiday', or 'absence'.
        """
        try:
            # Check vacations (they have priority)
            self.cursor.execute("""
                SELECT label 
                FROM vacances 
                WHERE ? BETWEEN start_date AND end_date
            """, (date_str,))
            vacation = self.cursor.fetchone()
            if vacation:
                return ('vacation', vacation[0])

            # Check holidays
            self.cursor.execute("SELECT label FROM jours_feries WHERE date = ?", (date_str,))
            holiday = self.cursor.fetchone()
            if holiday:
                return ('holiday', holiday[0])

            # Check absences
            self.cursor.execute("SELECT motif FROM absences WHERE date = ?", (date_str,))
            absence = self.cursor.fetchone()
            if absence:
                return ('absence', absence[0])

            return (None, None)
        except sqlite3.Error as e:
            logging.error(f"Error checking events: {e}")
            return (None, None)

    def get_class_info(self):
        """Get information about the first class."""
        try:
            self.cursor.execute("SELECT name, level, school_year FROM classes WHERE id = 1")
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error getting class info: {e}")
            return None

    def get_ma_table_values(self):
        """Get all values from ma_table."""
        try:
            self.cursor.execute("SELECT id, valeur FROM ma_table ORDER BY id")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting ma_table values: {e}")
            return []

    def get_last_distributions(self, week_number):
        """
        Get the last course number for each class from previous weeks.
        Returns a dictionary with class_name as key and last course number as value.
        """
        try:
            query = """
                SELECT class_name, MAX(course_number) as last_course
                FROM class_distributions
                WHERE week_number < ?
                GROUP BY class_name
            """
            self.cursor.execute(query, (week_number,))
            results = self.cursor.fetchall()
            return {row[0]: row[1] if row[1] is not None else 0 for row in results}
        except sqlite3.Error as e:
            logging.error(f"Database error getting last distributions: {e}")
            return {}

    def save_distribution_state(self, week_number, class_appearances):
        """
        Save the final distribution state for each class.
        class_appearances should be a dictionary with class_name as key and course_number as value.
        """
        try:
            for class_name, course_number in class_appearances.items():
                query = """
                    INSERT OR REPLACE INTO class_distributions 
                    (class_name, week_number, course_number) 
                    VALUES (?, ?, ?)
                """
                self.cursor.execute(query, (class_name, week_number, course_number))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error saving distribution state: {e}")

    def _fetch_course_value_by_id(self, course_id):
        """
        Fetch course value from the database using course_id.
        """
        try:
            query = "SELECT valeur FROM ma_table WHERE id = ?"
            self.cursor.execute(query, (course_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return None
        except sqlite3.Error as e:
            logging.error(f"Database error fetching course value by ID: {e}")
            return None
