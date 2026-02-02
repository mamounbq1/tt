"""
Course Distribution Manager for Cahier de Texte
Handles automatic course distribution based on schedule entries
"""

import sqlite3
import logging
from datetime import datetime, timedelta


class CourseDistributionManager:
    """Manages automatic course distribution across the school year"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
    
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
    
    def get_valid_slots(self, week_number):
        """
        Get all valid time slots for a given week (excluding lunch breaks)
        Returns list of (day_id, time_slot_id) tuples
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT d.id as day_id, t.id as time_slot_id
            FROM days d
            CROSS JOIN time_slots t
            WHERE t.is_lunch = 0
            ORDER BY d.display_order, t.display_order
        """)
        
        return [(row['day_id'], row['time_slot_id']) for row in cursor.fetchall()]
    
    def get_next_course(self, class_id, week_number, school_year):
        """
        Get the next course content for a class
        Returns (course_id, content) or (None, None) if no more courses
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get the last course assigned to this class
        cursor.execute("""
            SELECT last_course_id
            FROM course_progress
            WHERE class_id = ? AND school_year = ?
        """, (class_id, school_year))
        
        result = cursor.fetchone()
        last_course_id = result['last_course_id'] if result else None
        
        # Get next course from ma_table
        if last_course_id is None:
            # First course for this class
            cursor.execute("""
                SELECT id, valeur FROM ma_table
                ORDER BY id ASC LIMIT 1
            """)
        else:
            # Next sequential course
            cursor.execute("""
                SELECT id, valeur FROM ma_table
                WHERE id > ?
                ORDER BY id ASC LIMIT 1
            """, (last_course_id,))
        
        course = cursor.fetchone()
        if course:
            return course['id'], course['valeur']
        
        return None, None
    
    def update_course_progress(self, class_id, course_id, week_number, school_year):
        """Update the course progress for a class"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute("""
            SELECT id FROM course_progress
            WHERE class_id = ? AND school_year = ?
        """, (class_id, school_year))
        
        if cursor.fetchone():
            # Update existing record
            cursor.execute("""
                UPDATE course_progress
                SET last_course_id = ?, last_week = ?, updated_at = CURRENT_TIMESTAMP
                WHERE class_id = ? AND school_year = ?
            """, (course_id, week_number, class_id, school_year))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO course_progress (class_id, last_course_id, last_week, school_year)
                VALUES (?, ?, ?, ?)
            """, (class_id, course_id, week_number, school_year))
        
        conn.commit()
    
    def is_day_blocked(self, date_str, vacations, holidays, absences):
        """
        Check if a date is blocked (vacation, holiday, or absence)
        date_str format: 'YYYY-MM-DD'
        """
        # Check holidays
        for holiday in holidays:
            if holiday['date'] == date_str:
                logging.info(f"Date {date_str} is a holiday: {holiday['label']}")
                return True
        
        # Check vacations
        for vacation in vacations:
            start = vacation['start_date']
            end = vacation['end_date']
            if start <= date_str <= end:
                logging.info(f"Date {date_str} is in vacation: {vacation['label']}")
                return True
        
        # Check absences
        for absence in absences:
            if absence['date'] == date_str:
                logging.info(f"Date {date_str} has teacher absence: {absence['reason']}")
                return True
        
        return False
    
    def get_date_from_day_id(self, week_start, day_id):
        """
        Convert day_id (1-6) to actual date
        week_start: datetime object for Monday of the week
        day_id: 1=Lundi, 2=Mardi, ..., 6=Samedi
        """
        return week_start + timedelta(days=day_id - 1)
    
    def get_week_dates(self, week_number, school_year):
        """
        Get start and end dates for a given week number
        Returns (week_start, week_end) as datetime objects
        """
        # School year starts on first Monday of September
        year_start = int(school_year.split('-')[0])
        september_first = datetime(year_start, 9, 1)
        
        # Find first Monday
        days_until_monday = (7 - september_first.weekday()) % 7
        if days_until_monday == 0 and september_first.weekday() != 0:
            days_until_monday = 7
        first_monday = september_first + timedelta(days=days_until_monday)
        
        # Calculate week start
        week_start = first_monday + timedelta(weeks=week_number - 1)
        week_end = week_start + timedelta(days=5)  # Saturday
        
        return week_start, week_end
    
    def distribute_courses(self, week_number, school_year):
        """
        Main distribution algorithm: assign courses to schedule for a given week
        Returns: (success, message, distribution_data)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        logging.info(f"Starting course distribution for week {week_number}, school year {school_year}")
        
        # Get week dates
        week_start, week_end = self.get_week_dates(week_number, school_year)
        logging.info(f"Week {week_number}: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        
        # Load constraints
        cursor.execute("SELECT * FROM holidays")
        holidays = cursor.fetchall()
        
        cursor.execute("SELECT * FROM vacations")
        vacations = cursor.fetchall()
        
        cursor.execute("SELECT * FROM absences")
        absences = cursor.fetchall()
        
        # Get fixed schedule entries (which classes at which slots)
        cursor.execute("""
            SELECT se.day_id, se.time_slot_id, se.class_id, c.name as class_name
            FROM schedule_entries se
            JOIN classes c ON se.class_id = c.id
            ORDER BY se.day_id, se.time_slot_id
        """)
        schedule_entries = cursor.fetchall()
        
        if not schedule_entries:
            return False, "Aucune entrée d'emploi du temps fixe trouvée. Veuillez d'abord créer l'emploi du temps.", []
        
        # Clear existing distribution for this week
        cursor.execute("DELETE FROM schedule_data WHERE week_number = ?", (week_number,))
        
        distribution_data = []
        courses_assigned = 0
        slots_blocked = 0
        
        # Process each scheduled slot
        for entry in schedule_entries:
            day_id = entry['day_id']
            time_slot_id = entry['time_slot_id']
            class_id = entry['class_id']
            class_name = entry['class_name']
            
            # Get actual date
            slot_date = self.get_date_from_day_id(week_start, day_id)
            date_str = slot_date.strftime('%Y-%m-%d')
            
            # Check if day is blocked
            if self.is_day_blocked(date_str, vacations, holidays, absences):
                slots_blocked += 1
                logging.info(f"Slot blocked: {date_str} for {class_name}")
                continue
            
            # Get next course for this class
            course_id, course_content = self.get_next_course(class_id, week_number, school_year)
            
            if course_id is None:
                logging.warning(f"No more courses available for class {class_name}")
                course_content = "⚠️ Fin du programme"
            else:
                # Update progress
                self.update_course_progress(class_id, course_id, week_number, school_year)
                courses_assigned += 1
            
            # Save to schedule_data
            cursor.execute("""
                INSERT OR REPLACE INTO schedule_data (week_number, day_id, slot_id, content, class_id)
                VALUES (?, ?, ?, ?, ?)
            """, (week_number, day_id, time_slot_id, course_content, class_id))
            
            distribution_data.append({
                'day_id': day_id,
                'time_slot_id': time_slot_id,
                'class_id': class_id,
                'class_name': class_name,
                'content': course_content,
                'date': date_str
            })
        
        conn.commit()
        
        message = f"✅ Distribution réussie!\n"
        message += f"• Cours assignés: {courses_assigned}\n"
        message += f"• Créneaux bloqués (vacances/absences): {slots_blocked}\n"
        message += f"• Semaine: {week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}"
        
        logging.info(message)
        
        return True, message, distribution_data
    
    def get_distribution_summary(self, week_number):
        """Get summary of distribution for a week"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                d.name as day_name,
                t.start_time || '-' || t.end_time as time_range,
                c.name as class_name,
                sd.content
            FROM schedule_data sd
            JOIN days d ON sd.day_id = d.id
            JOIN time_slots t ON sd.slot_id = t.id
            LEFT JOIN classes c ON sd.class_id = c.id
            WHERE sd.week_number = ?
            ORDER BY d.display_order, t.display_order
        """, (week_number,))
        
        return cursor.fetchall()
    
    def load_sample_courses(self):
        """Load sample course content into ma_table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute("SELECT COUNT(*) FROM ma_table")
        if cursor.fetchone()[0] > 0:
            return False, "ma_table already contains courses"
        
        sample_courses = [
            "Introduction aux mathématiques",
            "Les nombres entiers",
            "Les fractions",
            "Les équations du premier degré",
            "La géométrie plane",
            "Les triangles et leurs propriétés",
            "Le théorème de Pythagore",
            "Les fonctions linéaires",
            "Les statistiques descriptives",
            "Les probabilités",
            "Introduction à la physique",
            "La mécanique newtonienne",
            "Les lois de la thermodynamique",
            "L'électricité",
            "Le magnétisme",
            "L'optique géométrique",
            "Les ondes",
            "La chimie organique",
            "Les réactions chimiques",
            "La biologie cellulaire",
            "La génétique",
            "L'évolution des espèces",
            "L'écosystème",
            "La grammaire française",
            "La conjugaison",
            "L'analyse littéraire",
            "La poésie",
            "Le roman au XIXe siècle",
            "Le théâtre classique",
            "L'argumentation",
        ]
        
        cursor.executemany(
            "INSERT INTO ma_table (valeur) VALUES (?)",
            [(course,) for course in sample_courses]
        )
        
        conn.commit()
        
        return True, f"{len(sample_courses)} sample courses loaded"
