import tkinter.ttk as ttk

class ThemeManager:
    """Gère les styles et le thème de l'application"""
    
    COLORS = {
        'primary': '#1976D2',      # Bleu foncé
        'primary_light': '#2196F3', # Bleu clair
        'secondary': '#757575',     # Gris
        'accent': '#FFC107',        # Ambre
        'background': '#F5F5F5',    # Gris clair
        'surface': '#FFFFFF',       # Blanc
        'error': '#F44336',         # Rouge
        'text_primary': '#212121',  # Gris très foncé
        'text_secondary': '#757575', # Gris moyen
        'secondary_light': '#757575',

    }
    
    FONTS = {
        'heading': ('Helvetica', 16, 'bold'),
        'subheading': ('Helvetica', 12, 'bold'),
        'body': ('Helvetica', 10),
        'button': ('Helvetica', 10, 'bold'),
        'small': ('Helvetica', 9)
    }
    
    @classmethod
    def setup_theme(cls):
        """Configure le style ttk pour toute l'application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style général
        style.configure('.',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['body']
        )
        
        # Bouton standard
        style.configure('TButton',
            padding=(15, 8),
            background=cls.COLORS['primary'],
            foreground='white',
            font=cls.FONTS['button']
        )
        style.map('TButton',
            background=[('active', cls.COLORS['primary_light'])],
            foreground=[('active', 'white')]
        )
        
        # Entry (champs de saisie)
        style.configure('TEntry',
            padding=(5, 5),
            fieldbackground=cls.COLORS['surface'],
            font=cls.FONTS['body']
        )
        
        # Label standard
        style.configure('TLabel',
            padding=(5, 5),
            font=cls.FONTS['body']
        )
        
        # Label titre
        style.configure('Heading.TLabel',
            font=cls.FONTS['heading'],
            foreground=cls.COLORS['primary'],
            background=cls.COLORS['background'],  # Add background color
            anchor='center'  # Center the text
        )
                
        # Frame standard
        style.configure('TFrame',
            background=cls.COLORS['background']
        )
        
        # Styles pour l'emploi du temps
        style.configure('Header.TLabel',
            padding=(10, 5),
            background=cls.COLORS['primary'],
            foreground='white',
            font=cls.FONTS['subheading']
        )
        
        style.configure('Time.TLabel',
            padding=(5, 5),
            background=cls.COLORS['secondary'],
            foreground='white',
            font=cls.FONTS['body'],
            anchor='center'  # Center the text

        )
        style.configure('Cell.TFrame',
            background=cls.COLORS['surface'],
            relief='solid',
            borderwidth=1
        )
        
        style.configure('Cell.TLabel',
            padding=(10, 5),  # Increased horizontal padding
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['body'],
            wraplength=120,  # Adjusted wrap length
            anchor='center',  # Center the text
            relief='solid',    # Add visible border
            borderwidth=1      # Set border width
        )
        
        style.configure('Empty.TLabel',
            padding=(10, 5),  # Match Cell.TLabel padding
            background='#d3d3d3',  # Changed to match cell background
            foreground=cls.COLORS['text_secondary'],
            font=cls.FONTS['body'],
            anchor='center',  # Center the text
            relief='solid',   # Add border
            borderwidth=1     # Add border width
        )
        
        style.configure('CellHover.TLabel',
            padding=(10, 5),  # Match Cell.TLabel padding
            background=cls.COLORS['primary_light'],
            foreground='white',
            font=cls.FONTS['body'],
            anchor='center',  # Center the text
            relief='solid',   # Add border
            borderwidth=1     # Add border width
        )
        style.configure('Separator.TFrame',
            background=cls.COLORS['primary'],
            height=20
        )
        
        # Style pour les boîtes de dialogue
        style.configure('Dialog.TFrame',
            background=cls.COLORS['background'],
            padding=10
        )
        # Add these styles in the setup_theme method of ThemeManager class:
        
        # Style pour les onglets
        style.configure('Tab.TFrame',
            background=cls.COLORS['surface'],
            padding=10
        )
        
        style.configure('TNotebook',
            background=cls.COLORS['background'],
            padding=5,
            borderwidth=0
        )
        
        style.configure('TNotebook.Tab',
            padding=(15, 8),
            font=cls.FONTS['body'],
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary']
        )
        
        style.map('TNotebook.Tab',
            background=[
                ('selected', cls.COLORS['primary']),
                ('active', cls.COLORS['primary_light'])
            ],
            foreground=[
                ('selected', 'white'),
                ('active', 'white')
            ]
        )
        style.configure('Cahier.TFrame',
            background=cls.COLORS['background']
        )
        
        style.configure('CahierHeader.TLabel',
            background=cls.COLORS['primary'],
            foreground='white',
            font=cls.FONTS['subheading'],
            padding=10
        )
        
        style.configure('CahierTime.TLabel',
            background=cls.COLORS['secondary'],
            foreground='white',
            font=cls.FONTS['body'],
            padding=5,
            anchor='center'  # Center the text

        )
        
        style.configure('CahierCell.TFrame',
            background=cls.COLORS['surface'],
            relief='solid',
            borderwidth=1
        )
        
        style.configure('CahierContent.TLabel',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['body'],
            padding=5
        )
        
        style.configure('CahierEmpty.TLabel',
            background='#d3d3d3',
            foreground=cls.COLORS['text_secondary'],
            font=cls.FONTS['body'],
            padding=5
        )
        
        style.configure('CahierVacation.TFrame',
            background='#FFE0E0',
            relief='solid',
            borderwidth=1
        )
        
        style.configure('CahierHoliday.TFrame',
            background='#E0FFE0',
            relief='solid',
            borderwidth=1
        )
        
        style.configure('CahierAbsence.TFrame',
            background='#E0E0FF',
            relief='solid',
            borderwidth=1
        )
        style.configure('EmptyCell.TFrame',
            background='#d3d3d3',  # Light grey background
            relief='solid',
            borderwidth=1
        )

        style.configure('EmptyCell.TLabel',
            background='#d3d3d3',  # Matching light grey
            foreground=cls.COLORS['text_secondary'],
            font=cls.FONTS['body'],
            anchor='center',
            relief='solid',
            borderwidth=1
        )