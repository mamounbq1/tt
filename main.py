"""
Main Application Entry Point
Cahier de Texte - School Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import DB_PATH, LOG_DIR, APP_NAME
from src.utils.theme import ThemeManager
from src.core.database import DatabaseManager

# Import UI frames
from src.ui.dashboard import DashboardFrame
from src.ui.add_entry import AddEntryFrame
from src.ui.schedule import ScheduleFrame
from src.ui.constraints import ConstraintsFrame
from src.ui.placeholder_frames import (
    PrintSchedulesFrame,
    ImportContentFrame,
    DistributionFrame
)


class Application(tk.Tk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Setup exception handling
        self.report_callback_exception = self.handle_exception
        
        # Initialize logging
        self.setup_logging()
        
        logging.info("=" * 70)
        logging.info(f"{APP_NAME} - Starting")
        logging.info("=" * 70)
        
        # Initialize database
        try:
            self.database = DatabaseManager(DB_PATH)
            self.database.verify_schema()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}", exc_info=True)
            messagebox.showerror(
                "Erreur de base de données",
                f"Impossible d'initialiser la base de données:\n{str(e)}"
            )
            sys.exit(1)
        
        # Setup UI
        self.setup_window()
        self.setup_frames()
        
        # Show dashboard
        self.show_frame('DashboardFrame')
        
        logging.info("Application initialized successfully")
    
    def setup_logging(self):
        """Configure logging"""
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(LOG_DIR, f'app_{date_str}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def setup_window(self):
        """Configure main window"""
        self.title(APP_NAME)
        self.geometry('1000x700')
        self.minsize(800, 600)
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Setup theme
        ThemeManager.setup_style(self)
    
    def setup_frames(self):
        """Initialize all application frames"""
        # Container for all frames
        self.container = ttk.Frame(self)
        self.container.pack(fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dictionary to hold all frames
        self.frames = {}
        
        # List of frame classes to initialize
        frame_classes = [
            ('DashboardFrame', DashboardFrame),
            ('AddEntryFrame', AddEntryFrame),
            ('PrintSchedulesFrame', PrintSchedulesFrame),
            ('ImportContentFrame', ImportContentFrame),
            ('ConstraintsFrame', ConstraintsFrame),
            ('ScheduleFrame', ScheduleFrame),
            ('DistributionFrame', DistributionFrame)
        ]
        
        # Create and store each frame
        for frame_name, FrameClass in frame_classes:
            try:
                frame = FrameClass(self.container, self)
                frame.grid(row=0, column=0, sticky='nsew')
                self.frames[frame_name] = frame
                logging.info(f"Frame initialized: {frame_name}")
            except Exception as e:
                logging.error(f"Failed to initialize {frame_name}: {e}", exc_info=True)
    
    def show_frame(self, frame_name):
        """Show the specified frame"""
        if frame_name not in self.frames:
            logging.error(f"Frame not found: {frame_name}")
            messagebox.showerror(
                "Erreur",
                f"Écran non trouvé: {frame_name}"
            )
            return
        
        frame = self.frames[frame_name]
        frame.tkraise()
        logging.info(f"Showing frame: {frame_name}")
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        messagebox.showerror(
            "Erreur inattendue",
            f"Une erreur inattendue s'est produite:\n{exc_value}\n\nVeuillez consulter les logs pour plus de détails."
        )
    
    def on_closing(self):
        """Handle application closing"""
        logging.info("Application closing")
        if self.database:
            self.database.close()
        self.destroy()


def main():
    """Main entry point"""
    try:
        app = Application()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        logging.critical(f"Application crashed: {e}", exc_info=True)
        messagebox.showerror(
            "Erreur critique",
            f"L'application a rencontré une erreur critique:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
