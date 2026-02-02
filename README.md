# Cahier de Texte - School Management System

Version 2.0.0 - Fresh Start

## Description

A complete school management application for tracking homework, schedules, and course distribution. Built with Python and Tkinter.

## Features

✅ **Dashboard** - Central navigation hub
✅ **Add Entries** - Record homework and course content
🚧 **Print Schedules** - View and print saved schedules (in development)
🚧 **Import Content** - Import from Excel files (in development)
🚧 **Manage Constraints** - Holidays, vacations, absences (in development)
🚧 **Schedule View** - Weekly schedule grid (in development)
🚧 **Course Distribution** - Automatic course allocation (in development)

## Project Structure

```
webapp-v2/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── data/                   # Database storage
│   └── cahier_texte.db    # SQLite database
├── logs/                   # Application logs
├── src/
│   ├── core/              # Business logic
│   │   └── database.py    # Database manager
│   ├── ui/                # User interface
│   │   ├── dashboard.py   # Main dashboard
│   │   ├── add_entry.py   # Add entry form
│   │   └── placeholder_frames.py  # Other screens
│   └── utils/             # Utilities
│       ├── config.py      # Configuration
│       └── theme.py       # UI theming
```

## Installation

### Requirements

- Python 3.8 or higher
- tkinter (usually included with Python)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/mamounbq1/tt.git
cd tt
git checkout fresh-start
```

2. Run the application:
```bash
python main.py
```

That's it! No additional dependencies required.

## Usage

### First Launch

When you first run the application:
1. Database is automatically created in `data/cahier_texte.db`
2. Default admin account is created (username: `admin`, password: `admin123`)
3. Days of week and time slots are populated
4. Dashboard appears with 6 navigation buttons

### Adding Homework Entries

1. Click **"➕ Ajouter une entrée"**
2. Fill in the form:
   - Date (DD/MM/YYYY format)
   - Class name (e.g., "6ème A")
   - Subject (e.g., "Mathématiques")
   - Course content (required)
   - Homework (optional)
   - Exam (optional)
3. Click **"💾 Enregistrer"** to save

### Database Schema

The application uses SQLite with the following tables:

- `teachers` - Teacher accounts
- `classes` - Class information
- `days` - Days of the week
- `time_slots` - Time slots (08:30-18:30)
- `courses` - Course content
- `homework_entries` - Homework and course entries
- `schedule_data` - Weekly schedules
- `holidays` - Public holidays
- `vacations` - School vacations
- `absences` - Teacher absences
- `modules` - Course modules
- `course_progress` - Progress tracking

## Development

### Code Style

- Written from scratch (no copy-paste)
- Clean, documented code
- Follows Python best practices
- Modular architecture

### Adding New Features

1. Create new frame class in `src/ui/`
2. Register it in `main.py` frame_classes list
3. Add navigation button in dashboard
4. Implement business logic in `src/core/`

### Logging

Logs are stored in `logs/` directory:
- `app_YYYYMMDD.log` - Daily log file
- Contains INFO, WARNING, and ERROR messages
- Console output enabled during development

## Configuration

Edit `src/utils/config.py` to customize:

- Database path
- Application name and version
- Window size and minimum dimensions
- Time slots
- Color scheme
- Font configuration

## Troubleshooting

### Database Issues

If you encounter database errors:

1. Check `data/cahier_texte.db` exists
2. Check file permissions
3. Review logs in `logs/` directory
4. Database is auto-created on first run

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/webapp-v2
python main.py
```

### UI Issues

The application uses tkinter which should be included with Python. If you get tkinter errors:

**On Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**On macOS:**
```bash
brew install python-tk
```

**On Windows:**
Tkinter is usually included. Reinstall Python if needed.

## License

MIT License - Free to use and modify

## Author

Created from scratch for the Cahier de Texte project

## Version History

### 2.0.0 (Current - Fresh Start)
- Complete rewrite from scratch
- Clean modular architecture
- Dashboard with navigation
- Add entry functionality
- Comprehensive database schema
- Logging and error handling
- No external dependencies

## Future Enhancements

- [ ] Complete schedule view implementation
- [ ] Excel import/export functionality
- [ ] PDF generation for printing
- [ ] Course distribution algorithm
- [ ] Constraints management UI
- [ ] User authentication system
- [ ] Data backup and restore
- [ ] Report generation
- [ ] Search and filter features
- [ ] Multi-language support

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/mamounbq1/tt
- Branch: fresh-start

---

**Built with ❤️ using Python and Tkinter**
