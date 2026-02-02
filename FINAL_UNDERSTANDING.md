# Compréhension Finale - Architecture Distribution

## ✅ COMPRÉHENSION 100% CORRECTE

Après relecture complète de l'ancienne application, voici l'architecture exacte :

## 📁 DEUX FICHIERS DISTINCTS

### 1. schedule.py (EmploiDuTempsApp) - EMPLOI DU TEMPS FIXE
**Rôle** : Définir l'emploi du temps hebdomadaire FIXE (ne change JAMAIS, réutilisé chaque semaine)

**Table** : `schedule_entries`
```sql
CREATE TABLE schedule_entries (
    entry_id INTEGER PRIMARY KEY,
    class_id INTEGER,
    day_id INTEGER,        -- 1-6 (Lundi-Samedi)
    time_slot_id INTEGER,  -- 1-9 (08:30-09:30, ..., 17:30-18:30)
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(day_id, time_slot_id)
)
```

**Affichage** :
```
┌─────────────────────────┐
│        6ème A           │  ← Nom de la classe
│   6ème - 2024-2025      │  ← Niveau + Année scolaire
└─────────────────────────┘
```

**Actions** :
- Clic sur cellule vide → Dialog pour sélectionner une classe → INSERT INTO schedule_entries
- Clic sur cellule remplie → Menu popup → Modifier ou Supprimer
- Bouton "Recharger" → Charger schedule_entries depuis la DB
- Bouton "Sauvegarder" → INSERT/UPDATE schedule_entries
- Bouton "Imprimer PDF" → Générer un PDF de l'emploi du temps fixe

**Mapping row/col** :
- Morning slots (rows 1-4) : 08:30-09:30, 09:30-10:30, 10:30-11:30, 11:30-12:30
- Lunch break (row 5) : Séparateur
- Afternoon slots (rows 6-9) : 14:30-15:30, 15:30-16:30, 16:30-17:30, 17:30-18:30
- Columns 0-5 : Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi

### 2. cahier_texte.py (CahierTextApp) - DISTRIBUTION HEBDOMADAIRE
**Rôle** : Afficher et éditer la distribution hebdomadaire des cours

**Tables** :
- `schedule_entries` (lecture seule) : Pour afficher les noms de classe
- `schedule_data` (écriture) : Pour sauvegarder les contenus des cours
- `ma_table` (lecture) : Pour distribuer automatiquement

```sql
CREATE TABLE schedule_data (
    id INTEGER PRIMARY KEY,
    week_number INTEGER,
    cell_row INTEGER,    -- Position dans la grille UI (2-13)
    cell_col INTEGER,    -- Position dans la grille UI (1-6)
    value TEXT,          -- CONTENU DU COURS (PAS le nom de la classe!)
    created_at TIMESTAMP
)
```

**Affichage** :
```
┌─────────────────────────┐
│        6ème A           │  ← Nom de classe (lecture seule, depuis schedule_entries)
│   Les fractions         │  ← Contenu du cours (éditable, depuis schedule_data)
└─────────────────────────┘
```

**Actions** :
- Sélectionner une semaine dans un combobox
- Bouton "Distribuer" → Appeler distribute_courses() pour remplir automatiquement
- Éditer le contenu d'une cellule
- Bouton "Sauvegarder" → INSERT INTO schedule_data (week_number, cell_row, cell_col, value)
- Bouton "Recharger" → Charger schedule_data pour la semaine sélectionnée

**Mapping cell_row/cell_col** :
- cell_row : 2-5 (matinée), 7-10 (après-midi) - correspond aux lignes UI
- cell_col : 1-6 (Lundi-Samedi) - correspond aux colonnes UI

**Algorithme de distribution** :
1. Charger schedule_entries pour savoir quelles classes sont prévues
2. Pour chaque créneau (day_id, time_slot_id) dans schedule_entries :
   - Vérifier si jour férié / vacances / absence → Skip
   - Vérifier si pause déjeuner → Skip
   - Récupérer la classe (class_id)
   - Appeler get_next_course(class_id) → Retourne course_id
   - Récupérer course_value depuis ma_table WHERE id = course_id
   - Calculer cell_row et cell_col depuis (day_id, time_slot_id)
   - Afficher dans la grille : class_name en haut, course_value en bas
3. L'utilisateur peut éditer les contenus
4. Sauvegarder → INSERT INTO schedule_data (week_number, cell_row, cell_col, value)

## 🔑 POINTS CLÉS

### 1. Deux grilles distinctes, même layout
- schedule.py : Grille pour définir l'emploi du temps FIXE
- cahier_texte.py : Grille pour distribuer et éditer les cours HEBDOMADAIRES

### 2. schedule_entries = FIXE, schedule_data = HEBDOMADAIRE
- schedule_entries : Utilisé par schedule.py ET cahier_texte.py (lecture seule)
- schedule_data : Utilisé uniquement par cahier_texte.py (écriture)

### 3. Mapping row/col → day_id/time_slot_id
```python
# Dans schedule.py
if row <= 4:  # Morning
    time_slot = morning_slots[row - 1]  # row 1-4 → index 0-3
else:         # Afternoon
    time_slot = afternoon_slots[row - 6]  # row 6-9 → index 0-3
```

### 4. Mapping day_id/time_slot_id → cell_row/cell_col
```python
# Dans cahier_texte.py
# cell_row : 2 (08:30), 3 (09:30), 4 (10:30), 5 (11:30),
#            7 (14:30), 8 (15:30), 9 (16:30), 10 (17:30)
# cell_col : 1 (Lundi), 2 (Mardi), 3 (Mercredi), 4 (Jeudi), 5 (Vendredi), 6 (Samedi)
```

### 5. Distribution automatique
- distribute_courses() retourne : `{class_id: [(day_id, time_slot_id, course_id), ...]}`
- Pour afficher : Récupérer course_value depuis ma_table WHERE id = course_id
- Pour sauvegarder : INSERT INTO schedule_data (week_number, cell_row, cell_col, course_value)

## 🎯 PROCHAINES ÉTAPES

1. ✅ Analyser l'ancienne application (FAIT)
2. ✅ Comprendre l'architecture (FAIT)
3. ✅ Identifier les erreurs dans l'implémentation actuelle (FAIT)
4. 🔜 Réécrire schedule.py basé sur EmploiDuTempsApp
5. 🔜 Créer cahier_texte.py basé sur CahierTextApp
6. 🔜 Adapter distribution.py pour déclencher la distribution
7. 🔜 Tests complets du workflow
8. 🔜 Commit et push

## 📚 RÉFÉRENCES

- Ancienne app : `/home/user/webapp`
- Fichiers analysés :
  - `/home/user/webapp/src/ui/schedule.py` (457 lignes)
  - `/home/user/webapp/cahier_texte.py` (757 lignes)
  - `/home/user/webapp/src/core/course_distribution.py` (430 lignes)
  - `/home/user/webapp/src/core/db_manager.py` (519 lignes)
