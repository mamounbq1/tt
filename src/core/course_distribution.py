"""
Course Distribution Manager for Cahier de Texte
Handles automatic course distribution based on schedule entries
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional


class CourseDistributionManager:
    """Manages automatic course distribution across the school year"""
    
    def __init__(self, db_path: str):
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
    
    def get_next_course(self, class_id: int, week_number: int, appearance_count: int, school_year: str) -> Optional[int]:
        """
        Get next course ID for a class based on progression
        
        Args:
            class_id: The class identifier
            week_number: Current week number
            appearance_count: Number of times this class has appeared in current distribution
            school_year: The school year (e.g., "2024-2025")
        
        Returns:
            course_id from ma_table or None if no more courses
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get last course from course_progress for this school year
        cursor.execute("""
            SELECT last_course_id 
            FROM course_progress 
            WHERE class_id = ? AND school_year = ? AND last_week < ?
            ORDER BY last_week DESC
            LIMIT 1
        """, (class_id, school_year, week_number))
        
        result = cursor.fetchone()
        logging.info(f"Found last course for class {class_id}: {result}")
        
        # If no previous course, start with the first course
        last_course_id = result['last_course_id'] if result else 0
        
        # Get all available courses
        cursor.execute("SELECT id FROM ma_table ORDER BY id")
        courses = [row['id'] for row in cursor.fetchall()]
        
        if not courses:
            return None
        
        # Find the index of the last course ID
        if last_course_id in courses:
            last_index = courses.index(last_course_id)
        else:
            last_index = -1
        
        # Calculate the next course index
        next_index = last_index + appearance_count + 1
        
        # Debug information
        logging.info(f"""
            Debug info:
            - Class: {class_id}
            - Week: {week_number}
            - School Year: {school_year}
            - Last course ID: {last_course_id}
            - Last index: {last_index}
            - Appearance count: {appearance_count}
            - Next index: {next_index}
        """)
        
        # Return next course if available
        if next_index < len(courses):
            next_course = courses[next_index]
            logging.info(f"Next course selected: {next_course}")
            return next_course
        return None
    
    def get_date_from_day_id(self, week_start, day_id: int):
        """
        Convert day_id (1-6) to actual date based on the week's start date.
        """
        if isinstance(week_start, datetime):
            week_start = week_start.date()
        # Subtract 1 from day_id since timedelta counts from 0
        result_date = week_start + timedelta(days=day_id - 1)
        # Ensure we return a date object
        if isinstance(result_date, datetime):
            return result_date.date()
        return result_date
    
    def is_day_in_vacation(self, date, vacation_periods: List[Tuple]) -> bool:
        """Check if the given date is within any of the vacation periods."""
        for start_date_str, end_date_str in vacation_periods:
            # Convert string dates to datetime.date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date <= date <= end_date:
                return True
        return False
    
    def is_lunch_break(self, time_slot_id: int) -> bool:
        """Check if the time slot is a lunch break."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT is_lunch FROM time_slots WHERE id = ?",
            (time_slot_id,)
        )
        result = cursor.fetchone()
        return result and result['is_lunch'] == 1 if result else False
    
    def distribute_courses(self, week_number: int, week_start, week_end, school_year: str) -> Dict[int, List[Tuple]]:
        """
        Main distribution algorithm: assign courses to schedule for a given week
        
        Args:
            week_number: Week number (1-36)
            week_start: Start date of the week
            week_end: End date of the week
            school_year: School year (e.g., "2024-2025")
        
        Returns:
            Dictionary mapping class_id to list of (day_id, time_slot_id, course_id) tuples
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Fetch all classes
        cursor.execute("SELECT DISTINCT id FROM classes")
        classes = [c['id'] for c in cursor.fetchall()]
        
        distribution = {class_id: [] for class_id in classes}
        appearance_count = {class_id: 0 for class_id in classes}
        
        # Fetch all schedule entries (fixed timetable)
        cursor.execute("""
            SELECT day_id, time_slot_id, class_id 
            FROM schedule_entries 
            ORDER BY day_id, time_slot_id
        """)
        all_schedule_entries = cursor.fetchall()
        
        # Fetch vacation periods
        cursor.execute("""
            SELECT start_date, end_date 
            FROM vacations 
            WHERE ? BETWEEN start_date AND end_date
            OR ? BETWEEN start_date AND end_date
            OR (start_date BETWEEN ? AND ?)
            OR (end_date BETWEEN ? AND ?)
        """, (week_start, week_end, week_start, week_end, week_start, week_end))
        vacation_periods = cursor.fetchall()
        
        # Format dates for holiday query
        if isinstance(week_start, datetime):
            date_param1 = week_start.strftime('%Y-%m-%d')
        else:
            date_param1 = week_start
            
        if isinstance(week_end, datetime):
            date_param2 = week_end.strftime('%Y-%m-%d')
        else:
            date_param2 = week_end
        
        # Fetch holidays
        cursor.execute("""
            SELECT date 
            FROM holidays 
            WHERE date BETWEEN ? AND ?
        """, (date_param1, date_param2))
        
        public_holidays = [datetime.strptime(row['date'], '%Y-%m-%d').date() if isinstance(row['date'], str) 
                        else row['date'].date() if isinstance(row['date'], datetime) else row['date'] 
                        for row in cursor.fetchall()]
        
        # Fetch absences
        cursor.execute("""
            SELECT date 
            FROM absences 
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        """, (week_start, week_end))
        absence_days = [row['date'] for row in cursor.fetchall()]
        
        # Iterate over schedule entries
        for entry in all_schedule_entries:
            day_id = entry['day_id']
            time_slot_id = entry['time_slot_id']
            class_id = entry['class_id']
            
            # Calculate actual date for this day_id
            actual_date = self.get_date_from_day_id(week_start, day_id)
            if isinstance(actual_date, datetime):
                actual_date = actual_date.date()
                    
            absence_dates = [datetime.strptime(d, '%Y-%m-%d').date() if isinstance(d, str) 
                            else d.date() if isinstance(d, datetime) else d 
                            for d in absence_days]
            
            # Skip if day is in vacation, public holiday, or absence
            if self.is_day_in_vacation(actual_date, vacation_periods):
                logging.info(f"SKIPPING: {actual_date} is during vacation period")
                continue
                
            if actual_date in absence_dates:
                logging.info(f"SKIPPING: {actual_date} is marked as absence")
                continue
                
            if actual_date in public_holidays:
                logging.info(f"SKIPPING: {actual_date} is a public holiday")
                continue
                
            logging.info(f"Day {actual_date} is valid - continuing with scheduling")
            
            # Skip lunch break
            if self.is_lunch_break(time_slot_id):
                continue
            
            # Assign course to this class
            course_id = self.get_next_course(class_id, week_number, appearance_count[class_id], school_year)
            if course_id:
                distribution[class_id].append((day_id, time_slot_id, course_id))
                appearance_count[class_id] += 1
            else:
                distribution[class_id].append((day_id, time_slot_id, "No more courses"))
        
        return distribution
    
    def load_sample_courses(self):
        """Load sample course content into ma_table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute("SELECT COUNT(*) as count FROM ma_table")
        if cursor.fetchone()['count'] > 0:
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
    
    def fetch_course_value_by_id(self, course_id):
        """
        Fetch course value (text content) from ma_table using course_id
        
        Args:
            course_id: The ID of the course in ma_table
        
        Returns:
            The course text (valeur) or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT valeur FROM ma_table WHERE id = ?", (course_id,))
        result = cursor.fetchone()
        
        if result:
            return result['valeur']
        return None
