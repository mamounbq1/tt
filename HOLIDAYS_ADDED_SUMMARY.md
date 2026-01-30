# ✅ 2025-2026 School Holidays & Vacations Added!

## 🎉 What Was Done

All official holidays and vacation periods from the Moroccan school calendar (2025-2026) have been added to the database.

## 📅 Holidays Added (14 days)

### Religious Holidays:
1. **عطلة المولد النبوي الشريف** (Prophet's Birthday)
   - September 14-15, 2025 (2 days)

2. **عيد الفطر** (Eid al-Fitr)
   - March 30 - April 2, 2026 (4 days)

3. **عيد الأضحى** (Eid al-Adha)
   - June 6-7, 2026 (2 days)

4. **رأس السنة الهجرية** (Islamic New Year 1448)
   - June 27, 2026 (1 day)

### National Holidays:
5. **ذكرى المسيرة الخضراء** (Green March Anniversary)
   - November 6, 2025 (1 day)

6. **عيد الاستقلال** (Independence Day)
   - November 18, 2025 (1 day)

7. **ذكرى تقديم وثيقة الاستقلال** (Independence Manifesto Day)
   - January 11, 2026 (1 day)

### International Holidays:
8. **فاتح السنة الميلادية** (New Year's Day)
   - January 1, 2026 (1 day)

9. **عيد الشغل** (Labor Day)
   - May 1, 2026 (1 day)

---

## 🏖️ Vacation Periods Added (5 periods)

1. **العطلة البينية الأولى** (First Inter-term Break)
   - October 19-26, 2025 (8 days)

2. **العطلة البينية الثانية** (Second Inter-term Break)
   - December 7-14, 2025 (8 days)

3. **عطلة نصف السنة الدراسية** (Mid-Year Break)
   - January 11-18, 2026 (8 days)

4. **العطلة البينية الثالثة** (Third Inter-term Break)
   - March 22-29, 2026 (8 days)

5. **العطلة البينية الرابعة** (Fourth Inter-term Break)
   - May 3-12, 2026 (10 days)

---

## 🔧 Technical Details

### Script Created: `add_school_holidays.py`

This script:
- ✅ Connects to the database
- ✅ Clears existing 2025-2026 data (if any)
- ✅ Adds 14 holidays to `jours_feries` table
- ✅ Adds 5 vacation periods to `vacances` table
- ✅ Verifies all data was added correctly

### Database Tables:

**`jours_feries` (Holidays)**
```sql
CREATE TABLE jours_feries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    label TEXT NOT NULL
);
```

**`vacances` (Vacations)**
```sql
CREATE TABLE vacances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    label TEXT NOT NULL
);
```

---

## 📊 How To Run

### First Time Setup:
```bash
cd "D:\Genspark Cahier De Texte\tt-main\tt-fixed"
git pull origin genspark_ai_developer

# Initialize database (if needed)
python -c "from src.core.db_manager import DatabaseManager; from src.utils.config import DB_PATH; DatabaseManager(db_name=DB_PATH)"

# Add holidays
python add_school_holidays.py
```

### Verify Data:
```bash
python -c "
import sqlite3
from src.utils.config import DB_PATH
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM jours_feries')
print(f'Holidays: {cursor.fetchone()[0]}')
cursor.execute('SELECT COUNT(*) FROM vacances')
print(f'Vacations: {cursor.fetchone()[0]}')
conn.close()
"
```

Expected output:
```
Holidays: 14
Vacations: 5
```

---

## 🎯 Impact on Application

### Course Distribution Algorithm:
The `CourseDistributionManager` will now:
- ✅ **Skip holidays** - No courses scheduled on public holidays
- ✅ **Skip vacations** - No courses during vacation periods
- ✅ **Show vacation cells** - Schedule grid displays "VACANCES" for vacation days
- ✅ **Accurate planning** - Respects the official school calendar

### UI Features:
- **Schedule Grid**: Vacation cells merged and highlighted
- **Constraints Tab**: View/edit holidays and vacations
- **PDF Export**: Vacation periods shown in printed schedules

---

## 📝 Data Source

Holidays and vacations extracted from:
- **Document**: منقير رقم 1
- **Title**: لائحة العطل بالتعليم الإبتدائي والثانوي الإعدادي والثانوي التأهيلي برسم السنة الدراسية 2025/2026
- **Authority**: Moroccan Ministry of Education

---

## 🔗 GitHub

- **Commit**: `afcfd35`
- **Branch**: `genspark_ai_developer`
- **Pull Request**: https://github.com/mamounbq1/tt/pull/1

---

## ✅ Next Steps

1. **Test the application**: `python main.py`
2. **View holidays**: Click "⚙️ Ajouter des contraintes" → "Jours Fériés" tab
3. **View vacations**: Click "⚙️ Ajouter des contraintes" → "Vacances" tab
4. **Test course distribution**: Verify courses skip holidays/vacations

---

**All set! The application now has the complete 2025-2026 school calendar!** 🎉
