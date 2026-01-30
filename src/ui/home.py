import tkinter as tk
from tkinter import ttk, messagebox
import logging, sqlite3
from course_dist.db_manager import DatabaseManager  # Import DatabaseManager
from theme_manager import ThemeManager


class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style='TFrame')
        self.controller = controller
        self.db_manager = DatabaseManager()  # Initialize DatabaseManager
        self.create_widgets()

    def create_widgets(self):
        """Create UI components."""
        container = ttk.Frame(self, style='TFrame')
        container.pack(expand=True)

        # Header
        header = ttk.Label(container, text="Bienvenue", style='Heading.TLabel')
        header.pack(pady=(40, 20))

        # Form frame
        form_frame = ttk.Frame(container, style='TFrame')
        form_frame.pack(pady=10)

        # Username
        ttk.Label(form_frame, text="Identifiant:", style='TLabel').pack(anchor="w")
        self.login_entry = ttk.Entry(form_frame, width=30, style='TEntry')
        self.login_entry.pack(pady=5)

        # Password
        ttk.Label(form_frame, text="Mot de passe:", style='TLabel').pack(anchor="w")
        self.password_entry = ttk.Entry(form_frame, show="•", width=30, style='TEntry')
        self.password_entry.pack(pady=5)

        # Error message
        self.error_label = ttk.Label(
            form_frame, text="", foreground=ThemeManager.COLORS['error'], style='TLabel'
        )
        self.error_label.pack(pady=5)

        # Login button
        ttk.Button(container, text="Se connecter", command=self.check_login, style='TButton').pack(pady=20)

        # Bind Enter key
        self.controller.bind('<Return>', lambda e: self.check_login())

        # Set initial focus
        self.login_entry.focus_set()

    def check_login(self):
        """Handle user login.
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()"""

        login = 'admin'
        password = 'admin'

        if not login or not password:
            self.show_error("Veuillez remplir tous les champs")
            return

        try:
            enseignant = self.db_manager.get_user(login, password)

            if enseignant:
                home_frame = self.controller.frames["HomeFrame"]
                home_frame.set_user(enseignant)
                self.controller.show_frame("HomeFrame")
            else:
                self.show_error("Identifiants incorrects")

        except sqlite3.Error as e:
            logging.error(f"Database error during login: {e}")
            self.show_error("Erreur de connexion à la base de données")
        except Exception as e:
            logging.error(f"Unexpected login error: {e}")
            self.show_error("Une erreur inattendue est survenue.")

    def show_error(self, message):
        """Display error message."""
        self.error_label.config(text=message)
        self.password_entry.delete(0, tk.END)


class HomeFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style='TFrame')
        self.controller = controller
        self.enseignant = None
        self.create_widgets()

    def set_user(self, enseignant):
        """Set logged-in user details."""
        self.enseignant = enseignant
        self.welcome_label.config(
            text=f"Bienvenue, {enseignant[1] if enseignant else 'Utilisateur'}"
        )

    def create_widgets(self):
        """Create UI components."""
        container = ttk.Frame(self, style='TFrame')
        container.pack(expand=True)

        # Header
        header = ttk.Label(container, text="Tableau de Bord", style='Heading.TLabel')
        header.pack(pady=(40, 10))

        # Welcome message
        self.welcome_label = ttk.Label(
            container,
            text="Bienvenue, Utilisateur",
            font=ThemeManager.FONTS['subheading'],
            foreground=ThemeManager.COLORS['text_secondary'],
            style='TLabel'
        )
        self.welcome_label.pack(pady=(0, 20))

        # Button grid
        button_frame = ttk.Frame(container, style='TFrame')
        button_frame.pack(pady=20)

        buttons = [
            ("➕ Ajouter une entrée", self.open_add_entry),
            ("🖨️ Imprimer l'état", self.print_state),
            ("📥 Importer contenu", self.import_content),
            ("⚙️ Ajouter des contraintes", self.add_constraints),
            ("📅 Emploi du temps", self.open_schedule),
            ("📚 Distribuer les cours", self.distribute_courses)
        ]

        for i, (text, command) in enumerate(buttons):
            row, col = divmod(i, 3)
            btn = ttk.Button(
                button_frame, text=text, command=command, style='TButton', padding=(20, 15)
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            button_frame.grid_columnconfigure(col, weight=1)

    def open_schedule(self):
        self.controller.show_frame("EmploiDuTempsApp")

    def open_add_entry(self):
        self.controller.show_frame("CahierTextFrame")

    def print_state(self):
        self.controller.show_frame("SavedSchedulesFrame")

    def import_content(self):
        self.controller.show_frame("ExcelImporterFrame")

    def add_constraints(self):
        self.controller.show_frame("TabManagerFrame")

    def distribute_courses(self):
        self.controller.show_frame("CahierTextFrame")
