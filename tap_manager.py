from tkinter import ttk
import tkinter as tk
from theme_manager import ThemeManager
from frames.vacances import create_vacances_tab
from frames.holiday import create_holidays_tab
from frames.absences import create_absences_tab
from frames.modules import create_modules_tab
from frames.classes import create_classes_tab

class TabManagerFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Top navigation frame
        nav_frame = ttk.Frame(self, padding="10")
        nav_frame.pack(fill='x', pady=(0, 10))
        
        # Back button
        back_button = ttk.Button(
            nav_frame,
            text="Retour au tableau de bord",
            command=lambda: self.controller.show_frame("HomeFrame")
        )
        back_button.pack(side='left', padx=5)
        
        # Main content
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Setup notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure notebook style
        style = ttk.Style()
        style.configure('TNotebook', 
            background=ThemeManager.COLORS['background'],
            padding=5
        )
        style.configure('TNotebook.Tab',
            padding=(10, 5),
            font=ThemeManager.FONTS['body'],
            background=ThemeManager.COLORS['surface'],
            foreground=ThemeManager.COLORS['text_primary']
        )
        style.map('TNotebook.Tab',
            background=[('selected', ThemeManager.COLORS['primary'])],
            foreground=[('selected', 'white')]
        )
        
        # Create frames
        self.create_frames()
    
    def create_frames(self):
        frames = {
            'Jours Fériés': (ttk.Frame, create_holidays_tab),
            'Vacances': (ttk.Frame, create_vacances_tab),
            'Absences': (ttk.Frame, create_absences_tab),
            'Les Classes': (ttk.Frame, create_classes_tab),
            'Les Modules': (ttk.Frame, create_modules_tab)
        }
        
        for title, (frame_class, create_func) in frames.items():
            frame = frame_class(self.notebook, style='Tab.TFrame')
            self.notebook.add(frame, text=title)
            create_func(frame)