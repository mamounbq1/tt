# Plan d'Implémentation Correct - Distribution Automatique

## ❌ ERREUR DANS L'IMPLÉMENTATION ACTUELLE

Notre `schedule.py` actuel est **complètement faux**. Il mélange deux concepts différents :
- Il charge depuis `schedule_data` (distribution hebdomadaire)
- Il devrait gérer `schedule_entries` (emploi du temps FIXE)

## ✅ ARCHITECTURE CORRECTE (basée sur l'ancienne app)

### 1. **schedule.py** (EmploiDuTempsApp)
**Rôle** : Gérer l'emploi du temps FIXE
- Table : `schedule_entries`
- Affichage : Nom de classe + niveau + année scolaire
- Actions :
  - Clic sur cellule vide → Ajouter une classe à ce créneau
  - Clic sur cellule remplie → Modifier ou supprimer la classe
  - Sauvegarder → INSERT INTO schedule_entries (class_id, day_id, time_slot_id)
  - Reload → Charger schedule_entries et afficher

**Exemple d'affichage** :
```
┌─────────────────────────────┐
│         6ème A               │
│    6ème - 2024-2025         │
└─────────────────────────────┘
```

### 2. **cahier_texte.py** (CahierTextApp) - À CRÉER
**Rôle** : Gérer la distribution hebdomadaire des cours
- Tables : schedule_entries (lecture seule) + schedule_data (écriture)
- Affichage : Nom de classe (en haut) + contenu du cours (en bas, éditable)
- Actions :
  - Distribuer → Appeler distribute_courses() pour remplir automatiquement
  - Modifier → Éditer le contenu d'un cours
  - Sauvegarder → INSERT INTO schedule_data (week_number, day_id, slot_id, content)
  - Reload → Charger schedule_data pour la semaine sélectionnée

**Exemple d'affichage** :
```
┌─────────────────────────────┐
│         6ème A               │  ← Nom de classe (lecture seule, depuis schedule_entries)
│  Les fractions              │  ← Contenu du cours (éditable, depuis schedule_data)
└─────────────────────────────┘
```

### 3. **distribution.py** (DistributionFrame)
**Rôle** : Interface pour déclencher la distribution
- Sélectionner une semaine
- Cliquer sur "Distribuer" → Appeler distribute_courses()
- Afficher le résumé de la distribution

## 📋 WORKFLOW COMPLET

```
1. CONTRAINTES
   ↓
   Créer les classes dans la table `classes`
   (ex: 6ème A, 5ème B, 4ème C, TCSF1, TCSF2, etc.)

2. EMPLOI DU TEMPS (schedule.py)
   ↓
   Définir l'emploi du temps FIXE dans `schedule_entries`
   (ex: Lundi 08:30 → 6ème A, Mardi 09:30 → 5ème B, etc.)

3. IMPORT EXCEL (import_content.py)
   ↓
   Importer les cours dans `ma_table`
   (ex: 1 → "Introduction aux mathématiques", 2 → "Les fractions", etc.)

4. DISTRIBUTION (distribution.py + cahier_texte.py)
   ↓
   Appeler distribute_courses() qui :
   - Lit schedule_entries pour savoir quelles classes sont prévues
   - Pour chaque créneau, assigne le prochain cours de ma_table
   - Respecte les contraintes (vacances, jours fériés, absences)
   - Exclut la pause déjeuner
   - Retourne {class_id: [(day_id, slot_id, course_id), ...]}
   
   ↓
   Afficher dans cahier_texte.py :
   - Nom de classe (depuis schedule_entries)
   - Contenu du cours (depuis ma_table via course_id)
   
   ↓
   Sauvegarder dans schedule_data :
   - week_number, day_id, slot_id, content (texte du cours)
```

## 🔧 TABLES

### schedule_entries (FIXE - ne change jamais)
```sql
CREATE TABLE schedule_entries (
    id INTEGER PRIMARY KEY,
    day_id INTEGER,              -- 1-6 (Lundi-Samedi)
    time_slot_id INTEGER,        -- 1-9 (créneaux horaires)
    class_id INTEGER,            -- Quelle classe
    created_at TIMESTAMP,
    UNIQUE(day_id, time_slot_id)
)
```

### schedule_data (HEBDOMADAIRE - change chaque semaine)
```sql
CREATE TABLE schedule_data (
    id INTEGER PRIMARY KEY,
    week_number INTEGER,         -- Numéro de semaine (1-36)
    day_id INTEGER,              -- 1-6 (Lundi-Samedi)
    slot_id INTEGER,             -- 1-9 (créneaux horaires)
    content TEXT,                -- CONTENU DU COURS (texte)
    class_id INTEGER,            -- Quelle classe (optionnel)
    created_at TIMESTAMP,
    UNIQUE(week_number, day_id, slot_id)
)
```

### ma_table (COURS - liste de tous les contenus)
```sql
CREATE TABLE ma_table (
    id INTEGER PRIMARY KEY,
    valeur TEXT,                 -- Contenu du cours
    created_at TIMESTAMP
)
```

### course_progress (PROGRESSION - suit où chaque classe en est)
```sql
CREATE TABLE course_progress (
    id INTEGER PRIMARY KEY,
    class_id INTEGER,
    last_course_id INTEGER,      -- Dernier cours utilisé
    last_week INTEGER,           -- Dernière semaine distribuée
    school_year TEXT,            -- Année scolaire (2024-2025)
    updated_at TIMESTAMP
)
```

## 📝 FICHIERS À CRÉER/MODIFIER

### 1. Réécrire schedule.py
- [x] ~~Basé sur l'ancienne app EmploiDuTempsApp~~ 
- [ ] Gérer schedule_entries uniquement
- [ ] Afficher classe + niveau + année
- [ ] Actions : Ajouter/Modifier/Supprimer classe

### 2. Créer cahier_texte.py
- [ ] Basé sur l'ancienne app CahierTextApp
- [ ] Charger schedule_entries (lecture seule pour les noms de classe)
- [ ] Charger/sauvegarder schedule_data (contenu des cours)
- [ ] Bouton "Distribuer" pour remplir automatiquement

### 3. Mettre à jour distribution.py
- [ ] Interface simple pour déclencher la distribution
- [ ] Sélection de semaine
- [ ] Bouton "Distribuer"
- [ ] Affichage du résumé

### 4. Tests
- [ ] test_schedule_entries.py (test emploi du temps fixe)
- [ ] test_distribution_workflow.py (test distribution complète)
- [ ] test_cahier_texte.py (test affichage et sauvegarde)

## 🎯 PROCHAINES ÉTAPES

1. [ ] Réécrire schedule.py basé sur EmploiDuTempsApp
2. [ ] Créer cahier_texte.py basé sur CahierTextApp
3. [ ] Adapter distribution.py pour déclencher la distribution
4. [ ] Écrire les tests
5. [ ] Vérifier le workflow complet
6. [ ] Commit et push

## 📚 RÉFÉRENCES

- Ancienne app : `/home/user/webapp`
- Fichiers clés :
  - `/home/user/webapp/src/ui/schedule.py` (EmploiDuTempsApp)
  - `/home/user/webapp/cahier_texte.py` (CahierTextApp)
  - `/home/user/webapp/src/core/course_distribution.py`
  - `/home/user/webapp/src/core/db_manager.py`
