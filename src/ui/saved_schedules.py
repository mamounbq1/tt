import tkinter as tk
from tkinter import ttk, messagebox
from course_dist.db_manager import DatabaseManager
from datetime import datetime, timedelta
import logging
from tkinter import filedialog
from course_dist.pdf_generator import generate_pdf
from course_dist.constants import MORNING_SLOTS, AFTERNOON_SLOTS
from theme_manager import ThemeManager
import os

class SavedSchedulesFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Initialize database connection with proper path
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'cahier_texte.db'))
        self.db = DatabaseManager(self.db_path)
        
        try:
            self._create_ui()
            self._load_weeks()
        except Exception as e:
            logging.error(f"Error initializing SavedSchedulesFrame: {e}")
            messagebox.showerror("Error", f"Failed to initialize schedule view: {str(e)}")

    def _create_ui(self):
        """Create UI elements with error handling"""
        try:
            # Navigation frame
            nav_frame = ttk.Frame(self, padding="10")
            nav_frame.pack(fill='x')
            
            back_button = ttk.Button(
                nav_frame,
                text="Retour au tableau de bord",
                command=self._safe_return_to_dashboard
            )
            back_button.pack(side='left', padx=5)

            # Title
            title = ttk.Label(
                self,
                text="Emplois du temps sauvegardés",
                style="Heading.TLabel"
            )
            title.pack(pady=(5, 10))

            # Create scrollable container
            self.container = ttk.Frame(self)
            self.container.pack(fill='both', expand=True, padx=10, pady=10)

            # Create canvas and scrollbar
            self.canvas = tk.Canvas(
                self.container,
                background=ThemeManager.COLORS['surface'],
                highlightthickness=0
            )
            self.scrollbar = ttk.Scrollbar(
                self.container,
                orient="vertical",
                command=self.canvas.yview
            )
            
            self.table_frame = ttk.Frame(self.canvas)
            
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas_frame = self.canvas.create_window(
                (0, 0),
                window=self.table_frame,
                anchor="nw"
            )

            # Configure grid weights
            self.table_frame.grid_columnconfigure(0, weight=2)
            self.table_frame.grid_columnconfigure(1, weight=3)
            self.table_frame.grid_columnconfigure(2, weight=1)

            # Create headers
            self._create_headers()

            # Pack canvas and scrollbar
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")

            # Bind configuration events
            self.table_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind("<Configure>", self._on_canvas_configure)

        except Exception as e:
            logging.error(f"Error creating UI: {e}")
            raise

    def _on_frame_configure(self, event=None):
        """Adjust scroll region when frame resizes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ensure canvas resizes properly"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _create_headers(self):
        """Create table headers"""
        try:
            header_frame = ttk.Frame(self.table_frame, style="Header.TFrame")
            header_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
            
            headers = ["Semaine", "Détails", "Actions"]
            for col, text in enumerate(headers):
                header = ttk.Label(
                    header_frame,
                    text=text,
                    style="Header.TLabel"
                )
                header.grid(row=0, column=col, sticky="ew", padx=5, pady=2)
                header_frame.grid_columnconfigure(col, weight=1)
        except Exception as e:
            logging.error(f"Error creating headers: {e}")
            raise

    def _load_weeks(self):
        try:
            saved_weeks = self.get_saved_weeks()
            print(f"_load_weeks: raw saved_weeks = {saved_weeks}")

            # Clear existing content (keeping header row intact)
            for widget in self.table_frame.winfo_children():
                if int(widget.grid_info().get('row', 0)) > 0:
                    widget.destroy()

            if not saved_weeks:
                no_data_label = ttk.Label(
                    self.table_frame,
                    text="Aucun emploi du temps sauvegardé n'a été trouvé.",
                    style="Body.TLabel"
                )
                no_data_label.grid(row=1, column=0, columnspan=3, pady=10)
                return

            for idx, week_tuple in enumerate(saved_weeks, start=1):
                print(f"Processing week tuple (type {type(week_tuple)}; length {len(week_tuple) if hasattr(week_tuple, '__len__') else 'N/A'}): {week_tuple}")
                if not isinstance(week_tuple, (list, tuple)) or len(week_tuple) < 2:
                    print(f"Error parsing week: expected 2 values, got {week_tuple}")
                    continue  # Skip malformed entries
                week_number, year = week_tuple
                self._create_week_row(idx, week_number, year)

        except Exception as e:
            print(f"Error loading weeks: {e}")
            messagebox.showerror(
                "Error",
                "Failed to load saved schedules. Please check the console output for details."
            )




    def _safe_print_week(self, week_number, year):
        """Safely print a specific week"""
        try:
            data = self._prepare_pdf_data(week_number, year)
            if not data:
                messagebox.showwarning("Avertissement", "Aucune donnée à imprimer pour cette semaine.")
                return

            # Get file path from user first
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"schedule_week_{week_number}_{year}.pdf"
            )
            
            if not filename:
                return

            # Generate PDF
            generate_pdf(data, filename)
            messagebox.showinfo("Succès", "PDF généré avec succès!")

        except Exception as e:
            logging.error(f"Error printing week {week_number}-{year}: {e}")
            messagebox.showerror("Erreur", "Impossible de générer le PDF")

    def _prepare_pdf_data(self, week_number, year):
        """Prepare data for PDF generation"""
        try:
            # Fetch data for the selected week
            data = self.db.get_schedule_for_week(week_number, year)
            if not data:
                return None
            return data
        except Exception as e:
            logging.error(f"Error preparing PDF data: {e}")
            return None

    def _safe_return_to_dashboard(self):
        """Safely return to dashboard"""
        try:
            self.controller.show_frame("HomeFrame")
        except Exception as e:
            logging.error(f"Error returning to dashboard: {e}")
            messagebox.showerror("Erreur", "Impossible de retourner au tableau de bord")

    def get_saved_weeks(self):
        """Retrieve saved weeks with error handling"""
        try:
            weeks = self.db.get_saved_weeks()
            return weeks if weeks else []
        except Exception as e:
            logging.error(f"Error fetching saved weeks: {e}")
            return []
    def _create_week_row(self, idx, week_number, year):
        """Create a row for a specific week"""
        try:
            logging.debug(f"Création de la ligne de semaine: idx={idx}, week_number={week_number}, year={year}")
            row_frame = ttk.Frame(self.table_frame, style="Row.TFrame")
            row_frame.grid(row=idx, column=0, columnspan=3, sticky="ew")

            # Configure grid weights
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=1)

            # Week label
            week_label = ttk.Label(
                row_frame,
                text=f"Semaine {week_number} - {year}",
                style="Body.TLabel"
            )
            week_label.grid(row=0, column=0, sticky="ew", padx=5, pady=2)

            # Details
            details = f"Année: {year}\nNuméro de semaine: {week_number}"
            details_label = ttk.Label(
                row_frame,
                text=details,
                style="Body.TLabel",
                wraplength=300
            )
            details_label.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        except Exception as e:
            logging.error(f"Error creating week row: {e}")
            raise
