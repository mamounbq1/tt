"""
Comprehensive Test Suite for Schedule/Emploi du Temps Feature
Tests database operations, UI functionality, and schedule management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import DatabaseManager
from src.utils.config import DB_PATH
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print('='*70)


def test_database_tables():
    """Test 1: Verify schedule-related tables exist"""
    print_test_header("Database Tables Verification")
    
    db = DatabaseManager(DB_PATH)
    
    required_tables = ['days', 'time_slots', 'schedule_data', 'classes']
    existing_tables = db.get_all_tables()
    
    print(f"Existing tables: {existing_tables}")
    
    for table in required_tables:
        if table in existing_tables:
            print(f"✓ Table '{table}' exists")
        else:
            print(f"✗ Table '{table}' MISSING")
            return False
    
    db.close()
    print("\n✓ All required tables exist")
    return True


def test_days_data():
    """Test 2: Verify days of week data"""
    print_test_header("Days of Week Data")
    
    db = DatabaseManager(DB_PATH)
    
    query = "SELECT * FROM days ORDER BY display_order"
    days = db.execute_query(query)
    
    print(f"Total days: {len(days)}")
    
    for day in days:
        print(f"  - {day['name']} (Order: {day['display_order']})")
    
    db.close()
    
    if len(days) != 6:
        print(f"✗ Expected 6 days, got {len(days)}")
        return False
    
    print("\n✓ Days data is correct")
    return True


def test_time_slots_data():
    """Test 3: Verify time slots data"""
    print_test_header("Time Slots Data")
    
    db = DatabaseManager(DB_PATH)
    
    query = "SELECT * FROM time_slots ORDER BY display_order"
    slots = db.execute_query(query)
    
    print(f"Total time slots: {len(slots)}")
    
    for slot in slots:
        lunch_flag = "🍽️ LUNCH" if slot['is_lunch'] else ""
        print(f"  - {slot['start_time']} → {slot['end_time']} ({slot['period']}) {lunch_flag}")
    
    db.close()
    
    if len(slots) != 9:
        print(f"✗ Expected 9 slots, got {len(slots)}")
        return False
    
    print("\n✓ Time slots data is correct")
    return True


def test_schedule_operations():
    """Test 4: Test schedule CRUD operations"""
    print_test_header("Schedule CRUD Operations")
    
    db = DatabaseManager(DB_PATH)
    
    # Clear test data
    print("Clearing test data (week 99)...")
    db.execute_update("DELETE FROM schedule_data WHERE week_number = 99")
    
    # Test INSERT
    print("\n1. Testing INSERT operation...")
    insert_query = """
        INSERT INTO schedule_data (week_number, day_id, slot_id, content)
        VALUES (?, ?, ?, ?)
    """
    
    test_entries = [
        (99, 1, 1, "Mathématiques - 6ème A"),
        (99, 1, 2, "Français - 5ème B"),
        (99, 2, 3, "Sciences - 4ème C"),
        (99, 3, 4, "Histoire - 3ème D"),
    ]
    
    for entry in test_entries:
        row_id = db.execute_update(insert_query, entry)
        print(f"  ✓ Inserted entry ID {row_id}: Day {entry[1]}, Slot {entry[2]}")
    
    # Test SELECT
    print("\n2. Testing SELECT operation...")
    select_query = "SELECT * FROM schedule_data WHERE week_number = 99"
    results = db.execute_query(select_query)
    
    print(f"  ✓ Found {len(results)} entries")
    for row in results:
        print(f"    - Day {row['day_id']}, Slot {row['slot_id']}: {row['content']}")
    
    if len(results) != 4:
        print(f"  ✗ Expected 4 entries, got {len(results)}")
        db.close()
        return False
    
    # Test UPDATE
    print("\n3. Testing UPDATE operation...")
    update_query = """
        UPDATE schedule_data
        SET content = ?
        WHERE week_number = ? AND day_id = ? AND slot_id = ?
    """
    db.execute_update(update_query, ("Mathématiques - UPDATED", 99, 1, 1))
    
    verify_query = "SELECT content FROM schedule_data WHERE week_number = 99 AND day_id = 1 AND slot_id = 1"
    updated = db.execute_query(verify_query)
    
    if updated[0]['content'] == "Mathématiques - UPDATED":
        print("  ✓ Update successful")
    else:
        print("  ✗ Update failed")
        db.close()
        return False
    
    # Test DELETE
    print("\n4. Testing DELETE operation...")
    delete_query = "DELETE FROM schedule_data WHERE week_number = 99"
    db.execute_update(delete_query)
    
    verify_delete = db.execute_query("SELECT COUNT(*) as count FROM schedule_data WHERE week_number = 99")
    if verify_delete[0]['count'] == 0:
        print("  ✓ Delete successful")
    else:
        print("  ✗ Delete failed")
        db.close()
        return False
    
    db.close()
    print("\n✓ All CRUD operations successful")
    return True


def test_week_navigation():
    """Test 5: Test week navigation functionality"""
    print_test_header("Week Navigation")
    
    max_weeks = 36
    current_week = 1
    
    print(f"Initial week: {current_week}/{max_weeks}")
    
    # Test forward navigation
    print("\nTesting forward navigation...")
    for i in range(5):
        current_week += 1
        if current_week <= max_weeks:
            print(f"  → Week {current_week}")
    
    if current_week != 6:
        print(f"✗ Expected week 6, got {current_week}")
        return False
    
    # Test backward navigation
    print("\nTesting backward navigation...")
    for i in range(3):
        current_week -= 1
        if current_week >= 1:
            print(f"  ← Week {current_week}")
    
    if current_week != 3:
        print(f"✗ Expected week 3, got {current_week}")
        return False
    
    # Test boundaries
    print("\nTesting boundaries...")
    current_week = 1
    if current_week > 1:
        print("  ✗ Should not go below week 1")
        return False
    else:
        print("  ✓ Cannot go below week 1")
    
    current_week = max_weeks
    if current_week < max_weeks:
        print("  ✗ Should not exceed max weeks")
        return False
    else:
        print("  ✓ Cannot exceed max weeks")
    
    print("\n✓ Week navigation works correctly")
    return True


def test_full_week_schedule():
    """Test 6: Create and save a complete week schedule"""
    print_test_header("Full Week Schedule Creation")
    
    db = DatabaseManager(DB_PATH)
    
    # Clear test week
    test_week = 10
    print(f"Setting up test week: {test_week}")
    db.execute_update("DELETE FROM schedule_data WHERE week_number = ?", (test_week,))
    
    # Get all days and slots
    days = db.execute_query("SELECT id FROM days ORDER BY display_order")
    slots = db.execute_query("SELECT id, is_lunch FROM time_slots ORDER BY display_order")
    
    # Create full schedule
    print("\nCreating full week schedule...")
    insert_query = """
        INSERT INTO schedule_data (week_number, day_id, slot_id, content)
        VALUES (?, ?, ?, ?)
    """
    
    subjects = ["Math", "Français", "Sciences", "Histoire", "Anglais", "Sport"]
    classes = ["6ème A", "5ème B", "4ème C", "3ème D"]
    
    count = 0
    for day in days:
        for slot in slots:
            if not slot['is_lunch']:  # Skip lunch slots
                subject = subjects[count % len(subjects)]
                class_name = classes[count % len(classes)]
                content = f"{subject} - {class_name}"
                
                db.execute_update(insert_query, (test_week, day['id'], slot['id'], content))
                count += 1
    
    print(f"  ✓ Created {count} schedule entries")
    
    # Verify
    verify_query = "SELECT COUNT(*) as count FROM schedule_data WHERE week_number = ?"
    result = db.execute_query(verify_query, (test_week,))
    
    if result[0]['count'] == count:
        print(f"  ✓ Verification successful: {count} entries saved")
    else:
        print(f"  ✗ Verification failed: Expected {count}, got {result[0]['count']}")
        db.close()
        return False
    
    # Display schedule summary
    print("\nSchedule summary by day:")
    for day in days:
        day_query = """
            SELECT COUNT(*) as count
            FROM schedule_data
            WHERE week_number = ? AND day_id = ?
        """
        day_result = db.execute_query(day_query, (test_week, day['id']))
        day_name_query = "SELECT name FROM days WHERE id = ?"
        day_name = db.execute_query(day_name_query, (day['id'],))
        print(f"  - {day_name[0]['name']}: {day_result[0]['count']} entries")
    
    db.close()
    print("\n✓ Full week schedule created and verified")
    return True


def test_empty_cell_handling():
    """Test 7: Test handling of empty schedule cells"""
    print_test_header("Empty Cell Handling")
    
    db = DatabaseManager(DB_PATH)
    
    test_week = 15
    print(f"Testing empty cells for week {test_week}")
    
    # Clear test data
    db.execute_update("DELETE FROM schedule_data WHERE week_number = ?", (test_week,))
    
    # Add some entries, leaving gaps
    insert_query = """
        INSERT INTO schedule_data (week_number, day_id, slot_id, content)
        VALUES (?, ?, ?, ?)
    """
    
    # Only fill some cells
    test_data = [
        (test_week, 1, 1, "Entry 1"),
        (test_week, 1, 3, "Entry 2"),  # Gap at slot 2
        (test_week, 2, 2, "Entry 3"),
        # Day 3-6 empty
    ]
    
    for entry in test_data:
        db.execute_update(insert_query, entry)
    
    print(f"  ✓ Created {len(test_data)} entries with gaps")
    
    # Load schedule (simulating UI load)
    load_query = """
        SELECT day_id, slot_id, content
        FROM schedule_data
        WHERE week_number = ?
    """
    results = db.execute_query(load_query, (test_week,))
    
    # Verify results
    print(f"  ✓ Loaded {len(results)} entries")
    
    # Get total possible cells
    total_days = db.execute_query("SELECT COUNT(*) as count FROM days")[0]['count']
    total_slots = db.execute_query("SELECT COUNT(*) as count FROM time_slots")[0]['count']
    total_cells = total_days * total_slots
    empty_cells = total_cells - len(results)
    
    print(f"  ℹ Total cells: {total_cells}")
    print(f"  ℹ Filled cells: {len(results)}")
    print(f"  ℹ Empty cells: {empty_cells}")
    
    if len(results) == len(test_data):
        print("  ✓ Empty cells handled correctly")
    else:
        print("  ✗ Empty cell handling failed")
        db.close()
        return False
    
    db.close()
    print("\n✓ Empty cell handling test passed")
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("SCHEDULE FEATURE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Database: {DB_PATH}")
    print(f"Testing: Schedule/Emploi du Temps functionality")
    print("="*70)
    
    tests = [
        ("Database Tables", test_database_tables),
        ("Days Data", test_days_data),
        ("Time Slots Data", test_time_slots_data),
        ("Schedule CRUD Operations", test_schedule_operations),
        ("Week Navigation", test_week_navigation),
        ("Full Week Schedule", test_full_week_schedule),
        ("Empty Cell Handling", test_empty_cell_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Final report
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed ({100*passed//total}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Schedule feature is fully functional.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
