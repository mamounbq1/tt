# 📚 Cahier de Texte - School Schedule Management System

A comprehensive school schedule management system built with Python and Tkinter. This application helps teachers and administrators manage class schedules, absences, holidays, course distribution, and more.

## ✨ Features

### 🎯 Core Features
- **User Authentication** - Secure login system for teachers
- **Schedule Management** - Create and manage weekly class schedules
- **Course Distribution** - Automatic distribution of courses across classes
- **Calendar Integration** - Track holidays, vacations, and absences
- **Excel Import/Export** - Import schedules from Excel files
- **PDF Generation** - Print schedules to PDF format
- **Multi-tab Interface** - Intuitive navigation between modules

### 📋 Modules

1. **Home Dashboard** (`src/ui/home.py`)
   - Welcome screen with quick access to all features
   - User authentication and session management

2. **Schedule Manager** (`src/ui/schedule.py`)
   - Weekly schedule grid view
   - Add/Edit/Delete schedule entries
   - Vacation and holiday highlighting
   - Automatic course distribution

3. **Tab Manager** (`src/ui/tab_manager.py`)
   - Manage constraints and rules
   - Configure time slots and classes

4. **Excel Importer** (`src/ui/import_excel.py`)
   - Import schedules from Excel files
   - Bulk data entry

5. **Saved Schedules** (`src/ui/saved_schedules.py`)
   - View and manage previously saved schedules
   - Week-by-week history

## 🏗️ Project Structure

```
cahier-de-texte/
│
├── main.py                 # Application entry point
├── cahier_texte.py        # Legacy Cahier de Texte interface
│
├── src/                    # Source code directory
│   ├── __init__.py
│   │
│   ├── core/              # Core modules
│   │   ├── __init__.py
│   │   ├── db_manager.py          # Database operations
│   │   ├── theme_manager.py       # UI theme configuration
│   │   ├── course_distribution.py # Course distribution logic
│   │   ├── absences.py            # Absence management
│   │   ├── classes.py             # Class management
│   │   ├── holiday.py             # Holiday management
│   │   ├── vacances.py            # Vacation management
│   │   └── modules.py             # Module management
│   │
│   ├── ui/                # User interface components
│   │   ├── __init__.py
│   │   ├── home.py                # Home/Login screens
│   │   ├── schedule.py            # Schedule grid interface
│   │   ├── tab_manager.py         # Tab management
│   │   ├── import_excel.py        # Excel import interface
│   │   ├── saved_schedules.py     # Saved schedules view
│   │   ├── add_entry.py           # Add entry dialog
│   │   ├── schedule_grid.py       # Schedule grid component
│   │   ├── top_frame.py           # Top frame component
│   │   └── loading_window.py      # Loading screen
│   │
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── config.py              # Configuration settings
│       ├── constants.py           # Application constants
│       └── pdf_generator.py       # PDF generation utilities
│
├── data/                   # Data directory
│   └── cahier_texte.db    # SQLite database
│
├── logs/                   # Log files directory
│   ├── error_YYYYMMDD.log
│   └── debug_YYYYMMDD.log
│
├── docs/                   # Documentation
│
├── Classeur1.xlsx         # Sample Excel file
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Tkinter (usually comes with Python)
- SQLite3 (included with Python)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mamounbq1/tt.git
   cd tt
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📖 Usage

### First Launch
1. The application will create necessary database tables automatically
2. Default admin credentials:
   - **Username**: `admin`
   - **Password**: `admin`

### Main Workflow
1. **Login** - Enter your credentials
2. **Home Dashboard** - Select the module you want to use
3. **Schedule Management**:
   - Select a week from the dropdown
   - Click cells to add/edit content
   - Save changes before switching weeks
   - Generate PDF for printing

### Course Distribution
1. Import course data via Excel importer
2. Configure class groups and time slots
3. Use automatic distribution feature
4. Review and adjust as needed

## 🗄️ Database Schema

The application uses SQLite with the following main tables:

- **enseignants** - Teacher information and credentials
- **classes** - Class/group information
- **schedule_entries** - Schedule assignments
- **schedule_data** - Weekly schedule content
- **time_slots** - Time slot definitions
- **days** - Days of the week
- **vacances** - School vacation periods
- **jours_feries** - Public holidays
- **absences** - Teacher absences
- **entries** - Cahier de texte entries
- **modules** - Course modules

## 🎨 Customization

### Theme Configuration
Edit `src/core/theme_manager.py` to customize colors and styles.

### Time Slots
Modify time slots in `src/utils/constants.py`:
- `MORNING_SLOTS`
- `AFTERNOON_SLOTS`

### Database Path
Change database location in `src/utils/config.py`:
```python
DB_PATH = os.path.join(BASE_DIR, 'data', 'cahier_texte.db')
```

## 🔧 Configuration

### config.py
```python
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'cahier_texte.db')
```

### constants.py
Define application-wide constants:
- Color schemes
- Time slots
- Days of the week
- School year dates

## 📝 Development

### Adding New Modules
1. Create module file in appropriate directory (`src/core/`, `src/ui/`, or `src/utils/`)
2. Import in `main.py`
3. Add to frame_classes dictionary in `_initialize_frames()`
4. Add navigation button in `home.py`

### Logging
Logs are stored in the `logs/` directory:
- `error_YYYYMMDD.log` - Error level logs
- `debug_YYYYMMDD.log` - Debug level logs
- Console output - Info level logs

## 🐛 Troubleshooting

### Database Issues
- Delete `data/cahier_texte.db` to reset database
- Application will recreate tables on next launch

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path includes `src/` directory

### UI Issues
- Ensure Tkinter is properly installed
- Try running with different Python version (3.7-3.10 recommended)

## 📄 License

This project is licensed under the MIT License.

## 👥 Contributors

- Project developed for school schedule management
- Based on French educational system requirements

## 🔄 Version History

### Current Version
- Reorganized project structure
- Added modular architecture
- Improved error handling
- Enhanced documentation

### Features in Development
- Multi-user support
- Advanced reporting
- Calendar synchronization
- Email notifications

## 📞 Support

For issues and feature requests, please use the GitHub issue tracker.

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Uses SQLite for data storage
- PDF generation with ReportLab/FPDF

---

**Note**: This is an educational project designed for managing school schedules in French educational institutions.
