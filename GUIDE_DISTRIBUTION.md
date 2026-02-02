# 🚀 Guide Rapide - Distribution Automatique des Cours

## Comment utiliser la distribution automatique

### 📋 Prérequis (à faire une seule fois)

#### 1. Créer des classes
```
Menu: 🚫 Ajouter des contraintes > Onglet "Classes"
➕ Ajouter: 6ème A, 5ème B, 4ème C, etc.
```

#### 2. Charger les cours
```
Menu: 🎲 Distribuer les Cours
Bouton: 📚 Charger Cours Exemple
→ 30 cours d'exemple seront ajoutés dans ma_table
```

#### 3. Créer l'emploi du temps fixe
Pour le moment, il faut le faire via SQL. Voici un exemple pour créer un emploi du temps simple :

```sql
-- Insérer des entrées pour définir quelles classes sont programmées à quels créneaux
-- Ex: Lundi 08:30 (jour_id=1, slot_id=1) → Classe 1
INSERT INTO schedule_entries (day_id, time_slot_id, class_id)
VALUES 
  (1, 1, 1),  -- Lundi 08:30 → Classe 1
  (1, 2, 2),  -- Lundi 09:30 → Classe 2
  (1, 3, 3),  -- Lundi 10:30 → Classe 3
  (1, 4, 1),  -- Lundi 11:30 → Classe 1
  -- Répéter pour tous les jours et créneaux...
```

*Note: Une interface UI pour créer l'emploi du temps fixe peut être ajoutée dans le futur.*

### 🎲 Distribuer les cours (à faire chaque semaine)

#### Étape 1: Ouvrir le module
```
Menu principal → 🎲 Distribuer les Cours
```

#### Étape 2: Vérifier le statut
```
Cliquer sur: 🔄 Rafraîchir Statut
Vérifier que tout est ✅ (cours, classes, emploi du temps fixe)
```

#### Étape 3: Configurer
```
Année scolaire: 2024-2025 (format YYYY-YYYY)
Semaine: 1 (de 1 à 36)
```

#### Étape 4: Distribuer
```
Cliquer sur: 🎲 DISTRIBUER

Le système va:
• Charger l'emploi du temps fixe
• Calculer les dates de la semaine
• Vérifier les contraintes (vacances, jours fériés, absences)
• Assigner les cours séquentiellement
• Sauvegarder dans schedule_data
```

#### Étape 5: Voir le résultat
```
Option 1: Cliquer sur 📊 Voir Résumé
→ Tableau avec tous les créneaux de la semaine

Option 2: Aller dans Emploi du temps
→ Sélectionner la semaine distribuée
→ Voir les cours assignés
```

### 🔄 Progression Automatique

Le système assure la **progression séquentielle** :

```
Semaine 1:
  Lundi 08:30  - Classe A: Cours 1 "Introduction aux mathématiques"
  Lundi 09:30  - Classe A: Cours 2 "Les nombres entiers"
  Mardi 08:30  - Classe A: Cours 3 "Les fractions"
  ...

Semaine 2:
  Lundi 08:30  - Classe A: Cours 6 "Les triangles et leurs propriétés"
  Lundi 09:30  - Classe A: Cours 7 "Le théorème de Pythagore"
  ...

Semaine 3:
  Lundi 08:30  - Classe A: Cours 11 "Introduction à la physique"
  ...
```

Chaque classe progresse **indépendamment** à travers le programme.

### 🚫 Gestion Automatique des Contraintes

Le système respecte automatiquement :

#### Jours fériés
```
Menu: 🚫 Ajouter des contraintes > Onglet "Holidays"
➕ Ajouter: 01/11/2024 - Toussaint
→ Le créneau sera **automatiquement sauté** lors de la distribution
```

#### Vacances scolaires
```
Menu: 🚫 Ajouter des contraintes > Onglet "Vacations"
➕ Ajouter: 23/12/2024 - 06/01/2025 - Vacances de Noël
→ Tous les créneaux de cette période seront **automatiquement sautés**
```

#### Absences enseignants
```
Menu: 🚫 Ajouter des contraintes > Onglet "Absences"
➕ Ajouter: 15/10/2024 - M. Dupont - Congé maladie
→ Les créneaux de cet enseignant seront **automatiquement sautés**
```

#### Pause déjeuner
```
⚠️ Le créneau 12:30-14:30 est **automatiquement exclu**
→ Aucune configuration nécessaire
```

### 📊 Panneau de Statut

Le panneau affiche en temps réel :

```
📚 CONTENU DES COURS (ma_table)
   ├─ Nombre de cours disponibles: 30
   └─ ✅ Prêt

📅 EMPLOI DU TEMPS FIXE (schedule_entries)
   ├─ Nombre d'entrées: 20
   └─ ✅ Prêt

🏫 CLASSES
   ├─ Nombre de classes: 3
   └─ ✅ Prêt

🚫 CONTRAINTES
   ├─ Jours fériés: 5
   └─ Périodes de vacances: 4

📊 DISTRIBUTION EFFECTUÉE
   ├─ Semaines distribuées: 12
   └─ Numéros: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

✅ SYSTÈME PRÊT - Vous pouvez distribuer!
```

### ⚠️ Messages d'Erreur Courants

#### "Aucune entrée d'emploi du temps fixe trouvée"
**Solution**: Créez l'emploi du temps fixe en remplissant la table `schedule_entries`

#### "Format d'année scolaire invalide"
**Solution**: Utilisez le format YYYY-YYYY (ex: 2024-2025)

#### "⚠️ Fin du programme"
**Signification**: La classe a épuisé tous les cours de ma_table
**Solution**: Ajoutez plus de cours dans ma_table

### 🔧 Dépannage

#### Les cours ne se distribuent pas
1. Vérifier que ma_table contient des cours
2. Vérifier que schedule_entries contient des entrées
3. Vérifier que les classes existent
4. Consulter les logs pour plus de détails

#### La progression n'est pas correcte
1. Vérifier la table course_progress
2. Réinitialiser si nécessaire (supprimer les enregistrements)
3. Redistribuer depuis la semaine 1

#### Les contraintes ne sont pas respectées
1. Vérifier les dates dans holidays/vacations/absences
2. Format de date doit être: YYYY-MM-DD ou DD/MM/YYYY
3. Redistribuer la semaine concernée

### 💡 Astuces

#### Distribuer toute l'année en une fois
```python
# Script Python pour distribuer toutes les semaines
from src.core.course_distribution import CourseDistributionManager
from src.utils.config import DB_PATH

manager = CourseDistributionManager(DB_PATH)

for week in range(1, 37):  # Semaines 1-36
    success, message, _ = manager.distribute_courses(week, '2024-2025')
    print(f"Semaine {week}: {'✅' if success else '❌'} {message}")

manager.close()
```

#### Vérifier la distribution d'une semaine
```python
from src.core.course_distribution import CourseDistributionManager
from src.utils.config import DB_PATH

manager = CourseDistributionManager(DB_PATH)
summary = manager.get_distribution_summary(week_number=1)

for entry in summary:
    print(f"{entry['day_name']} {entry['time_range']} - {entry['class_name']}: {entry['content']}")

manager.close()
```

### 📅 Workflow Recommandé

**Début d'année scolaire:**
1. Créer toutes les classes
2. Charger les cours dans ma_table
3. Créer l'emploi du temps fixe (schedule_entries)
4. Ajouter les jours fériés et vacances de l'année
5. Distribuer les 36 semaines en une fois (ou au fur et à mesure)

**Chaque semaine:**
1. Consulter l'emploi du temps de la semaine
2. Si nécessaire, modifier manuellement via "Emploi du temps"
3. Ajouter absences enseignants si nécessaire
4. Redistribuer la semaine si changements importants

**En cas de changement:**
1. Modifier les contraintes (holidays/vacations/absences)
2. Redistribuer les semaines affectées
3. Vérifier le résumé

---

## 🎉 C'est Tout !

Le système est maintenant prêt à être utilisé. La distribution automatique vous fait gagner un temps considérable en gérant automatiquement :
- ✅ La progression séquentielle des cours
- ✅ Le respect des contraintes
- ✅ La répartition équitable sur l'année
- ✅ L'exclusion des périodes non-travaillées

**Bonne utilisation ! 🚀**
