# 🚀 Quick Start Guide - Cahier de Texte

## ✅ Step 1: Get Latest Code (2 minutes)

```bash
cd "D:\Genspark Cahier De Texte\tt-main\tt-fixed"
git pull origin genspark_ai_developer
```

---

## ✅ Step 2: Initialize Database (1 minute)

```bash
# Initialize all database tables
python -c "from src.core.db_manager import DatabaseManager; from src.utils.config import DB_PATH; DatabaseManager(db_name=DB_PATH)"
```

Expected output: Database initialized with 16 tables

---

## ✅ Step 3: Add Holidays (1 minute)

```bash
python add_school_holidays.py
```

Expected output:
```
🗓️  Adding 2025-2026 School Holidays and Vacations...
✅ Added 14 holidays
✅ Added 5 vacation periods
```

---

## ✅ Step 4: Add Sample Data (1 minute)

```bash
python add_sample_data.py
```

Expected output:
```
📚 Adding Sample Data for Testing...
✅ Added 6 classes
✅ Added 16 courses  
✅ Added 6 modules
```

---

## ✅ Step 5: Launch Application (10 seconds)

```bash
python main.py
```

**Expected:** Dashboard appears with 6 buttons

---

## 🎯 Step 6: Test Each Feature (20 minutes)

### **Test 1: View Holidays & Vacations**
```
1. Click: "⚙️ Ajouter des contraintes"
2. Click: "Jours Fériés" tab
3. Verify: You see 14 holidays
4. Click: "Vacances" tab  
5. Verify: You see 5 vacation periods
```

**✅ Success:** Holidays and vacations display correctly

---

### **Test 2: View Classes**
```
1. Still in "⚙️ Ajouter des contraintes"
2. Click: "Les Classes" tab
3. Verify: You see 6 classes (6ème A/B, 5ème A/B, 4ème A, 3ème A)
4. Try: Click "Ajouter Classe" to add a new class
5. Try: Select a class and click "Supprimer Classe"
```

**✅ Success:** Can view, add, and delete classes

---

### **Test 3: View Courses**
```
1. Click: "← Retour au tableau de bord"
2. Click: "📥 Importer contenu"
3. Verify: You see 16 courses in the tree view
4. Try: Search for "Math" in search box
5. Try: Click "Ajouter" to add a new course
6. Try: Select course and click "Modifier"
```

**✅ Success:** Can view, search, add, edit courses

---

### **Test 4: Course Distribution (Main Feature!)**
```
1. Click: "← Retour au tableau de bord"
2. Click: "📚 Distribuer les cours"
3. Verify: Weekly schedule interface appears
4. Select: A week from dropdown
5. Click: "Reload" or "Distribute" button
6. Verify: Schedule populates with courses
7. Check: Vacation days show "VACANCES"
```

**✅ Success:** Course distribution works and respects holidays/vacations

---

### **Test 5: Schedule Grid**
```
1. Click: "← Retour au tableau de bord"
2. Click: "📅 Emploi du temps"
3. Verify: Empty schedule grid appears
4. Try: Click an empty cell to add a class
5. Try: Click a filled cell to edit/delete
6. Try: Click "PDF" export button
```

**✅ Success:** Can create and modify schedules manually

---

### **Test 6: Saved Schedules**
```
1. Click: "← Retour au tableau de bord"
2. Click: "🖨️ Imprimer l'état"
3. Verify: List of saved schedules appears
4. Try: Export a schedule to PDF
```

**✅ Success:** Can view and print saved schedules

---

## 🐛 If You See Errors

### **Error Type 1: Import Error**
```
ModuleNotFoundError: No module named 'X'
```

**Solution:**
```bash
pip install reportlab openpyxl tkcalendar
```

---

### **Error Type 2: Database Error**
```
sqlite3.OperationalError: no such table: X
```

**Solution:** Re-run database initialization
```bash
python -c "from src.core.db_manager import DatabaseManager; from src.utils.config import DB_PATH; DatabaseManager(db_name=DB_PATH)"
```

---

### **Error Type 3: Week Loading Error**
```
_load_weeks: raw saved_weeks = [(0, 'Erreur de récupération')]
```

**This is normal!** It means no weeks have been saved yet. 
- Use "📚 Distribuer les cours" to create weekly schedules
- They will then appear in saved weeks

---

## 📊 Quick Verification Checklist

After running all setup steps, verify:

- [ ] App launches without errors
- [ ] Dashboard shows 6 buttons
- [ ] Can navigate between screens
- [ ] Holidays tab shows 14 entries
- [ ] Vacations tab shows 5 periods
- [ ] Classes tab shows 6 classes
- [ ] Import content shows 16 courses
- [ ] Course distribution interface loads
- [ ] Schedule grid is interactive

---

## 🎯 What To Do Next

### **Option A: Start Using for Real**
1. Add your actual classes (via "⚙️ Ajouter des contraintes" → "Les Classes")
2. Add your actual courses (via "📥 Importer contenu")
3. Use "📚 Distribuer les cours" to auto-generate schedules
4. Adjust manually with "📅 Emploi du temps"
5. Export PDFs with "🖨️ Imprimer l'état"

### **Option B: Keep Testing**
1. Test each button thoroughly
2. Report any bugs/errors you find
3. I'll fix them immediately
4. Then move to real usage

### **Option C: Customize**
1. Add more classes
2. Import Excel file with your courses
3. Add teacher absences
4. Adjust holidays/vacations as needed

---

## 💡 Pro Tips

### **Faster Data Entry:**
- Use Excel to prepare course lists, then import
- Use "Distribuer les cours" for automatic scheduling
- Use search in "Import content" to find courses quickly

### **Vacation Handling:**
- Course distribution automatically skips vacations
- Vacation cells show merged "VACANCES" text
- PDF exports include vacation indicators

### **PDF Export:**
- Use "🖨️ Imprimer l'état" for weekly reports
- Use "📅 Emploi du temps" → Export for custom schedules
- PDFs are formatted for printing

---

## 🆘 Need Help?

If you encounter any issues:

1. **Check the logs:**
   - `logs/error_YYYYMMDD.log` - Error messages
   - `logs/debug_YYYYMMDD.log` - Debug info
   - `cahier_texte.log` - Course distribution logs

2. **Share the error:**
   - Copy the full error message
   - Include which button you clicked
   - Tell me what you were trying to do

3. **I'll fix it immediately!** 🚀

---

## ✅ Success Criteria

You're ready to use the app officially when:

- ✅ All 6 buttons work without errors
- ✅ You can navigate between all screens
- ✅ Course distribution creates schedules
- ✅ Schedules respect holidays/vacations
- ✅ You can add/edit/delete data
- ✅ PDF export works

---

**Let's get started!** Run the 5 setup steps above and report back! 🎉
