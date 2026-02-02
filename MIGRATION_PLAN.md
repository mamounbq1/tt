# 🔄 Migration Plan: Implement Old App's Distribution Logic

## 📋 **Analysis of Old App**

### **Key Differences Found**:

1. **`ma_table` instead of `courses`**:
   - Old app: `ma_table (id, valeur)` - stores course content
   - New app: `courses (id, content, class_id, subject)` - more fields

2. **`schedule_entries` table**:
   - Defines FIXED class schedules (which class is in which slot)
   - Used as template for course distribution
   - Schema: `(day_id, time_slot_id, class_id)`

3. **`class_course_progress` table**:
   - Tracks progression: which course each class is currently on
   - Schema: `(class_id, last_course_id, last_week, year)`
   - Enables sequential course assignment

4. **Smart Distribution Algorithm**:
   - Uses `schedule_entries` as template
   - Assigns next course from `ma_table` sequentially
   - Checks constraints: holidays, vacations, absences
   - Skips lunch breaks automatically
   - Tracks progression per class

## 🎯 **Migration Tasks**

### **Task 1: Update Database Schema** ✓

Add these tables:

```sql
-- Rename courses to ma_table (or create alias)
CREATE TABLE IF NOT EXISTS ma_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valeur TEXT NOT NULL  -- course content
);

-- Add schedule_entries table (fixed class schedule template)
CREATE TABLE IF NOT EXISTS schedule_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_id INTEGER NOT NULL,
    time_slot_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    UNIQUE(day_id, time_slot_id, class_id),
    FOREIGN KEY (day_id) REFERENCES days(id),
    FOREIGN KEY (time_slot_id) REFERENCES time_slots(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Update class_course_progress (already exists, add year field)
ALTER TABLE course_progress ADD COLUMN year INTEGER DEFAULT 2025;
```

### **Task 2: Update Distribution Algorithm** ✓

Implement from `course_distribution.py`:

```python
class CourseDistributionManager:
    def distribute_courses(self, week_number, week_start, week_end):
        # 1. Get all classes
        # 2. For each scheduled slot in schedule_entries:
        #    a. Check if day is holiday/vacation/absence
        #    b. Get next course for the class from ma_table
        #    c. Track progression in class_course_progress
        #    d. Assign course_id to schedule_data
        # 3. Return distribution map
```

**Key methods**:
- `get_next_course(class_id, week_number, appearance_count, year)`
- `is_day_in_vacation(date, vacation_periods)`
- `get_valid_slots(week_number)` - excludes holidays, vacations, lunch
- `distribute_courses(week_number, week_start, week_end)`

### **Task 3: Update Schedule UI** ✓

Changes needed:
- Display class name above course content
- Show course content from `ma_table` via `course_id`
- Join: `schedule_data → ma_table → classes`

Display format:
```
┌─────────────┐
│   Class 6A  │  ← class name (bold)
├─────────────┤
│ Lesson 5:   │  ← course content from ma_table
│ Triangles   │
└─────────────┘
```

### **Task 4: Add Schedule Template UI** ✓

New feature: **Configure Fixed Schedule**
- Before distribution, define which classes are scheduled when
- Edit `schedule_entries` table
- UI: Grid where you assign classes to time slots

## 📝 **Implementation Steps**

### **Step 1: Database Migration**

```python
# Add to database.py create_schema()

# Add ma_table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ma_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valeur TEXT NOT NULL
    )
""")

# Add schedule_entries
cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedule_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_id INTEGER NOT NULL,
        time_slot_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        UNIQUE(day_id, time_slot_id, class_id),
        FOREIGN KEY (day_id) REFERENCES days(id),
        FOREIGN KEY (time_slot_id) REFERENCES time_slots(id),
        FOREIGN KEY (class_id) REFERENCES classes(id)
    )
""")

# Update course_progress table
cursor.execute("""
    ALTER TABLE course_progress ADD COLUMN year INTEGER DEFAULT 2025
""")
```

### **Step 2: Create Distribution Manager**

Create `/home/user/webapp-v2/src/core/distribution.py`:
- Port logic from old `course_distribution.py`
- Adapt to new table structure
- Keep constraint checking logic

### **Step 3: Update Distribution UI**

Update `/home/user/webapp-v2/src/ui/distribution.py`:
- Add "Configure Schedule Template" button
- Show dialog to assign classes to slots
- Save to `schedule_entries`
- Use new distribution algorithm

### **Step 4: Update Schedule Display**

Update `/home/user/webapp-v2/src/ui/schedule.py`:
- Query: JOIN schedule_data with ma_table and classes
- Display class name + course content
- Format properly

### **Step 5: Add Course Management**

New UI for managing `ma_table`:
- Add courses (sequential lessons)
- Edit course content
- View all courses
- Delete courses

## 🔍 **Key Algorithm Logic**

### **Sequential Course Assignment**:

```python
def get_next_course(class_id, week_number, appearance_count, year):
    # 1. Get last course this class was on
    last_course_id = get_from_class_course_progress(class_id, year, week_number)
    
    # 2. Get all courses from ma_table in order
    courses = get_all_courses_ordered()
    
    # 3. Find index of last course
    last_index = courses.index(last_course_id) if last_course_id else -1
    
    # 4. Calculate next course index
    next_index = last_index + appearance_count + 1
    
    # 5. Return next course (or None if end of list)
    return courses[next_index] if next_index < len(courses) else None
```

### **Distribution Flow**:

```
1. Get week dates (start, end)
2. Get all classes
3. For each day in week:
    a. Check if holiday → skip
    b. Check if vacation → skip
    c. Check if absence → skip
    d. For each time slot:
        i. Skip if lunch break
        ii. Get classes from schedule_entries for this slot
        iii. For each class:
            - Get next course
            - Save to schedule_data
            - Update class_course_progress
```

## 📊 **Database Schema Comparison**

| Table | Old App | New App | Action |
|-------|---------|---------|--------|
| **ma_table** | ✓ (id, valeur) | ✗ | **ADD** |
| **courses** | ✗ | ✓ (id, content, ...) | Keep (different purpose) |
| **schedule_entries** | ✓ | ✗ | **ADD** |
| **schedule_data** | ✓ (with course_id) | ✓ (with content) | **UPDATE** |
| **class_course_progress** | ✓ (with year) | ✓ (no year) | **UPDATE** |

## 🎯 **Expected Result**

After implementation:
1. **Configure** fixed class schedule (schedule_entries)
2. **Add** course content to ma_table (Lesson 1, 2, 3...)
3. **Distribute** → automatically assigns next course to each class
4. **View** schedule showing class name + current lesson
5. **Progression** tracked across weeks/years

## 📝 **Status**

- ✅ Analysis complete
- ⏳ Database migration needed
- ⏳ Distribution algorithm needs porting
- ⏳ UI updates needed
- ⏳ Testing required

---

**Next Action**: Start implementing database schema changes
