# 🐛 Système de Debug et Gestion d'Erreurs

## ✅ IMPLÉMENTÉ ET OPÉRATIONNEL

Un système complet de logging et de gestion d'erreurs a été ajouté à l'application.

---

## 📁 Fichier Principal

**`src/utils/debug_logger.py`** (273 lignes)

### Classes Principales

#### 1. `DebugLogger`
Logger amélioré avec plusieurs flux de sortie et formatage détaillé.

**Fonctionnalités** :
- Logs console (INFO et supérieur)
- Logs fichier debug (tous les messages)
- Logs fichier erreurs (erreurs uniquement)
- Logs fichier quotidien
- Formatage détaillé avec nom de fichier, numéro de ligne, fonction

**Utilisation** :
```python
from src.utils.debug_logger import DebugLogger

logger = DebugLogger('mon_module')
logger.info("Message d'information")
logger.debug("Message de debug")
logger.error("Message d'erreur")
logger.warning("Message d'avertissement")
```

#### 2. `ErrorHandler`
Gestionnaire centralisé d'erreurs.

**Méthodes** :
- `handle_database_error()` - Erreurs de base de données
- `handle_file_error()` - Erreurs de fichiers
- `handle_validation_error()` - Erreurs de validation
- `handle_generic_error()` - Erreurs génériques

**Utilisation** :
```python
from src.utils.debug_logger import ErrorHandler

try:
    # Opération base de données
    pass
except Exception as e:
    result = ErrorHandler.handle_database_error(e, "INSERT operation", logger)
```

---

## 📊 Niveaux de Log

| Niveau | Description | Fichier | Console |
|--------|-------------|---------|---------|
| **DEBUG** | Messages de debug détaillés | ✅ debug.log | ❌ |
| **INFO** | Informations générales | ✅ debug.log, daily.log | ✅ |
| **WARNING** | Avertissements | ✅ debug.log, daily.log | ✅ |
| **ERROR** | Erreurs | ✅ debug.log, errors.log, daily.log | ✅ |
| **CRITICAL** | Erreurs critiques | ✅ debug.log, errors.log, daily.log | ✅ |

---

## 📂 Fichiers de Log Créés

### Structure
```
logs/
├── application.log                 # Log global de l'application
├── {module}_debug.log              # Tous les messages d'un module
├── {module}_errors.log             # Erreurs uniquement d'un module
└── {module}_{YYYY-MM-DD}.log       # Log quotidien d'un module
```

### Exemples
```
logs/
├── application.log
├── course_distribution_debug.log
├── course_distribution_errors.log
├── course_distribution_2026-02-02.log
├── database_debug.log
├── database_errors.log
└── database_2026-02-02.log
```

---

## 🔧 Décorateurs de Fonction

### 1. `@log_function_call(logger)`
Log automatique des entrées/sorties de fonction.

**Exemple** :
```python
from src.utils.debug_logger import DebugLogger, log_function_call

logger = DebugLogger('mon_module')

@log_function_call(logger)
def ma_fonction(param1, param2):
    return param1 + param2

# Logs automatiques:
# >>> ENTER ma_fonction
#     Args: (1, 2)
#     Kwargs: {}
# <<< EXIT ma_fonction
#     Result: 3
```

### 2. `@handle_errors(logger, default_return=None)`
Gestion automatique des erreurs.

**Exemple** :
```python
from src.utils.debug_logger import DebugLogger, handle_errors

logger = DebugLogger('mon_module')

@handle_errors(logger, default_return=[])
def fonction_risquee():
    # Code qui peut lever une exception
    return result

# Si exception: log automatique + retour de default_return
```

---

## 📝 Format des Logs

### Format Détaillé (fichiers)
```
2026-02-02 19:24:09 - module_name - INFO - [filename.py:123] - function_name() - Message
```

### Format Simple (console)
```
19:24:09 - INFO - Message
```

---

## 🎯 Exemples d'Utilisation

### 1. Initialisation Simple
```python
from src.utils.debug_logger import DebugLogger

logger = DebugLogger('my_app')

logger.info("Application started")
logger.debug("Detailed debug information")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### 2. Log d'Entrée/Sortie de Fonction
```python
logger.log_function_entry("distribute_courses", 
                         week_number=1, 
                         school_year="2024-2025")

# ... code ...

logger.log_function_exit("distribute_courses", result=distribution)
```

### 3. Log d'Opération Base de Données
```python
logger.log_database_operation("INSERT", 
                             "schedule_data",
                             week_number=1,
                             class_id=5)
```

### 4. Log d'Exception
```python
try:
    # Code risqué
    pass
except Exception as e:
    logger.log_exception(e, context="distribute_courses")
```

---

## 🔍 Modules avec Debug

### Implémenté
✅ **course_distribution.py**
- Logs __init__, get_connection, close
- Logs détaillés des opérations de distribution
- Tracking des erreurs DB

### À Implémenter
⏳ **database.py**
- Toutes les opérations CRUD
- Erreurs de connexion
- Erreurs de schéma

⏳ **cahier_texte.py**
- Chargement des données
- Sauvegarde
- Distribution automatique

⏳ **schedule.py**
- Ajout/Modification/Suppression de classes
- Sauvegarde emploi du temps
- Rechargement

---

## 📊 Exemple de Sortie

### Console
```
19:25:12 - INFO - Initializing CourseDistributionManager
19:25:12 - INFO - Database connection established successfully
19:25:12 - INFO - Loading sample courses
19:25:12 - INFO - 30 courses loaded successfully
```

### Fichier Debug
```
2026-02-02 19:25:12 - course_distribution - DEBUG - [course_distribution.py:25] - get_connection() - get_connection() called
2026-02-02 19:25:12 - course_distribution - DEBUG - [course_distribution.py:29] - get_connection() - Creating new database connection
2026-02-02 19:25:12 - course_distribution - INFO - [course_distribution.py:32] - get_connection() - Database connection established successfully
```

### Fichier Errors (quand erreur)
```
2026-02-02 19:30:45 - course_distribution - ERROR - [course_distribution.py:150] - distribute_courses() - Distribution failed
Traceback (most recent call last):
  File "course_distribution.py", line 145, in distribute_courses
    result = self.get_next_course(class_id, week, 0, year)
  File "course_distribution.py", line 98, in get_next_course
    cursor.execute(query, params)
sqlite3.OperationalError: no such table: course_progress
```

---

## 🚀 Configuration Globale

### setup_global_logging()
Configure le logging global de l'application.

**Utilisation dans main.py** :
```python
from src.utils.debug_logger import setup_global_logging, log_system_info

# Au démarrage de l'application
setup_global_logging()
log_system_info()

# Logs automatiques:
# ================================================================================
# APPLICATION STARTED
# Timestamp: 2026-02-02 19:24:09
# Python version: 3.12.11
# Working directory: /home/user/webapp-v2
# ================================================================================
```

---

## 🎯 Avantages

### 1. Debug Facilité
- Tous les logs dans des fichiers séparés
- Logs console pour feedback immédiat
- Logs détaillés pour investigation

### 2. Tracking des Erreurs
- Fichier dédié aux erreurs
- Stack traces complets
- Contexte de l'erreur

### 3. Analyse
- Logs quotidiens pour analyse historique
- Format structuré pour parsing
- Multiple niveaux de détail

### 4. Production
- Logs non intrusifs (console INFO+)
- Fichiers rotatifs (quotidiens)
- Performance minimale

---

## 📚 Prochaines Étapes

1. ✅ Système de base implémenté
2. ⏳ Ajouter logs à tous les modules critiques
3. ⏳ Ajouter rotation automatique des logs (taille max)
4. ⏳ Ajouter monitoring des performances
5. ⏳ Ajouter export des logs (JSON, CSV)
6. ⏳ Ajouter dashboard de visualisation

---

## 🎉 Statut

**✅ SYSTÈME OPÉRATIONNEL**

- Classe DebugLogger fonctionnelle
- ErrorHandler implémenté
- Décorateurs disponibles
- Logs multi-niveaux
- Formatage détaillé
- course_distribution.py avec debug

**Prêt pour** : Extension à tous les modules

---

**Créé le** : 2026-02-02  
**Fichier** : src/utils/debug_logger.py  
**Lignes** : 273  
**Tests** : ✅ Passants
