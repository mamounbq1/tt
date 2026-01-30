from datetime import datetime, timedelta

# Color scheme
COLORS = {
    'header_bg': '#2C3E50',
    'header_fg': 'white',
    'time_bg': '#34495E',
    'time_fg': 'white',
    'cell_bg': 'white',
    'cell_fg': '#2C3E50',
    'empty_fg': '#95A5A6',
    'hover_bg': '#ECF0F1',
    'hover_empty_fg': '#7F8C8D',
    'placeholder_bg': '#F0F0F0',
    'holiday_bg': '#FFB6C1',
    'absence_bg': '#FFE4E1',
    'vacation_bg': '#FFE4E1',
    'no_more_courses_bg': '#FFF3CD',  # Light yellow for "No more courses" warning
    'distribution_error_bg': '#F8D7DA', # Light red for distribution errors
    'holiday_bg': '#FFB6C1',  # Light pink for public holidays
    'absence_bg': '#FFE4E1',  # Light red for absences
    'vacation_bg': '#FFCCBC',  # Light orange for vacations
    'default_bg': '#FFFFFF'    # Fallback color
}

# Time slots
MORNING_SLOTS = [
    "08:30 - 09:30",
    "09:30 - 10:30",
    "10:30 - 11:30",
    "11:30 - 12:30"
]

AFTERNOON_SLOTS = [
    "14:30 - 15:30",
    "15:30 - 16:30",
    "16:30 - 17:30",
    "17:30 - 18:30"
]

DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

# Course distribution settings
DISTRIBUTION_FORMAT = "{group} - {course}"  # Format for displaying distributed courses
NO_MORE_COURSES_TEXT = "No more courses available"

def get_school_year():
    """Get the current school year start and end dates"""
    current_date = datetime.now()
    if current_date.month < 9:  # If current month is before September
        start_year = current_date.year - 1
    else:
        start_year = current_date.year
        
    school_start = datetime(start_year, 9, 1)
    school_end = datetime(start_year + 1, 7, 7)
    return school_start, school_end

def format_week_text(week_start, vacation_text=""):
    """Format week text for display"""
    week_end = week_start + timedelta(days=5)
    week_number = week_start.isocalendar()[1]
    return (f"Semaine {week_number} - du {week_start.strftime('%d/%m/%Y')} "
            f"au {week_end.strftime('%d/%m/%Y')}{vacation_text}")

def get_week_dates(week_start, days):
    """Get dates for each day of the week"""
    dates = {}
    for i, day in enumerate(days):
        date = week_start + timedelta(days=i)
        dates[day] = date.strftime('%Y-%m-%d')
    return dates