#!/usr/bin/env python3
"""
Cahier de Texte - School Schedule Management System
Main application entry point
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import from reorganized structure
from src.core.theme_manager import ThemeManager
from src.core.db_manager import DatabaseManager
from src.ui.home import HomeFrame  # Only import HomeFrame, skip LoginFrame
from src.ui.schedule import EmploiDuTempsApp
from src.ui.tab_manager import TabManagerFrame
from src.ui.import_excel import ExcelImporterFrame
from src.ui.saved_schedules import SavedSchedulesFrame
from src.utils.config import DB_PATH

# Import CahierTextFrame wrapper
from src.ui.cahier_text_frame import CahierTextFrame


class MainApp(tk.Tk):
    """Main application window"""
    
    def __init__(self):
        try:
            super().__init__()
            
            # Setup exception handler
            sys.excepthook = self._handle_global_exception
            
            self.withdraw()  # Hide main window initially
            self._initialize_app()
        except Exception as e:
            self._handle_fatal_error("Erreur d'initialisation", e)
    
    def _handle_global_exception(self, exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        try:
            logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            if not isinstance(exc_value, SystemExit):
                messagebox.showerror(
                    "Erreur inattendue",
                    f"Une erreur inattendue s'est produite: {str(exc_value)}"
                )
        except:
            print("Critical error in exception handler:", exc_type, exc_value)
    
    def _initialize_app(self):
        """Initialize application"""
        try:
            self._setup_environment()
            self._setup_window()
            self._initialize_frames()
            
            # Initialize database manager
            self.db_manager = DatabaseManager(db_name=DB_PATH)
            logging.info("DatabaseManager initialized successfully.")
            
            # Show main window - Skip login and go directly to HomeFrame
            self.deiconify()
            self.show_frame("HomeFrame")
            
        except Exception as e:
            raise Exception(f"Échec de l'initialisation : {str(e)}")
    
    def _setup_environment(self):
        """Setup application environment"""
        try:
            # Configure logging with separate log files
            log_dir = 'logs'
            os.makedirs(log_dir, exist_ok=True)
            date_str = datetime.now().strftime("%Y%m%d")
            
            handlers = [
                logging.FileHandler(os.path.join(log_dir, f'error_{date_str}.log')),
                logging.FileHandler(os.path.join(log_dir, f'debug_{date_str}.log')),
                logging.StreamHandler()
            ]
            handlers[0].setLevel(logging.ERROR)
            handlers[1].setLevel(logging.DEBUG)
            handlers[2].setLevel(logging.INFO)
            
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=handlers
            )
            
            logging.info("Application starting...")
            
            # Setup theme
            ThemeManager.setup_theme()
            self.title("Système de Gestion Scolaire - Cahier de Texte")
            
        except Exception as e:
            raise Exception(f"Échec de la configuration : {str(e)}")
    
    def _setup_window(self):
        """Configure main window"""
        try:
            self.state('zoomed')
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.minsize(800, 600)
            self.geometry(f"{screen_width}x{screen_height}+0+0")
            
            try:
                self.container = ttk.Frame(self, style='TFrame')
            except tk.TclError:
                self.container = ttk.Frame(self)
                logging.warning("Failed to apply TFrame style")
            
            self.container.pack(fill="both", expand=True)
            self.container.grid_rowconfigure(0, weight=1)
            self.container.grid_columnconfigure(0, weight=1)
            
        except Exception as e:
            raise Exception(f"Échec de la configuration de la fenêtre : {str(e)}")
    
    def _initialize_frames(self):
        """Initialize all application frames with proper error handling"""
        try:
            self.frames = {}
            frame_classes = {
                'HomeFrame': HomeFrame,
                'EmploiDuTempsApp': EmploiDuTempsApp,
                'TabManagerFrame': TabManagerFrame,
                'SavedSchedulesFrame': SavedSchedulesFrame,
                'CahierTextFrame': CahierTextFrame,
                'ExcelImporterFrame': ExcelImporterFrame
            }
            
            for frame_name, FrameClass in frame_classes.items():
                try:
                    frame = FrameClass(self.container, self)
                    self.frames[frame_name] = frame
                    frame.grid(row=0, column=0, sticky="nsew")
                    logging.info(f"Successfully initialized {frame_name}")
                except Exception as e:
                    logging.error(f"Error initializing {frame_name}: {str(e)}")
                    # Continue with other frames instead of failing completely
            
        except Exception as e:
            raise Exception(f"Frame initialization error: {str(e)}")
    
    def show_frame(self, frame_name):
        """Show the specified frame with error handling"""
        try:
            frame = self.frames.get(frame_name)
            if frame:
                frame.tkraise()
                logging.info(f"Displayed frame: {frame_name}")
            else:
                raise ValueError(f"Frame not found: {frame_name}")
        except Exception as e:
            logging.error(f"Error displaying frame {frame_name}: {e}")
            messagebox.showerror("Error", f"Unable to display {frame_name}")
    
    def _handle_fatal_error(self, title, error):
        """Handle fatal errors"""
        error_message = f"A fatal error occurred: {str(error)}"
        logging.critical(error_message, exc_info=True)
        
        try:
            messagebox.showerror(title, error_message)
        except:
            print(error_message)
        
        try:
            self.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    try:
        app = MainApp()
        app.mainloop()
    except Exception as e:
        logging.critical("Application failed to start", exc_info=True)
        try:
            messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        except:
            print(f"Critical error: {str(e)}")
        sys.exit(1)
