"""
Theme Manager for Tkinter Application
Provides consistent styling across the application
"""

import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """Manages application theme and styling"""
    
    # Color scheme
    COLORS = {
        'primary': '#1976D2',
        'primary_dark': '#1565C0',
        'primary_light': '#42A5F5',
        'secondary': '#424242',
        'background': '#FFFFFF',
        'surface': '#F5F5F5',
        'error': '#F44336',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'info': '#2196F3',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'divider': '#BDBDBD'
    }
    
    # Font configuration
    FONTS = {
        'heading': ('Arial', 18, 'bold'),
        'subheading': ('Arial', 14, 'bold'),
        'body': ('Arial', 11),
        'body_bold': ('Arial', 11, 'bold'),
        'small': ('Arial', 9),
        'button': ('Arial', 10, 'bold')
    }
    
    @classmethod
    def setup_style(cls, root):
        """Setup ttk style for the application"""
        style = ttk.Style(root)
        
        # Configure TFrame
        style.configure('TFrame', background=cls.COLORS['background'])
        
        # Configure TLabel
        style.configure('TLabel',
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['body'])
        
        # Configure heading labels
        style.configure('Heading.TLabel',
                       font=cls.FONTS['heading'],
                       foreground=cls.COLORS['primary'])
        
        style.configure('Subheading.TLabel',
                       font=cls.FONTS['subheading'],
                       foreground=cls.COLORS['text_primary'])
        
        # Configure TButton
        style.configure('TButton',
                       font=cls.FONTS['button'],
                       padding=10)
        
        # Configure primary button
        style.configure('Primary.TButton',
                       background=cls.COLORS['primary'],
                       foreground='white',
                       font=cls.FONTS['button'],
                       padding=10)
        
        # Configure TEntry
        style.configure('TEntry',
                       fieldbackground='white',
                       font=cls.FONTS['body'])
        
        # Configure Treeview
        style.configure('Treeview',
                       font=cls.FONTS['body'],
                       rowheight=25)
        
        style.configure('Treeview.Heading',
                       font=cls.FONTS['body_bold'])
        
        return style
    
    @classmethod
    def create_card_frame(cls, parent, **kwargs):
        """Create a card-style frame with shadow effect"""
        frame = ttk.Frame(parent, **kwargs)
        frame.configure(relief='raised', borderwidth=1)
        return frame
    
    @classmethod
    def create_button(cls, parent, text, command, style='TButton', **kwargs):
        """Create a styled button"""
        button = ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        return button
    
    @classmethod
    def create_label(cls, parent, text, style='TLabel', **kwargs):
        """Create a styled label"""
        label = ttk.Label(parent, text=text, style=style, **kwargs)
        return label
    
    @classmethod
    def create_entry(cls, parent, **kwargs):
        """Create a styled entry widget"""
        entry = ttk.Entry(parent, **kwargs)
        return entry
