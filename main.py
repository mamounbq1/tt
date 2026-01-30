import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import logging
from datetime import datetime
from theme_manager import ThemeManager
# from loading_window import LoadingContext  <-- Loading window is temporarily disabled
from home import LoginFrame, HomeFrame
from schadual import EmploiDuTempsApp
from tap_manager import TabManagerFrame
from course_dist.cahier_texte import CahierTextFrame
from import_excel import ExcelImporterFrame
from course_dist.SavedSchedulesFrame import SavedSchedulesFrame
from course_dist.db_manager import DatabaseManager  # Import our DatabaseManager
from config import DB_PATH  # Import the global DB_PATH

class MainApp(tk.Tk):
    def __init__(self):
        try:
            super().__init__()
            
            # Setup exception handler
            sys.excepthook = self._handle_global_exception
            
            self.withdraw()  # Hide main window initially
            self._initialize_app_with_loading()  # Use the initialization method below
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
    
    def _initialize_app_with_loading(self):
        """Initialize application with loading screen disabled for now."""
        # Temporarily disable the loading window:
        # with LoadingContext(
        #     title="Démarrage de l'application",
        #     message="Veuillez patienter pendant l'initialisation..."
        # ) as loading:
        try:
            # Uncomment the following lines if you wish to update the loading status:
            # loading.update_status("Configuration de l'environnement...")
            self._setup_environment()
            
            # loading.update_status("Configuration de la fenêtre...")
            self._setup_window()
            
            # loading.update_status("Chargement des interfaces...")
            self._initialize_frames()
            
            # loading.update_status("Configuration de la base de données...")
            self.db_manager = DatabaseManager(db_name=DB_PATH)
            logging.info("DatabaseManager initialized successfully.")
            
            # loading.update_status("Finalisation...")
            self.deiconify()
            self.show_frame("LoginFrame")
            
        except Exception as e:
            raise Exception(f"Échec de l'initialisation : {str(e)}")
    
    def _setup_environment(self):
        """Setup application environment"""
        try:
            # Configure logging with separate log files for different severity levels
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
            self.title("Système de Gestion")
            
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
                'LoginFrame': LoginFrame,
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
                    raise Exception(f"Failed to initialize {frame_name}: {str(e)}")
            
            missing_frames = set(frame_classes.keys()) - set(self.frames.keys())
            if missing_frames:
                raise Exception(f"Missing frames: {', '.join(missing_frames)}")
            
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
