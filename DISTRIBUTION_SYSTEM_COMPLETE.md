# 🎲 Système de Distribution Automatique des Cours

## Vue d'ensemble

Ce document décrit le système complet de distribution automatique des cours implémenté dans l'application **Cahier de Texte**, basé sur l'architecture de l'ancienne application.

## 📋 Architecture

### Tables de Base de Données

#### 1. `ma_table` - Répertoire Principal des Cours
```sql
CREATE TABLE ma_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valeur TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
- **Rôle**: Contient tous les contenus de cours disponibles
- **Utilisation**: Source séquentielle pour la distribution

#### 2. `schedule_entries` - Emploi du Temps Fixe
```sql
CREATE TABLE schedule_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_id INTEGER NOT NULL,
    time_slot_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(day_id, time_slot_id),
    FOREIGN KEY (day_id) REFERENCES days(id),
    FOREIGN KEY (time_slot_id) REFERENCES time_slots(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
```
- **Rôle**: Définit quelles classes sont planifiées à quels créneaux
- **Utilisation**: Modèle fixe pour la distribution hebdomadaire

#### 3. `course_progress` - Suivi de Progression
```sql
CREATE TABLE course_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    last_course_id INTEGER,
    last_week INTEGER,
    school_year TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (last_course_id) REFERENCES ma_table(id),
    UNIQUE(class_id, school_year)
)
```
- **Rôle**: Suit le dernier cours assigné à chaque classe
- **Utilisation**: Assure la progression séquentielle

#### 4. `schedule_data` - Distribution Effective
```sql
CREATE TABLE schedule_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_number INTEGER NOT NULL,
    day_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    content TEXT,
    class_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_number, day_id, slot_id),
    FOREIGN KEY (day_id) REFERENCES days(id),
    FOREIGN KEY (slot_id) REFERENCES time_slots(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
```
- **Rôle**: Stocke la distribution finale par semaine
- **Utilisation**: Données affichées dans l'emploi du temps

## 🔄 Algorithme de Distribution

### Principe
L'algorithme distribue les cours de manière **séquentielle** et **automatique** en respectant les contraintes.

### Étapes

```python
def distribute_courses(week_number, school_year):
    """
    1. Charger l'emploi du temps fixe (schedule_entries)
    2. Calculer les dates de la semaine
    3. Charger les contraintes (vacances, jours fériés, absences)
    4. Pour chaque créneau dans schedule_entries:
        a. Calculer la date réelle du créneau
        b. Vérifier si jour bloqué (vacances/férié/absence)
        c. Si bloqué: passer au suivant
        d. Sinon:
            - Récupérer le prochain cours pour la classe (depuis ma_table)
            - Mettre à jour la progression (course_progress)
            - Enregistrer dans schedule_data
    5. Commit et retour du résultat
    """
```

### Progression Séquentielle

- **Classe A, Semaine 1**: Cours 1, 2, 3, 4, 5
- **Classe A, Semaine 2**: Cours 6, 7, 8, 9, 10
- **Classe A, Semaine 3**: Cours 11, 12, 13, 14, 15

Chaque classe progresse **indépendamment** à travers `ma_table`.

## 🚫 Gestion des Contraintes

### 1. Jours Fériés (`holidays`)
```python
def is_day_blocked(date_str, holidays):
    for holiday in holidays:
        if holiday['date'] == date_str:
            return True  # Créneau bloqué
```

### 2. Vacances Scolaires (`vacations`)
```python
def is_day_blocked(date_str, vacations):
    for vacation in vacations:
        if vacation['start_date'] <= date_str <= vacation['end_date']:
            return True  # Créneau bloqué
```

### 3. Absences Enseignants (`absences`)
```python
def is_day_blocked(date_str, absences):
    for absence in absences:
        if absence['date'] == date_str:
            return True  # Créneau bloqué
```

### 4. Pause Déjeuner
- **Automatiquement exclue** via `WHERE is_lunch = 0` dans les requêtes
- Créneau 12:30-14:30 jamais utilisé pour la distribution

## 📊 Module `CourseDistributionManager`

### Fichier: `src/core/course_distribution.py`

### Méthodes Principales

#### `get_valid_slots(week_number)`
```python
"""Retourne tous les créneaux valides (hors pause déjeuner)"""
# Résultat: [(day_id, time_slot_id), ...]
# 6 jours × 8 créneaux non-lunch = 48 slots
```

#### `get_next_course(class_id, week_number, school_year)`
```python
"""
Récupère le prochain cours pour une classe
1. Cherche last_course_id dans course_progress
2. Si None: retourne premier cours de ma_table
3. Sinon: retourne cours suivant (id > last_course_id)
"""
```

#### `update_course_progress(class_id, course_id, week_number, school_year)`
```python
"""Met à jour la progression de la classe"""
# INSERT ou UPDATE dans course_progress
```

#### `distribute_courses(week_number, school_year)`
```python
"""
Exécute la distribution complète pour une semaine
Retourne: (success, message, distribution_data)
"""
```

#### `get_distribution_summary(week_number)`
```python
"""Retourne un résumé lisible de la distribution"""
# Pour affichage dans l'UI
```

#### `load_sample_courses()`
```python
"""Charge 30 cours d'exemple dans ma_table"""
# Utile pour les tests et démonstrations
```

## 🖼️ Interface Utilisateur

### Fichier: `src/ui/distribution.py`

### Fonctionnalités

#### 1. Panneau de Configuration
- **Année scolaire**: Format YYYY-YYYY (ex: 2024-2025)
- **Semaine**: Spinbox 1-36

#### 2. Actions Disponibles
- **📚 Charger Cours Exemple**: Remplit `ma_table` avec 30 cours
- **🔄 Rafraîchir Statut**: Affiche l'état du système
- **🎲 DISTRIBUER**: Lance la distribution pour la semaine sélectionnée
- **📊 Voir Résumé**: Affiche la distribution dans un tableau

#### 3. Panneau de Statut
Affiche en temps réel:
- Nombre de cours dans `ma_table`
- Nombre d'entrées dans `schedule_entries`
- Nombre de classes
- Contraintes (jours fériés, vacances)
- Semaines déjà distribuées
- Prérequis (✅ ou ⚠️)

### Exemple de Statut
```
╔══════════════════════════════════════════════════════════════════════╗
║                    STATUT DU SYSTÈME DE DISTRIBUTION                 ║
╚══════════════════════════════════════════════════════════════════════╝

📚 CONTENU DES COURS (ma_table)
   ├─ Nombre de cours disponibles: 30
   └─ ✅ Prêt

📅 EMPLOI DU TEMPS FIXE (schedule_entries)
   ├─ Nombre d'entrées: 20
   └─ ✅ Prêt

🏫 CLASSES
   ├─ Nombre de classes: 3
   └─ ✅ Prêt

✅ SYSTÈME PRÊT - Vous pouvez distribuer!
```

## 🧪 Tests

### Fichier: `test_course_distribution.py`

### Tests Couverts (11 tests)

1. ✅ **Vérification des tables requises**
2. ✅ **Chargement de cours d'exemple**
3. ✅ **Création de classes de test**
4. ✅ **Création d'entrées d'emploi du temps fixe**
5. ✅ **Récupération des créneaux valides**
6. ✅ **Récupération du prochain cours**
7. ✅ **Ajout de contraintes**
8. ✅ **Exécution de la distribution (Semaine 1)**
9. ✅ **Vérification du suivi de progression**
10. ✅ **Récupération du résumé de distribution**
11. ✅ **Distribution Semaine 2 (progression séquentielle)**

### Résultats
```
📚 Courses in ma_table:        30
📅 Fixed schedule entries:      20
📊 Distributed entries:         40 (2 weeks × 20 entries)
📆 Weeks distributed:           1, 2

✅ ALL TESTS COMPLETED SUCCESSFULLY!
```

## 📝 Guide d'Utilisation

### Prérequis

1. **Créer des classes** (via Contraintes > Classes)
   - Ex: 6ème A, 5ème B, 4ème C

2. **Charger les cours** (via Distribution > Charger Cours Exemple)
   - Ou ajouter manuellement dans `ma_table`

3. **Créer l'emploi du temps fixe** (via SQL ou interface)
   ```sql
   INSERT INTO schedule_entries (day_id, time_slot_id, class_id)
   VALUES (1, 1, 1);  -- Lundi 08:30, Classe 1
   ```

4. **Ajouter des contraintes** (optionnel)
   - Jours fériés, vacances, absences

### Workflow

1. **Ouvrir** "🎲 Distribuer les Cours"
2. **Vérifier** le statut (bouton Rafraîchir)
3. **Sélectionner** l'année et la semaine
4. **Cliquer** "DISTRIBUER"
5. **Voir** le résumé (bouton Voir Résumé)
6. **Consulter** l'emploi du temps distribué dans "Emploi du temps"

### Exemple Complet

```
Semaine 1: 02/09/2024 - 07/09/2024
─────────────────────────────────────────────────────
Lundi    08:30-09:30   6ème A   Introduction aux mathématiques
Lundi    09:30-10:30   5ème B   Introduction aux mathématiques
Lundi    10:30-11:30   4ème C   Introduction aux mathématiques
Lundi    11:30-12:30   6ème A   Les nombres entiers
Mardi    08:30-09:30   5ème B   Les nombres entiers
...

Semaine 2: 09/09/2024 - 14/09/2024
─────────────────────────────────────────────────────
Lundi    08:30-09:30   6ème A   Les fractions
Lundi    09:30-10:30   5ème B   Les fractions
...
```

## 🔗 Intégration avec le Reste de l'Application

### Relation avec `schedule.py`
- **schedule.py**: Affichage et édition manuelle de l'emploi du temps
- **distribution.py**: Remplissage automatique de `schedule_data`
- Les deux utilisent la même table `schedule_data`

### Relation avec `constraints.py`
- **constraints.py**: Gestion des contraintes (holidays, vacations, absences, classes)
- **distribution.py**: Lecture des contraintes pour bloquer les créneaux

### Relation avec `import_content.py`
- **import_content.py**: Importe des cours depuis Excel/CSV vers `courses`
- **distribution.py**: Pourrait être étendu pour utiliser `courses` au lieu de `ma_table`

## 🚀 Améliorations Futures

### Fonctionnalités Potentielles

1. **Import depuis `courses`**
   - Utiliser la table `courses` comme source au lieu de `ma_table`
   - Filtrer par `class_id` et `subject`

2. **Distribution multi-matières**
   - Assigner différentes matières à différents créneaux
   - Respecter des quotas horaires par matière

3. **Optimisation des créneaux**
   - Éviter trop de créneaux consécutifs pour une même classe
   - Équilibrer la charge hebdomadaire

4. **Prévision et simulation**
   - Mode "simulation" avant commit
   - Prévisualisation sur plusieurs semaines

5. **Export et statistiques**
   - Export PDF de la distribution
   - Statistiques sur l'utilisation des cours

6. **Gestion des ressources**
   - Salles de classe
   - Matériel pédagogique
   - Enseignants multiples

## 📊 Comparaison Ancienne vs Nouvelle Application

| Aspect | Ancienne App | Nouvelle App |
|--------|--------------|--------------|
| **Table des cours** | `ma_table` | `ma_table` ✅ |
| **Emploi du temps fixe** | `schedule_entries` | `schedule_entries` ✅ |
| **Suivi progression** | `class_course_progress` | `course_progress` ✅ |
| **Distribution finale** | `schedule_data` | `schedule_data` ✅ |
| **Algorithme** | Séquentiel | Séquentiel ✅ |
| **Contraintes** | Vacances, jours fériés, absences | Vacances, jours fériés, absences ✅ |
| **UI** | Interface basique | Interface moderne avec statut en temps réel ✅ |
| **Tests** | Non | 11 tests complets ✅ |

## ✅ Statut Final

### Ce qui est implémenté

- ✅ Tables de base de données
- ✅ Module `CourseDistributionManager`
- ✅ Interface utilisateur complète
- ✅ Algorithme de distribution séquentielle
- ✅ Gestion des contraintes
- ✅ Suivi de progression
- ✅ Système de statut en temps réel
- ✅ Chargement de cours d'exemple
- ✅ Résumé de distribution
- ✅ Suite de tests complète (11 tests, 100% réussite)

### Documentation Complète

- ✅ Architecture de la base de données
- ✅ Description de l'algorithme
- ✅ Guide d'utilisation
- ✅ Exemples concrets
- ✅ Comparaison avec l'ancienne app

---

**🎉 Le système de distribution automatique des cours est complet et opérationnel !**

Date de création: 2026-02-02  
Version: 1.0  
Basé sur: Architecture de l'ancienne application `/home/user/webapp`
