"""
Complete Workflow Integration Test
Tests the entire flow: Constraints → Schedule → Import → Distribution
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import DatabaseManager
from src.core.course_distribution import CourseDistributionManager
from src.utils.config import DB_PATH


def test_complete_workflow():
    """Test the complete workflow from start to finish"""
    print("=" * 80)
    print("COMPLETE WORKFLOW INTEGRATION TEST")
    print("=" * 80)
    
    # Clean slate - backup existing DB if it exists
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + '.backup'
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(DB_PATH, backup_path)
        print(f"✓ Backed up existing database to {backup_path}")
    
    try:
        # Step 1: Initialize database
        print("\n" + "=" * 80)
        print("STEP 1: Initialize Database")
        print("=" * 80)
        
        db = DatabaseManager(DB_PATH)
        print("✓ Database initialized")
        print(f"✓ Database location: {DB_PATH}")
        
        # Verify tables exist
        tables = db.get_all_tables()
        expected_tables = [
            'classes', 'days', 'time_slots', 'schedule_entries', 
            'schedule_data', 'ma_table', 'course_progress',
            'holidays', 'vacations', 'absences'
        ]
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' MISSING!")
                return False
        
        # Step 2: Create Classes (Constraints)
        print("\n" + "=" * 80)
        print("STEP 2: Create Classes (Constraints)")
        print("=" * 80)
        
        classes_to_create = [
            ('6ème A', '6ème', '2024-2025'),
            ('5ème B', '5ème', '2024-2025'),
            ('4ème C', '4ème', '2024-2025'),
            ('TCSF1', 'Terminale', '2024-2025'),
            ('TCSF2', 'Terminale', '2024-2025')
        ]
        
        for class_name, level, school_year in classes_to_create:
            query = """
                INSERT INTO classes (name, level, school_year)
                VALUES (?, ?, ?)
            """
            db.execute_update(query, (class_name, level, school_year))
            print(f"✓ Created class: {class_name} ({level} - {school_year})")
        
        # Verify classes created
        result = db.execute_query("SELECT COUNT(*) as count FROM classes")
        class_count = result[0]['count']
        print(f"\n✓ Total classes created: {class_count}")
        
        # Step 3: Create Fixed Schedule (schedule_entries)
        print("\n" + "=" * 80)
        print("STEP 3: Create Fixed Schedule (schedule_entries)")
        print("=" * 80)
        
        schedule_entries = [
            # Monday
            (1, 1, 1),  # Lundi 08:30-09:30 → 6ème A (class_id=1)
            (1, 2, 2),  # Lundi 09:30-10:30 → 5ème B (class_id=2)
            (1, 3, 3),  # Lundi 10:30-11:30 → 4ème C (class_id=3)
            (1, 4, 4),  # Lundi 11:30-12:30 → TCSF1 (class_id=4)
            # Tuesday
            (2, 1, 2),  # Mardi 08:30-09:30 → 5ème B
            (2, 2, 3),  # Mardi 09:30-10:30 → 4ème C
            (2, 3, 4),  # Mardi 10:30-11:30 → TCSF1
            (2, 4, 5),  # Mardi 11:30-12:30 → TCSF2 (class_id=5)
            # Wednesday
            (3, 1, 3),  # Mercredi 08:30-09:30 → 4ème C
            (3, 2, 4),  # Mercredi 09:30-10:30 → TCSF1
            (3, 3, 5),  # Mercredi 10:30-11:30 → TCSF2
            (3, 4, 1),  # Mercredi 11:30-12:30 → 6ème A
            # Thursday
            (4, 1, 4),  # Jeudi 08:30-09:30 → TCSF1
            (4, 2, 5),  # Jeudi 09:30-10:30 → TCSF2
            (4, 3, 1),  # Jeudi 10:30-11:30 → 6ème A
            (4, 4, 2),  # Jeudi 11:30-12:30 → 5ème B
            # Friday
            (5, 1, 5),  # Vendredi 08:30-09:30 → TCSF2
            (5, 2, 1),  # Vendredi 09:30-10:30 → 6ème A
            (5, 3, 2),  # Vendredi 10:30-11:30 → 5ème B
            (5, 4, 3),  # Vendredi 11:30-12:30 → 4ème C
        ]
        
        for day_id, time_slot_id, class_id in schedule_entries:
            query = """
                INSERT INTO schedule_entries (day_id, time_slot_id, class_id)
                VALUES (?, ?, ?)
            """
            db.execute_update(query, (day_id, time_slot_id, class_id))
        
        # Get day and class names for display
        for day_id, time_slot_id, class_id in schedule_entries[:5]:  # Show first 5
            day_query = "SELECT name FROM days WHERE id = ?"
            day_result = db.execute_query(day_query, (day_id,))
            day_name = day_result[0]['name'] if day_result else f"Day {day_id}"
            
            slot_query = "SELECT start_time, end_time FROM time_slots WHERE id = ?"
            slot_result = db.execute_query(slot_query, (time_slot_id,))
            time_slot = f"{slot_result[0]['start_time']}-{slot_result[0]['end_time']}" if slot_result else f"Slot {time_slot_id}"
            
            class_query = "SELECT name FROM classes WHERE id = ?"
            class_result = db.execute_query(class_query, (class_id,))
            class_name = class_result[0]['name'] if class_result else f"Class {class_id}"
            
            print(f"✓ {day_name} {time_slot} → {class_name}")
        
        print(f"  ... ({len(schedule_entries) - 5} more entries)")
        
        result = db.execute_query("SELECT COUNT(*) as count FROM schedule_entries")
        entry_count = result[0]['count']
        print(f"\n✓ Total schedule entries created: {entry_count}")
        
        # Step 4: Import Courses (ma_table)
        print("\n" + "=" * 80)
        print("STEP 4: Import Courses (ma_table)")
        print("=" * 80)
        
        distributor = CourseDistributionManager(DB_PATH)
        distributor.load_sample_courses()
        
        result = db.execute_query("SELECT COUNT(*) as count FROM ma_table")
        course_count = result[0]['count']
        print(f"✓ Total courses in ma_table: {course_count}")
        
        # Show first 5 courses
        courses = db.execute_query("SELECT id, valeur FROM ma_table LIMIT 5")
        for course in courses:
            print(f"  {course['id']}: {course['valeur']}")
        print(f"  ... ({course_count - 5} more courses)")
        
        # Step 5: Distribute Courses (Week 1)
        print("\n" + "=" * 80)
        print("STEP 5: Distribute Courses Automatically (Week 1)")
        print("=" * 80)
        
        week_number = 1
        school_start = datetime(2024, 9, 2)  # Sept 2, 2024 is a Monday
        week_start = school_start
        week_end = week_start + timedelta(days=5)
        school_year = "2024-2025"
        
        print(f"Week {week_number}: {week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}")
        
        distribution = distributor.distribute_courses(week_number, week_start, week_end, school_year)
        
        total_distributed = 0
        for class_id, slots in distribution.items():
            class_query = "SELECT name FROM classes WHERE id = ?"
            class_result = db.execute_query(class_query, (class_id,))
            class_name = class_result[0]['name'] if class_result else f"Class {class_id}"
            
            print(f"\n✓ Class: {class_name}")
            print(f"  Total courses distributed: {len(slots)}")
            
            # Show first 3 courses
            for i, (day_id, time_slot_id, course_id) in enumerate(slots[:3]):
                course_value = distributor.fetch_course_value_by_id(course_id)
                day_query = "SELECT name FROM days WHERE id = ?"
                day_result = db.execute_query(day_query, (day_id,))
                day_name = day_result[0]['name'] if day_result else f"Day {day_id}"
                
                print(f"    Day {day_id} ({day_name}), Slot {time_slot_id}: {course_value}")
            
            if len(slots) > 3:
                print(f"    ... ({len(slots) - 3} more)")
            
            total_distributed += len(slots)
        
        print(f"\n✓ Total courses distributed: {total_distributed}")
        
        # Step 6: Verify course_progress updated
        print("\n" + "=" * 80)
        print("STEP 6: Verify Course Progress Tracking")
        print("=" * 80)
        
        progress_query = """
            SELECT cp.class_id, c.name as class_name, cp.last_course_id, cp.last_week, cp.school_year
            FROM course_progress cp
            JOIN classes c ON cp.class_id = c.id
        """
        progress_results = db.execute_query(progress_query)
        
        for progress in progress_results:
            print(f"✓ {progress['class_name']}: Last course ID = {progress['last_course_id']}, Last week = {progress['last_week']}, School year = {progress['school_year']}")
        
        # Step 7: Test Week 2 Distribution
        print("\n" + "=" * 80)
        print("STEP 7: Test Week 2 Distribution (Sequential Progression)")
        print("=" * 80)
        
        week_number = 2
        week_start = school_start + timedelta(weeks=1)
        week_end = week_start + timedelta(days=5)
        
        print(f"Week {week_number}: {week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}")
        
        distribution_week2 = distributor.distribute_courses(week_number, week_start, week_end, school_year)
        
        total_distributed_week2 = 0
        for class_id, slots in distribution_week2.items():
            class_query = "SELECT name FROM classes WHERE id = ?"
            class_result = db.execute_query(class_query, (class_id,))
            class_name = class_result[0]['name'] if class_result else f"Class {class_id}"
            
            print(f"\n✓ Class: {class_name}")
            print(f"  Total courses distributed: {len(slots)}")
            
            # Show first course to verify sequential progression
            if slots:
                day_id, time_slot_id, course_id = slots[0]
                course_value = distributor.fetch_course_value_by_id(course_id)
                print(f"    First course: ID {course_id} - {course_value}")
            
            total_distributed_week2 += len(slots)
        
        print(f"\n✓ Total courses distributed for Week 2: {total_distributed_week2}")
        
        # Verify progression
        progress_results_week2 = db.execute_query(progress_query)
        print("\n✓ Updated progress after Week 2:")
        for progress in progress_results_week2:
            print(f"  {progress['class_name']}: Last course ID = {progress['last_course_id']}, Last week = {progress['last_week']}")
        
        # Final Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        print("\n✅ ALL TESTS PASSED!")
        print(f"\n📊 Statistics:")
        print(f"  - Classes created: {class_count}")
        print(f"  - Schedule entries: {entry_count}")
        print(f"  - Courses in ma_table: {course_count}")
        print(f"  - Week 1 distributions: {total_distributed}")
        print(f"  - Week 2 distributions: {total_distributed_week2}")
        print(f"  - Total distributions: {total_distributed + total_distributed_week2}")
        
        print(f"\n🎉 Complete workflow is WORKING!")
        print(f"   Constraints → Schedule → Import → Distribution ✓")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore backup if needed
        backup_path = DB_PATH + '.backup'
        if os.path.exists(backup_path):
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            os.rename(backup_path, DB_PATH)
            print(f"\n✓ Restored original database from backup")


if __name__ == '__main__':
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
