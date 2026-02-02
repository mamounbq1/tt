"""
Quick test for new course distribution system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager
from src.core.course_distribution import CourseDistributionManager
from src.utils.config import DB_PATH
from datetime import datetime, timedelta

def test_new_distribution():
    print("=" * 70)
    print("QUICK TEST - NEW COURSE DISTRIBUTION SYSTEM")
    print("=" * 70)
    print()
    
    # Initialize
    db = DatabaseManager(DB_PATH)
    dist = CourseDistributionManager(DB_PATH)
    
    # Test 1: Load sample courses
    print("✅ Test 1: Load Sample Courses")
    success, message = dist.load_sample_courses()
    print(f"   {message}")
    
    # Test 2: Create test classes
    print("\n✅ Test 2: Create Test Classes")
    test_classes = [
        ('TCSF1', 'Terminal', '2024-2025'),
        ('TCSF2', 'Terminal', '2024-2025'),
        ('TCSF3', 'Terminal', '2024-2025'),
    ]
    
    for name, level, year in test_classes:
        db.execute_update(
            "INSERT OR IGNORE INTO classes (name, level, school_year) VALUES (?, ?, ?)",
            (name, level, year)
        )
        print(f"   Created: {name}")
    
    # Test 3: Create fixed schedule entries
    print("\n✅ Test 3: Create Fixed Schedule Entries")
    conn = dist.get_connection()
    cursor = conn.cursor()
    
    # Get class IDs
    cursor.execute("SELECT id, name FROM classes")
    classes = {row['name']: row['id'] for row in cursor.fetchall()}
    
    # Create schedule: TCSF1 on Monday/Wednesday, TCSF2 on Tuesday/Thursday, etc.
    schedule_plan = [
        (1, 1, 'TCSF1'),  # Lundi 08:30 - TCSF1
        (1, 2, 'TCSF2'),  # Lundi 09:30 - TCSF2
        (2, 1, 'TCSF3'),  # Mardi 08:30 - TCSF3
        (2, 2, 'TCSF1'),  # Mardi 09:30 - TCSF1
        (3, 1, 'TCSF2'),  # Mercredi 08:30 - TCSF2
        (3, 2, 'TCSF3'),  # Mercredi 09:30 - TCSF3
    ]
    
    for day_id, slot_id, class_name in schedule_plan:
        class_id = classes[class_name]
        db.execute_update(
            "INSERT OR REPLACE INTO schedule_entries (day_id, time_slot_id, class_id) VALUES (?, ?, ?)",
            (day_id, slot_id, class_id)
        )
    
    print(f"   Created {len(schedule_plan)} schedule entries")
    
    # Test 4: Distribute courses for week 1
    print("\n✅ Test 4: Distribute Courses for Week 1")
    week_start = datetime(2024, 9, 2)  # First Monday of September
    week_end = week_start + timedelta(days=5)
    
    distribution = dist.distribute_courses(
        week_number=1,
        week_start=week_start,
        week_end=week_end,
        school_year='2024-2025'
    )
    
    print(f"   Distribution result: {len(distribution)} classes")
    for class_id, slots in distribution.items():
        cursor.execute("SELECT name FROM classes WHERE id = ?", (class_id,))
        class_name = cursor.fetchone()['name']
        print(f"   • {class_name}: {len(slots)} courses assigned")
        for day_id, slot_id, course_id in slots[:3]:  # Show first 3
            if course_id != "No more courses":
                course_text = dist.fetch_course_value_by_id(course_id)
                print(f"     - Day {day_id}, Slot {slot_id}: {course_text}")
    
    # Test 5: Verify course_value retrieval
    print("\n✅ Test 5: Verify Course Value Retrieval")
    course_value = dist.fetch_course_value_by_id(1)
    print(f"   Course ID 1 = '{course_value}'")
    
    # Test 6: Check ma_table content
    print("\n✅ Test 6: Check ma_table Content")
    cursor.execute("SELECT COUNT(*) as count FROM ma_table")
    count = cursor.fetchone()['count']
    cursor.execute("SELECT id, valeur FROM ma_table LIMIT 5")
    print(f"   Total courses in ma_table: {count}")
    print("   First 5 courses:")
    for row in cursor.fetchall():
        print(f"     {row['id']}: {row['valeur']}")
    
    dist.close()
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ ALL QUICK TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    test_new_distribution()
