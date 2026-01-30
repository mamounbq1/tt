#!/usr/bin/env python3
"""
Script to add 2025-2026 school year holidays and vacations to the database
Based on the official school calendar (منقير رقم 1)
"""

import sqlite3
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.utils.config import DB_PATH

def add_holidays_and_vacations():
    """Add all holidays and vacations from the 2025-2026 school calendar"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🗓️  Adding 2025-2026 School Holidays and Vacations...")
    print("=" * 60)
    
    # Clear existing data for 2025-2026 school year
    cursor.execute("DELETE FROM jours_feries WHERE date >= '2025-09-01' AND date <= '2026-07-15'")
    cursor.execute("DELETE FROM vacances WHERE start_date >= '2025-09-01' AND end_date <= '2026-07-15'")
    print("✅ Cleared existing 2025-2026 holidays and vacations")
    
    # Single-day holidays (jours_feries)
    holidays = [
        # Row 1: عطلة المولد النبوي الشريف (Prophet's Birthday)
        # 12 و13 ربيع الأول 1447 = September 14-15, 2025 (approximate)
        ('2025-09-14', 'عطلة المولد النبوي الشريف - يوم 1'),
        ('2025-09-15', 'عطلة المولد النبوي الشريف - يوم 2'),
        
        # Row 3: ذكرى المسيرة الخضراء (Green March Anniversary)
        ('2025-11-06', 'ذكرى المسيرة الخضراء'),
        
        # Row 4: عيد الاستقلال (Independence Day)
        ('2025-11-18', 'عيد الاستقلال'),
        
        # Row 6: فاتح السنة الميلادية (New Year)
        ('2026-01-01', 'فاتح السنة الميلادية'),
        
        # Row 8: ذكرى تقديم وثيقة الاستقلال (Independence Manifesto)
        ('2026-01-11', 'ذكرى تقديم وثيقة الاستقلال'),
        
        # Row 11: عيد الفطر (Eid al-Fitr) - approximate dates
        # 29 رمضان - 2 شوال 1447 = March 30 - April 2, 2026
        ('2026-03-30', 'عيد الفطر - يوم 1'),
        ('2026-03-31', 'عيد الفطر - يوم 2'),
        ('2026-04-01', 'عيد الفطر - يوم 3'),
        ('2026-04-02', 'عيد الفطر - يوم 4'),
        
        # Row 13: عيد الأضحى (Eid al-Adha)
        # 10 و11 ذي الحجة 1447 = June 6-7, 2026 (approximate)
        ('2026-06-06', 'عيد الأضحى - يوم 1'),
        ('2026-06-07', 'عيد الأضحى - يوم 2'),
        
        # Row 14: رأس السنة الهجرية (Islamic New Year)
        # 1 محرم 1448 = June 27, 2026 (approximate)
        ('2026-06-27', 'رأس السنة الهجرية 1448'),
        
        # Row 10: عيد الشغل (Labor Day)
        ('2026-05-01', 'عيد الشغل'),
    ]
    
    for date, label in holidays:
        try:
            cursor.execute('''
                INSERT INTO jours_feries (date, label)
                VALUES (?, ?)
            ''', (date, label))
            print(f"  ✅ Added holiday: {label} ({date})")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Holiday already exists: {label}")
    
    print("\n" + "=" * 60)
    
    # Vacation periods (vacances)
    vacations = [
        # Row 2: العطلة البينية الأولى (First Break)
        ('2025-10-19', '2025-10-26', 'العطلة البينية الأولى'),
        
        # Row 5: العطلة البينية الثانية (Second Break)
        ('2025-12-07', '2025-12-14', 'العطلة البينية الثانية'),
        
        # Row 7: عطلة نصف السنة الدراسية (Mid-Year Break)
        ('2026-01-11', '2026-01-18', 'عطلة نصف السنة الدراسية'),
        
        # Row 9: العطلة البينية الثالثة (Third Break)
        ('2026-03-22', '2026-03-29', 'العطلة البينية الثالثة'),
        
        # Row 12: العطلة البينية الرابعة (Fourth Break) 
        ('2026-05-03', '2026-05-12', 'العطلة البينية الرابعة'),
    ]
    
    for start_date, end_date, label in vacations:
        try:
            cursor.execute('''
                INSERT INTO vacances (start_date, end_date, label)
                VALUES (?, ?, ?)
            ''', (start_date, end_date, label))
            print(f"  ✅ Added vacation: {label} ({start_date} → {end_date})")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Vacation already exists: {label}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Successfully added all 2025-2026 holidays and vacations!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"  • Single-day holidays: {len(holidays)} days")
    print(f"  • Vacation periods: {len(vacations)} periods")
    print(f"  • Database: {DB_PATH}")
    print("\n🎉 Ready to use in the application!")

if __name__ == "__main__":
    try:
        add_holidays_and_vacations()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
