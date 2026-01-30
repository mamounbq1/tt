"""
CahierTextFrame - Wrapper for the main schedule interface
Integrates CahierTextApp into the main application as a frame
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Ensure cahier_texte.py is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cahier_texte import CahierTextApp

class CahierTextFrame(ttk.Frame):
    """Frame wrapper for CahierTextApp to integrate with main application"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        # Create a container for the CahierTextApp
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Create back button at the top
        top_bar = ttk.Frame(self.container)
        top_bar.pack(side="top", fill="x", padx=5, pady=5)
        
        back_btn = ttk.Button(
            top_bar,
            text="← Retour au tableau de bord",
            command=self.go_back,
            style='TButton'
        )
        back_btn.pack(side="left", padx=5)
        
        # Create content frame for CahierTextApp
        content_frame = ttk.Frame(self.container)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        try:
            # Initialize CahierTextApp but don't create a new Tk window
            # Instead, we'll embed it in our frame
            self.app = CahierTextApp(content_frame)
            
        except Exception as e:
            error_label = ttk.Label(
                content_frame,
                text=f"Erreur d'initialisation: {str(e)}\nVeuillez vérifier les logs.",
                foreground="red",
                font=("Arial", 12)
            )
            error_label.pack(pady=50)
            import logging
            logging.error(f"Failed to initialize CahierTextFrame: {e}", exc_info=True)
    
    def go_back(self):
        """Return to home frame"""
        self.controller.show_frame("HomeFrame")
