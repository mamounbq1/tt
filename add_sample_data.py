#!/usr/bin/env python3
"""
Script to add sample data for testing the application
"""

import sqlite3
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.utils.config import DB_PATH

def add_sample_data():
    """Add sample classes and courses for testing"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📚 Adding Sample Data for Testing...")
    print("=" * 60)
    
    # Add sample classes
    classes = [
        ("6ème A", "Collège", "2025-2026"),
        ("6ème B", "Collège", "2025-2026"),
        ("5ème A", "Collège", "2025-2026"),
        ("5ème B", "Collège", "2025-2026"),
        ("4ème A", "Collège", "2025-2026"),
        ("3ème A", "Collège", "2025-2026"),
    ]
    
    print("\n📋 Adding Classes:")
    for name, level, year in classes:
        try:
            cursor.execute('''
                INSERT INTO classes (name, level, school_year)
                VALUES (?, ?, ?)
            ''', (name, level, year))
            print(f"  ✅ Added class: {name} ({level} - {year})")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Class already exists: {name}")
    
    # Add sample courses
    courses = [
        "Mathématiques - Algèbre",
        "Mathématiques - Géométrie",
        "Français - Grammaire",
        "Français - Littérature",
        "Sciences Physiques",
        "Sciences Naturelles",
        "Histoire-Géographie",
        "Anglais - Communication",
        "Anglais - Grammaire",
        "Education Physique",
        "Arts Plastiques",
        "Education Musicale",
        "Informatique",
        "Technologie",
        "Arabe - Langue",
        "Education Islamique",
    ]
    
    print("\n📚 Adding Courses to ma_table:")
    for course in courses:
        try:
            cursor.execute('''
                INSERT INTO ma_table (valeur)
                VALUES (?)
            ''', (course,))
            print(f"  ✅ Added course: {course}")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Course already exists: {course}")
    
    # Add sample modules
    modules = [
        ("Mathématiques", "Cours de mathématiques"),
        ("Français", "Cours de français"),
        ("Sciences", "Sciences physiques et naturelles"),
        ("Histoire-Géo", "Histoire et Géographie"),
        ("Langues", "Anglais et Arabe"),
        ("Arts & Sport", "Arts, musique et EPS"),
    ]
    
    print("\n📖 Adding Modules:")
    for name, desc in modules:
        try:
            cursor.execute('''
                INSERT INTO modules (name, description)
                VALUES (?, ?)
            ''', (name, desc))
            print(f"  ✅ Added module: {name}")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Module already exists: {name}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Successfully added sample data!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"  • Classes: {len(classes)}")
    print(f"  • Courses: {len(courses)}")
    print(f"  • Modules: {len(modules)}")
    print(f"  • Database: {DB_PATH}")
    print("\n🎉 Ready to test the application!")

if __name__ == "__main__":
    try:
        add_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
