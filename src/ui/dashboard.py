"""
Dashboard Frame - Main landing page after startup
Shows overview and navigation buttons
"""

import tkinter as tk
from tkinter import ttk
from src.utils.theme import ThemeManager


class DashboardFrame(ttk.Frame):
    """Main dashboard with navigation buttons"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_user = None
        self.build_ui()
    
    def build_ui(self):
        """Build the dashboard interface"""
        # Main container
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill='both')
        
        # Header section
        header_frame = ttk.Frame(container)
        header_frame.pack(fill='x', pady=(0, 30))
        
        title_label = ThemeManager.create_label(
            header_frame,
            text="Tableau de Bord",
            style='Heading.TLabel'
        )
        title_label.pack()
        
        # Welcome message
        self.welcome_label = ThemeManager.create_label(
            header_frame,
            text="Bienvenue, Utilisateur",
            style='Subheading.TLabel'
        )
        self.welcome_label.pack(pady=10)
        
        # Button grid
        button_frame = ttk.Frame(container)
        button_frame.pack(expand=True)
        
        # Configure grid columns
        for i in range(3):
            button_frame.columnconfigure(i, weight=1, pad=10)
        
        # Define navigation buttons
        buttons = [
            {
                'text': '➕ Ajouter une entrée',
                'command': self.open_add_entry,
                'icon': '➕'
            },
            {
                'text': '🖨️ Imprimer l\'état',
                'command': self.open_print_schedules,
                'icon': '🖨️'
            },
            {
                'text': '📥 Importer contenu',
                'command': self.open_import_content,
                'icon': '📥'
            },
            {
                'text': '⚙️ Ajouter des contraintes',
                'command': self.open_constraints,
                'icon': '⚙️'
            },
            {
                'text': '📅 Emploi du temps',
                'command': self.open_schedule,
                'icon': '📅'
            },
            {
                'text': '📚 Distribuer les cours',
                'command': self.open_distribution,
                'icon': '📚'
            }
        ]
        
        # Create buttons in grid
        for index, btn_data in enumerate(buttons):
            row = index // 3
            col = index % 3
            
            btn = ThemeManager.create_button(
                button_frame,
                text=btn_data['text'],
                command=btn_data['command'],
                style='Primary.TButton'
            )
            btn.grid(row=row, column=col, sticky='ew', padx=10, pady=10, ipadx=20, ipady=15)
    
    def set_user(self, user_data):
        """Set current user and update welcome message"""
        self.current_user = user_data
        if user_data:
            name = user_data.get('name', 'Utilisateur')
            self.welcome_label.config(text=f"Bienvenue, {name}")
        else:
            self.welcome_label.config(text="Bienvenue, Utilisateur")
    
    def open_add_entry(self):
        """Navigate to add entry frame"""
        self.controller.show_frame('AddEntryFrame')
    
    def open_print_schedules(self):
        """Navigate to print schedules frame"""
        self.controller.show_frame('PrintSchedulesFrame')
    
    def open_import_content(self):
        """Navigate to import content frame"""
        self.controller.show_frame('ImportContentFrame')
    
    def open_constraints(self):
        """Navigate to constraints management frame"""
        self.controller.show_frame('ConstraintsFrame')
    
    def open_schedule(self):
        """Navigate to schedule view frame"""
        self.controller.show_frame('ScheduleFrame')
    
    def open_distribution(self):
        """Navigate to course distribution frame (Cahier de Texte)"""
        self.controller.show_frame('CahierTexteFrame')
