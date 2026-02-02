"""
Placeholder frames for other application features
These will be fully implemented in subsequent versions
"""

import tkinter as tk
from tkinter import ttk
from src.utils.theme import ThemeManager


class PrintSchedulesFrame(ttk.Frame):
    """Frame for viewing and printing schedules"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_ui()
    
    def build_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill='both')
        
        back_btn = ThemeManager.create_button(container, text='← Retour', command=self.go_back)
        back_btn.pack(anchor='nw')
        
        title = ThemeManager.create_label(container, text='Imprimer l\'état', style='Heading.TLabel')
        title.pack(pady=20)
        
        message = ThemeManager.create_label(
            container,
            text='Fonctionnalité en développement\nVous pourrez consulter et imprimer les emplois du temps sauvegardés'
        )
        message.pack(pady=20)
    
    def go_back(self):
        self.controller.show_frame('DashboardFrame')


class ImportContentFrame(ttk.Frame):
    """Frame for importing content from Excel"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_ui()
    
    def build_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill='both')
        
        back_btn = ThemeManager.create_button(container, text='← Retour', command=self.go_back)
        back_btn.pack(anchor='nw')
        
        title = ThemeManager.create_label(container, text='Importer contenu', style='Heading.TLabel')
        title.pack(pady=20)
        
        message = ThemeManager.create_label(
            container,
            text='Fonctionnalité en développement\nVous pourrez importer du contenu depuis des fichiers Excel'
        )
        message.pack(pady=20)
    
    def go_back(self):
        self.controller.show_frame('DashboardFrame')


class DistributionFrame(ttk.Frame):
    """Frame for distributing courses automatically"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_ui()
    
    def build_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill='both')
        
        back_btn = ThemeManager.create_button(container, text='← Retour', command=self.go_back)
        back_btn.pack(anchor='nw')
        
        title = ThemeManager.create_label(container, text='Distribuer les cours', style='Heading.TLabel')
        title.pack(pady=20)
        
        message = ThemeManager.create_label(
            container,
            text='Fonctionnalité en développement\nVous pourrez distribuer automatiquement les cours sur la semaine'
        )
        message.pack(pady=20)
    
    def go_back(self):
        self.controller.show_frame('DashboardFrame')
