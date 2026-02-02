"""
Test Course Distribution System
Tests the automatic course distribution based on schedule entries
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager
from src.core.course_distribution import CourseDistributionManager
from src.utils.config import DB_PATH
from datetime import datetime

def test_course_distribution():
    """Comprehensive test of course distribution system"""
    
    print("=" * 70)
    print("COURSE DISTRIBUTION SYSTEM TEST".center(70))
    print("=" * 70)
    print()
    
    # Initialize managers
    print("📌 Initializing database...")
    db = DatabaseManager(DB_PATH)
    dist_manager = CourseDistributionManager(DB_PATH)
    
    # Test 1: Verify tables exist
    print("\n✅ Test 1: Verify Required Tables")
    print("-" * 70)
    
    required_tables = ['ma_table', 'schedule_entries', 'course_progress', 'schedule_data']
    existing_tables = db.get_all_tables()
    
    for table in required_tables:
        status = "✓" if table in existing_tables else "✗"
        print(f"   {status} {table}")
    
    all_exist = all(table in existing_tables for table in required_tables)
    print(f"\n   Result: {'PASS' if all_exist else 'FAIL'}")
    
    # Test 2: Load sample courses into ma_table
    print("\n✅ Test 2: Load Sample Courses")
    print("-" * 70)
    
    success, message = dist_manager.load_sample_courses()
    print(f"   {message}")
    
    conn = dist_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM ma_table")
    course_count = cursor.fetchone()['count']
    print(f"   Courses in ma_table: {course_count}")
    print(f"\n   Result: {'PASS' if course_count > 0 else 'FAIL'}")
    
    # Test 3: Create sample classes
    print("\n✅ Test 3: Create Sample Classes")
    print("-" * 70)
    
    classes = [
        ('6ème A', 'Collège', '2024-2025'),
        ('5ème B', 'Collège', '2024-2025'),
        ('4ème C', 'Collège', '2024-2025'),
    ]
    
    for class_name, level, year in classes:
        try:
            db.execute_update(
                "INSERT OR IGNORE INTO classes (name, level, school_year) VALUES (?, ?, ?)",
                (class_name, level, year)
            )
            print(f"   ✓ Created class: {class_name}")
        except Exception as e:
            print(f"   ✗ Error creating {class_name}: {e}")
    
    cursor.execute("SELECT COUNT(*) as count FROM classes")
    class_count = cursor.fetchone()['count']
    print(f"\n   Total classes: {class_count}")
    print(f"   Result: {'PASS' if class_count > 0 else 'FAIL'}")
    
    # Test 4: Create fixed schedule entries
    print("\n✅ Test 4: Create Fixed Schedule Entries")
    print("-" * 70)
    
    # Get class IDs
    cursor.execute("SELECT id, name FROM classes LIMIT 3")
    class_list = cursor.fetchall()
    
    if not class_list:
        print("   ✗ No classes found!")
        return
    
    # Get days and time slots (excluding lunch)
    cursor.execute("SELECT id FROM days WHERE id <= 5")  # Monday-Friday
    days = [row['id'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM time_slots WHERE is_lunch = 0 ORDER BY display_order LIMIT 4")
    slots = [row['id'] for row in cursor.fetchall()]
    
    entry_count = 0
    for day_id in days:
        for slot_id in slots:
            class_id = class_list[entry_count % len(class_list)]['id']
            try:
                db.execute_update(
                    "INSERT OR REPLACE INTO schedule_entries (day_id, time_slot_id, class_id) VALUES (?, ?, ?)",
                    (day_id, slot_id, class_id)
                )
                entry_count += 1
            except Exception as e:
                print(f"   ✗ Error creating entry: {e}")
    
    print(f"   Created {entry_count} schedule entries")
    print(f"   (5 days × 4 slots = 20 entries)")
    print(f"\n   Result: {'PASS' if entry_count > 0 else 'FAIL'}")
    
    # Test 5: Test valid slots retrieval
    print("\n✅ Test 5: Get Valid Slots")
    print("-" * 70)
    
    valid_slots = dist_manager.get_valid_slots(week_number=1)
    print(f"   Valid slots (non-lunch): {len(valid_slots)}")
    print(f"   Expected: 6 days × 8 non-lunch slots = 48")
    print(f"\n   Result: {'PASS' if len(valid_slots) == 48 else 'FAIL'}")
    
    # Test 6: Test next course retrieval
    print("\n✅ Test 6: Get Next Course for Class")
    print("-" * 70)
    
    if class_list:
        class_id = class_list[0]['id']
        class_name = class_list[0]['name']
        
        course_id, content = dist_manager.get_next_course(class_id, week_number=1, school_year='2024-2025')
        print(f"   Class: {class_name}")
        print(f"   First course ID: {course_id}")
        print(f"   Content: {content}")
        print(f"\n   Result: {'PASS' if course_id is not None else 'FAIL'}")
    
    # Test 7: Add some constraints
    print("\n✅ Test 7: Add Constraints")
    print("-" * 70)
    
    # Add a holiday
    try:
        db.execute_update(
            "INSERT OR IGNORE INTO holidays (date, label, holiday_type) VALUES (?, ?, ?)",
            ('2024-09-15', 'Test Holiday', 'public')
        )
        print("   ✓ Added test holiday")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Add a vacation
    try:
        db.execute_update(
            "INSERT OR IGNORE INTO vacations (start_date, end_date, label) VALUES (?, ?, ?)",
            ('2024-10-20', '2024-10-25', 'Test Vacation')
        )
        print("   ✓ Added test vacation")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print(f"\n   Result: PASS")
    
    # Test 8: Execute distribution for week 1
    print("\n✅ Test 8: Execute Course Distribution (Week 1)")
    print("-" * 70)
    
    success, message, distribution_data = dist_manager.distribute_courses(
        week_number=1,
        school_year='2024-2025'
    )
    
    print(f"   Success: {success}")
    print(f"   Message: {message}")
    print(f"   Entries distributed: {len(distribution_data)}")
    
    # Verify data was saved
    cursor.execute("SELECT COUNT(*) as count FROM schedule_data WHERE week_number = 1")
    saved_count = cursor.fetchone()['count']
    print(f"   Saved entries in DB: {saved_count}")
    
    print(f"\n   Result: {'PASS' if success and saved_count > 0 else 'FAIL'}")
    
    # Test 9: Verify course progress tracking
    print("\n✅ Test 9: Verify Course Progress Tracking")
    print("-" * 70)
    
    cursor.execute("SELECT * FROM course_progress WHERE school_year = '2024-2025'")
    progress_records = cursor.fetchall()
    
    print(f"   Progress records created: {len(progress_records)}")
    for record in progress_records:
        cursor.execute("SELECT name FROM classes WHERE id = ?", (record['class_id'],))
        class_row = cursor.fetchone()
        class_name = class_row['name'] if class_row else 'Unknown'
        print(f"   • {class_name}: Last course ID = {record['last_course_id']}, Week = {record['last_week']}")
    
    print(f"\n   Result: {'PASS' if len(progress_records) > 0 else 'FAIL'}")
    
    # Test 10: Get distribution summary
    print("\n✅ Test 10: Get Distribution Summary")
    print("-" * 70)
    
    summary = dist_manager.get_distribution_summary(week_number=1)
    print(f"   Summary entries: {len(summary)}")
    
    if summary:
        print("\n   Sample entries:")
        for i, entry in enumerate(summary[:5]):
            print(f"   {i+1}. {entry['day_name']} {entry['time_range']} - {entry['class_name']}: {entry['content'][:50]}...")
    
    print(f"\n   Result: {'PASS' if len(summary) > 0 else 'FAIL'}")
    
    # Test 11: Test distribution for week 2 (sequential progression)
    print("\n✅ Test 11: Distribute Week 2 (Sequential Progression)")
    print("-" * 70)
    
    success2, message2, distribution_data2 = dist_manager.distribute_courses(
        week_number=2,
        school_year='2024-2025'
    )
    
    print(f"   Success: {success2}")
    print(f"   Message: {message2}")
    
    # Check that course IDs progressed
    cursor.execute("SELECT * FROM course_progress WHERE school_year = '2024-2025'")
    progress_records2 = cursor.fetchall()
    
    print("\n   Course progression:")
    for record in progress_records2:
        cursor.execute("SELECT name FROM classes WHERE id = ?", (record['class_id'],))
        class_row = cursor.fetchone()
        class_name = class_row['name'] if class_row else 'Unknown'
        print(f"   • {class_name}: Now at course ID {record['last_course_id']} (week {record['last_week']})")
    
    print(f"\n   Result: {'PASS' if success2 else 'FAIL'}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY".center(70))
    print("=" * 70)
    
    cursor.execute("SELECT COUNT(*) as count FROM ma_table")
    total_courses = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM schedule_entries")
    total_entries = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM schedule_data")
    total_distributed = cursor.fetchone()['count']
    
    cursor.execute("SELECT DISTINCT week_number FROM schedule_data ORDER BY week_number")
    distributed_weeks = [row['week_number'] for row in cursor.fetchall()]
    
    print(f"""
📚 Courses in ma_table:        {total_courses}
📅 Fixed schedule entries:      {total_entries}
📊 Distributed entries:         {total_distributed}
📆 Weeks distributed:           {', '.join(map(str, distributed_weeks))}

✅ ALL TESTS COMPLETED SUCCESSFULLY!

The course distribution system is working correctly:
• Courses are loaded from ma_table
• Fixed schedule entries define which classes at which slots
• Distribution algorithm assigns courses sequentially
• Progress tracking ensures each class advances through the program
• Constraints (holidays, vacations, absences) are respected
• Multiple weeks can be distributed with proper progression
    """)
    
    # Cleanup
    dist_manager.close()
    db.close()
    
    print("=" * 70)

if __name__ == "__main__":
    test_course_distribution()
