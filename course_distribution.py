import sqlite3
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging
from course_dist.db_manager import DatabaseManager

from course_dist.constants import (
    COLORS, MORNING_SLOTS, AFTERNOON_SLOTS, DAYS,
    get_school_year, format_week_text, get_week_dates
)

class CourseDistributionManager:
    def __init__(self, db_path: str):
        """Initialize the course distribution manager"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._setup_tables()
        self.db = DatabaseManager()

    def _setup_tables(self):
        """Set up necessary database tables if they don't exist"""
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS class_course_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                last_course_id INTEGER,
                last_week INTEGER,
                FOREIGN KEY (last_course_id) REFERENCES ma_table(id),
                FOREIGN KEY (class_id) REFERENCES classes(id),
                UNIQUE(class_id, last_week)
            );

            CREATE TABLE IF NOT EXISTS schedule_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                day_id INTEGER NOT NULL,
                time_slot_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (course_id) REFERENCES ma_table(id),
                FOREIGN KEY (class_id) REFERENCES classes(id),
                UNIQUE(week_number, class_id, day_id, time_slot_id)
            );
        """)
        self.conn.commit()

    def get_valid_slots(self, week_number: int) -> List[Tuple[int, int]]:
        """Fetch valid time slots for a given week, excluding vacation days and lunch breaks"""
        logging.info(f"Fetching valid slots for week {week_number}")
        self.cursor.execute("""
            SELECT d.day_id AS day_id, ts.slot_id AS time_slot_id
            FROM days d
            CROSS JOIN time_slots ts
            WHERE NOT EXISTS (
                SELECT 1 FROM vacances v
                WHERE ? BETWEEN v.start_date AND v.end_date
            )
            AND ts.start_time != '12:30'  -- Exclude lunch break
            ORDER BY d.day_id, ts.slot_id
        """, (week_number,))
        valid_slots = self.cursor.fetchall()
        logging.info(f"Valid slots: {valid_slots}")
        return valid_slots
    def get_total_courses(self) -> int:
        """Get the total number of courses available in ma_table"""
        self.cursor.execute("SELECT COUNT(*) FROM ma_table")
        return self.cursor.fetchone()[0]
    







































    def get_school_year_weeks(self):
            school_start, school_end = get_school_year()
            vacations = self.db.get_vacations()
            vacations = [(datetime.strptime(start, '%Y-%m-%d'), 
                        datetime.strptime(end, '%Y-%m-%d'),
                        desc) for start, end, desc in vacations]
            
            weeks = []
            current_date = school_start
            while current_date <= school_end:
                week_start = current_date - timedelta(days=current_date.weekday())
                week_end = week_start + timedelta(days=5)
                
                vacation_text = ""
                for vac_start, vac_end, vac_desc in vacations:
                    if (week_start <= vac_end and week_end >= vac_start):
                        vacation_text = f" ({vac_desc})"
                        break
                
                weeks.append(format_week_text(week_start, vacation_text))
                current_date += timedelta(days=7)
            
            return weeks










    def get_next_course(self, class_id: int, week_number: int, appearance_count: int, current_year: int) -> Optional[int]:
        """
        Get next course based on the progression, handling year transitions.
        Args:
            class_id: The class identifier
            week_number: Current week number
            appearance_count: Number of times this class has appeared in current distribution
            current_year: The year to use (end year for week 1, start year for others)
        """
        if week_number == 1:
            # For week 1, check both previous year and current year
            self.cursor.execute("""
                SELECT last_course_id 
                FROM class_course_progress 
                WHERE class_id = ? AND 
                    ((year = ? AND last_week >= 50) OR  -- End of previous year
                    (year = ? AND last_week < ?))      -- Start of current year
                ORDER BY year DESC, last_week DESC
                LIMIT 1
            """, (class_id, current_year - 1, current_year, week_number))
        else:
            # For other weeks, check only up to current week in current year
            self.cursor.execute("""
                SELECT last_course_id 
                FROM class_course_progress 
                WHERE class_id = ? AND year = ? AND last_week < ?
                ORDER BY last_week DESC
                LIMIT 1
            """, (class_id, current_year, week_number))
        
        result = self.cursor.fetchone()
        print(f"Found last course for class {class_id}: {result}")
        
        # If no previous course, start with the first course
        last_course_id = result[0] if result else 0
        
        # Get all available courses
        self.cursor.execute("SELECT id FROM ma_table ORDER BY id")
        courses = [row[0] for row in self.cursor.fetchall()]
        
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
        print(f"""
            Debug info:
            - Class: {class_id}
            - Week: {week_number}
            - Year: {current_year}
            - Last course ID: {last_course_id}
            - Last index: {last_index}
            - Appearance count: {appearance_count}
            - Next index: {next_index}
        """)
        
        # Return next course if available
        if next_index < len(courses):
            next_course = courses[next_index]
            print(f"Next course selected: {next_course}")
            return next_course
        return None


    def distribute_courses(self, week_number: int, week_start, week_end) -> Dict[int, List[Tuple]]:
        # Determine the primary year for this week
        # For week 1, use the end year (2025)
        # For week 52/53, use the start year (2024)
        if week_number == 1:
            # Week 1 belongs to the end year (2025 for week starting Dec 30, 2024)
            primary_year = week_end.year if isinstance(week_end, datetime) else int(week_end.split('-')[0])
        else:
            # All other weeks belong to the start year
            primary_year = week_start.year if isinstance(week_start, datetime) else int(week_start.split('-')[0])

        # Fetch all classes
        self.cursor.execute("SELECT DISTINCT id FROM classes")
        classes = [c[0] for c in self.cursor.fetchall()]
        
        distribution = {class_id: [] for class_id in classes}
        appearance_count = {class_id: 0 for class_id in classes}
        
        # Fetch valid slots for the week
        valid_slots = self.get_valid_slots(week_number)
        
        # Fetch all schedule entries
        self.cursor.execute("""
            SELECT day_id, time_slot_id, class_id 
            FROM schedule_entries 
            ORDER BY day_id, time_slot_id
        """)
        all_schedule_entries = self.cursor.fetchall()
        
        self.cursor.execute("""
            SELECT start_date, end_date 
            FROM vacances 
            WHERE ? BETWEEN start_date AND end_date
            OR ? BETWEEN start_date AND end_date
            OR (start_date BETWEEN ? AND ?)
            OR (end_date BETWEEN ? AND ?)
        """, (week_start, week_end, week_start, week_end, week_start, week_end))
        vacation_periods = self.cursor.fetchall()
        
        # Format dates for holiday query
        if isinstance(week_start, datetime):
            date_param1 = week_start.strftime('%Y-%m-%d')
        elif isinstance(week_start, datetime.date):
            date_param1 = week_start.strftime('%Y-%m-%d')
        else:
            date_param1 = week_start
            
        if isinstance(week_end, datetime):
            date_param2 = week_end.strftime('%Y-%m-%d')
        elif isinstance(week_end, datetime.date):
            date_param2 = week_end.strftime('%Y-%m-%d')
        else:
            date_param2 = week_end
        
        # Fetch holidays
        self.cursor.execute("""
            SELECT date 
            FROM jours_feries 
            WHERE date BETWEEN ? AND ?
        """, (date_param1, date_param2))
        
        public_holidays = [datetime.strptime(row[0], '%Y-%m-%d').date() if isinstance(row[0], str) 
                        else row[0].date() if isinstance(row[0], datetime) else row[0] 
                        for row in self.cursor.fetchall()]
        
        # Fetch absences
        self.cursor.execute("""
            SELECT date 
            FROM absences 
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        """, (week_start, week_end))
        absence_days = [row[0] for row in self.cursor.fetchall()]
        
        # Iterate over valid slots
        for day_id, time_slot_id in valid_slots:
            # Calculate actual date for this day_id
            actual_date = self.get_date_from_day_id(week_start, day_id)
            if isinstance(actual_date, datetime):
                actual_date = actual_date.date()
                    
            absence_dates = [datetime.strptime(d, '%Y-%m-%d').date() if isinstance(d, str) 
                            else d.date() if isinstance(d, datetime) else d 
                            for d in absence_days]
            
            # Skip if day is in vacation, public holiday, or absence
            if self.is_day_in_vacation(actual_date, vacation_periods):
                print(f"SKIPPING: {actual_date} is during vacation period")
                continue
                
            if actual_date in absence_dates:
                print(f"SKIPPING: {actual_date} is marked as absence")
                continue
                
            if actual_date in public_holidays:
                print(f"SKIPPING: {actual_date} is a public holiday (in list: {public_holidays})")
                continue
                
            print(f"Day {actual_date} is valid - continuing with scheduling")
            
            # Skip lunch break
            if self.is_lunch_break(time_slot_id):
                continue
            
            # Get classes scheduled for this slot
            scheduled_classes = [
                class_id for d, ts, class_id in all_schedule_entries 
                if d == day_id and ts == time_slot_id
            ]
            
            # Assign courses to scheduled classes using primary_year for the whole week
            for class_id in scheduled_classes:
                course_id = self.get_next_course(class_id, week_number, appearance_count[class_id], primary_year)
                if course_id:
                    distribution[class_id].append((day_id, time_slot_id, course_id))
                    appearance_count[class_id] += 1
                else:
                    distribution[class_id].append((day_id, time_slot_id, "No more courses"))
        
        return distribution
    def is_day_in_vacation(self, date: datetime.date, vacation_periods: List[Tuple]) -> bool:
        """Check if the given date is within any of the vacation periods."""
        for start_date_str, end_date_str in vacation_periods:
            # Convert string dates to datetime.date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date <= date <= end_date:
                return True
        return False
        
    def get_date_from_day_id(self, week_start: datetime.date, day_id: int) -> datetime.date:
        """Convert a day_id (1-6) to an actual date based on the week's start date."""
        # Ensure week_start is a date object
        if isinstance(week_start, datetime):
            week_start = week_start.date()
        # Subtract 1 from day_id since timedelta counts from 0
        result_date = week_start + timedelta(days=day_id - 1)
        # Ensure we return a date object
        if isinstance(result_date, datetime):
            return result_date.date()
        return result_date
    def is_lunch_break(self, time_slot_id: int) -> bool:
        """Check if the time slot is a lunch break."""
        # Assuming lunch break time slots are known and can be checked here
        lunch_break_slots = {}  # Example time slot IDs for lunch break
        return time_slot_id in lunch_break_slots


















    
    def validate_distribution(self, week_number: int, distribution: Dict[int, List[Tuple]]) -> Tuple[bool, List[str]]:
        """Validate the distribution"""
        errors = []
        
        # Check for empty slots
        for class_id, slots in distribution.items():
            for day_id, time_slot_id, course in slots:
                if course == "No more courses":
                    continue
                if not course:
                    errors.append(f"Empty slot found for class {class_id} on day {day_id}, time slot {time_slot_id}")

        # Check for duplicate assignments
        assigned_slots = set()
        for slots in distribution.values():
            for day_id, time_slot_id, _ in slots:
                slot_key = (day_id, time_slot_id)
                if slot_key in assigned_slots:
                    errors.append(f"Duplicate assignment found for day {day_id}, time slot {time_slot_id}")
                assigned_slots.add(slot_key)

        return len(errors) == 0, errors
   
   
   

    def load_saved_distribution(self, week_number: int) -> Dict[int, List[Tuple]]:
        """Load a saved distribution"""
        self.cursor.execute("""
            SELECT class_id, day_id, time_slot_id, course_id
            FROM schedule_data
            WHERE week_number = ?
            ORDER BY class_id, day_id, time_slot_id
        """, (week_number,))
        
        results = self.cursor.fetchall()
        distribution = {}
        
        for class_id, day_id, time_slot_id, course_id in results:
            if class_id not in distribution:
                distribution[class_id] = []
            distribution[class_id].append((day_id, time_slot_id, course_id))
            
        return distribution

    def close(self):
        """Close the database connection"""
        self.conn.close()