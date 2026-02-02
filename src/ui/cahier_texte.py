"""
Cahier de Texte - Weekly Course Distribution
Manages weekly distribution of courses (schedule_data table)
Based on CahierTextApp from old app
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime, timedelta
import sqlite3
from src.utils.theme import ThemeManager
from src.utils.config import DB_PATH
from src.core.course_distribution import CourseDistributionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class CahierTexteFrame(ttk.Frame):
    """Frame for managing weekly course distribution (schedule_data)"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Database connection
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.cursor = self.conn.cursor()
            self.cursor.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            messagebox.showerror("Erreur Base de Données", f"Une erreur est survenue : {e}")
        
        # Initialize course distributor
        logging.info("Initializing CourseDistributionManager...")
        self.course_distributor = CourseDistributionManager(DB_PATH)
        logging.info("CourseDistributionManager initialized successfully.")
        
        self.cells = {}
        self.unsaved_changes = False
        
        # Colors
        self.colors = {
            'header_bg': '#2c3e50',
            'header_fg': 'white',
            'time_bg': '#34495e',
            'time_fg': 'white',
            'cell_bg': 'white',
            'cell_fg': '#2c3e50',
            'empty_fg': '#95a5a6',
            'placeholder_bg': '#ecf0f1',
            'vacation_bg': '#f39c12',
            'holiday_bg': '#e74c3c',
            'absence_bg': '#95a5a6'
        }
        
        # Time slots and days
        self.morning_slots = [
            "08:30 - 09:30", "09:30 - 10:30", 
            "10:30 - 11:30", "11:30 - 12:30"
        ]
        self.afternoon_slots = [
            "14:30 - 15:30", "15:30 - 16:30", 
            "16:30 - 17:30", "17:30 - 18:30"
        ]
        self.columns = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        
        self._create_main_layout()
    
    def _create_main_layout(self):
        """Create the main application layout"""
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill='both', expand=True)
        
        for i in range(len(self.columns) + 1):
            self.main_frame.grid_columnconfigure(i, weight=1)
        
        self._create_top_frame()
        self._create_header_row()
        self._create_schedule_grid()
    
    def _create_top_frame(self):
        """Create the top frame with controls"""
        buttons_top = tk.Frame(self.main_frame)
        buttons_top.grid(row=0, column=0, columnspan=7, sticky='ew', pady=(0, 5))
        
        for i in range(5):
            buttons_top.grid_columnconfigure(i, weight=1)
        
        # Week selector
        week_label = tk.Label(
            buttons_top,
            text="Semaine:",
            font=("Arial", 11, "bold")
        )
        week_label.grid(row=0, column=0, padx=5)
        
        self.week_var = tk.StringVar()
        weeks = self._get_school_year_weeks()
        
        self.week_selector = ttk.Combobox(
            buttons_top,
            textvariable=self.week_var,
            values=weeks,
            state="readonly",
            width=30
        )
        self.week_selector.grid(row=0, column=1, padx=5)
        self.week_selector.bind('<<ComboboxSelected>>', self._on_week_change)
        
        # Set current week (week 1 by default)
        if weeks:
            self.week_selector.current(0)
        
        # Control buttons
        btn_width = 15
        buttons = [
            ("🔄 Reload", self.reload_schedule),
            ("💾 Save", self.save_schedule),
            ("🖨️ Print PDF", self.print_to_pdf)
        ]
        
        for idx, (text, command) in enumerate(buttons):
            btn = tk.Button(
                buttons_top,
                text=text,
                command=command,
                bg=self.colors['header_bg'],
                fg=self.colors['header_fg'],
                font=("Arial", 10, "bold"),
                width=btn_width
            )
            btn.grid(row=0, column=idx+2, padx=5)
        
        # Back button
        back_btn = tk.Button(
            buttons_top,
            text="← Retour",
            command=lambda: self.controller.show_frame("DashboardFrame"),
            bg='#7f8c8d',
            fg='white',
            font=("Arial", 10, "bold"),
            width=10
        )
        back_btn.grid(row=0, column=5, padx=5)
    
    def _get_school_year_weeks(self):
        """Get list of weeks for the school year"""
        weeks = []
        # School year: September to June
        current_year = datetime.now().year
        school_start = datetime(current_year, 9, 1)
        
        # Generate 36 weeks
        for week_num in range(1, 37):
            week_start = school_start + timedelta(weeks=week_num-1)
            week_end = week_start + timedelta(days=5)
            
            week_text = f"Semaine {week_num} - du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}"
            weeks.append(week_text)
        
        return weeks
    
    def _create_header_row(self):
        """Create the header row with day labels"""
        for col, text in enumerate(["Horaire"] + self.columns):
            label = tk.Label(
                self.main_frame,
                text=text,
                font=("Arial", 11, "bold"),
                bg=self.colors['header_bg'],
                fg=self.colors['header_fg'],
                relief="raised",
                height=2,
                borderwidth=1
            )
            label.grid(row=1, column=col, sticky='nsew', padx=1, pady=1)
    
    def _create_schedule_grid(self):
        """Create the main schedule grid"""
        self._clear_existing_cells()
        
        # Get schedule_entries (fixed schedule)
        schedule_entries = self._get_schedule_entries()
        
        # Create class_schedule mapping
        class_schedule = {}
        for entry in schedule_entries:
            day_id = entry['day_id']
            time_slot_id = entry['time_slot_id']
            class_name = entry['class_name']
            class_schedule[(day_id, time_slot_id)] = class_name
        
        # Create the grid
        all_slots = self.morning_slots + ["Pause Déjeuner"] + self.afternoon_slots
        for row, slot in enumerate(all_slots, start=2):
            # Time label
            time_label = tk.Label(
                self.main_frame,
                text=slot,
                font=("Arial", 10),
                bg=self.colors['time_bg'],
                fg=self.colors['time_fg'],
                relief="raised",
                borderwidth=1
            )
            time_label.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
            
            # Create cells for each day
            for col in range(1, len(self.columns) + 1):
                self._create_regular_cell(row, col, slot, class_schedule)
    
    def _create_regular_cell(self, row, col, slot, class_schedule):
        """Create a regular schedule cell"""
        if slot == "Pause Déjeuner":
            # Lunch break cell
            lunch_frame = tk.Frame(
                self.main_frame,
                bg=self.colors['placeholder_bg'],
                relief="raised",
                borderwidth=1
            )
            lunch_frame.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
            
            lunch_label = tk.Label(
                lunch_frame,
                text="Pause Déjeuner",
                font=("Arial", 9),
                fg=self.colors['cell_fg'],
                bg=self.colors['placeholder_bg']
            )
            lunch_label.pack(fill='both', expand=True)
            
            self.cells[(row, col)] = lunch_frame
            return
        
        # Regular cell
        cell_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['cell_bg'],
            relief="raised",
            borderwidth=1
        )
        cell_frame.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
        
        # Get time_slot_id from slot
        time_slot_id = self._get_time_slot_id(slot)
        
        # Get class name from schedule_entries
        class_name = class_schedule.get((col, time_slot_id))
        
        if class_name:
            # Class label (top, read-only)
            class_label = tk.Label(
                cell_frame,
                text=class_name,
                font=("Arial", 9, "bold"),
                fg=self.colors['cell_fg'],
                bg=self.colors['cell_bg']
            )
            class_label.pack(fill='x')
            
            # Text widget for course content (editable)
            text_widget = tk.Text(
                cell_frame,
                font=("Arial", 9),
                fg=self.colors['cell_fg'],
                bg=self.colors['cell_bg'],
                wrap=tk.WORD,
                height=3,
                width=15
            )
            text_widget.pack_forget()  # Hidden initially
            
            # Placeholder
            placeholder = tk.Label(
                cell_frame,
                text="Cliquez pour éditer",
                font=("Arial", 9, "italic"),
                fg=self.colors['empty_fg'],
                bg=self.colors['placeholder_bg']
            )
            placeholder.pack(fill='both', expand=True)
            
            # Bind click event to show text widget
            def on_click(event, tw=text_widget, ph=placeholder):
                tw.pack(fill='both', expand=True)
                ph.pack_forget()
                tw.focus_set()
                self.unsaved_changes = True
            
            placeholder.bind('<Button-1>', on_click)
            text_widget.bind('<FocusOut>', lambda e, tw=text_widget, ph=placeholder: None)
            
            # Store cell reference
            self.cells[(row, col)] = (text_widget, placeholder, class_label)
        else:
            # Empty cell (no class scheduled)
            empty_label = tk.Label(
                cell_frame,
                text="",
                font=("Arial", 9),
                fg=self.colors['empty_fg'],
                bg=self.colors['placeholder_bg']
            )
            empty_label.pack(fill='both', expand=True)
            self.cells[(row, col)] = empty_label
    
    def _clear_existing_cells(self):
        """Clear all existing cells in the grid"""
        for cell in self.cells.values():
            if isinstance(cell, tuple):
                for widget in cell:
                    if widget:
                        widget.destroy()
            elif cell:
                cell.destroy()
        self.cells.clear()
    
    def _get_schedule_entries(self):
        """Get schedule_entries from database"""
        try:
            query = """
                SELECT se.day_id, se.time_slot_id, c.name as class_name
                FROM schedule_entries se
                JOIN classes c ON se.class_id = c.id
                ORDER BY se.day_id, se.time_slot_id
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error loading schedule_entries: {e}")
            return []
    
    def _get_time_slot_id(self, slot):
        """Get time_slot_id from slot string"""
        all_slots = self.morning_slots + self.afternoon_slots
        if slot in all_slots:
            return all_slots.index(slot) + 1
        return None
    
    def _on_week_change(self, event=None):
        """Handle week selection change"""
        self._create_schedule_grid()
        self.reload_schedule()
    
    def reload_schedule(self):
        """Reload schedule from database or distribute automatically"""
        try:
            selected_week = self.week_selector.get()
            if not selected_week:
                return
            
            # Extract week number
            week_number = int(selected_week.split("Semaine ")[1].split(" -")[0])
            
            # Check if data exists for this week
            self.cursor.execute("""
                SELECT day_id, slot_id, content
                FROM schedule_data
                WHERE week_number = ?
            """, (week_number,))
            saved_data = self.cursor.fetchall()
            
            if saved_data:
                # Load saved data
                self._load_saved_data(saved_data)
                messagebox.showinfo("Info", f"Données chargées pour la semaine {week_number}")
            else:
                # Distribute automatically
                self._distribute_ma_table_values(week_number)
                messagebox.showinfo("Info", f"Distribution automatique effectuée pour la semaine {week_number}")
        
        except Exception as e:
            logging.error(f"Error reloading schedule: {e}")
            messagebox.showerror("Erreur", f"Échec du rechargement :\n{str(e)}")
    
    def _load_saved_data(self, saved_data):
        """Load saved data into the grid"""
        for row_data in saved_data:
            day_id = row_data['day_id']
            slot_id = row_data['slot_id']
            content = row_data['content']
            
            # Convert day_id/slot_id to row/col
            row = self._get_row_from_time_slot(slot_id)
            col = day_id
            
            if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
                text_widget, placeholder, _ = self.cells[(row, col)]
                if text_widget:
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', content)
                    text_widget.pack(fill='both', expand=True)
                    placeholder.pack_forget()
                    placeholder.pack_forget()
    
    def _distribute_ma_table_values(self, week_number):
        """Distribute courses automatically from ma_table"""
        try:
            selected_week = self.week_selector.get()
            week_start = datetime.strptime(selected_week.split("du ")[1].split(" au")[0], "%d/%m/%Y")
            week_end = week_start + timedelta(days=5)
            school_year = "2024-2025"  # Extract from week or use current
            
            logging.info(f"Distributing courses for week {week_number}...")
            distribution = self.course_distributor.distribute_courses(week_number, week_start, week_end, school_year)
            logging.info(f"Distribution result: {distribution}")
            
            for class_id, slots in distribution.items():
                for day_id, time_slot_id, course_id in slots:
                    # Fetch course value from ma_table
                    course_value = self.course_distributor.fetch_course_value_by_id(course_id)
                    
                    if not course_value:
                        logging.warning(f"No course_value found for course_id: {course_id}")
                        continue
                    
                    # Map day_id and time_slot_id to row/col
                    row = self._get_row_from_time_slot(time_slot_id)
                    col = day_id
                    
                    logging.info(f"Assigning '{course_value}' to row {row}, col {col}")
                    
                    # Update cell
                    if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
                        text_widget, placeholder, _ = self.cells[(row, col)]
                        if text_widget:
                            text_widget.delete('1.0', tk.END)
                            text_widget.insert('1.0', course_value)
                            text_widget.pack(fill='both', expand=True)
                            placeholder.pack_forget()
        
        except Exception as e:
            logging.error(f"Error distributing courses: {e}")
            messagebox.showerror("Erreur", f"Échec de la distribution :\n{str(e)}")
    
    def _get_row_from_time_slot(self, time_slot_id):
        """Map time_slot_id to row in grid"""
        # time_slot_id: 1-4 (morning), 5 (lunch), 6-9 (afternoon)
        # rows: 2-5 (morning), 6 (lunch), 7-10 (afternoon)
        if time_slot_id <= 4:
            return 2 + time_slot_id - 1
        elif time_slot_id == 5:
            return 6  # Lunch
        else:
            return 2 + 4 + 1 + (time_slot_id - 6)
    
    def _get_slot_id_from_row(self, row):
        """Map row in grid to time_slot_id (inverse of _get_row_from_time_slot)"""
        # rows: 2-5 (morning), 6 (lunch), 7-10 (afternoon)
        # time_slot_id: 1-4 (morning), 5 (lunch), 6-9 (afternoon)
        if row <= 5:
            # Morning: row 2-5 → slot_id 1-4
            return row - 2 + 1
        elif row == 6:
            # Lunch
            return 5
        else:
            # Afternoon: row 7-10 → slot_id 6-9
            return row - 7 + 6
    
    def save_schedule(self):
        """Save schedule to database"""
        try:
            selected_week = self.week_selector.get()
            if not selected_week:
                messagebox.showwarning("Attention", "Veuillez sélectionner une semaine")
                return
            
            week_number = int(selected_week.split("Semaine ")[1].split(" -")[0])
            
            # Delete existing data for this week
            self.cursor.execute("DELETE FROM schedule_data WHERE week_number = ?", (week_number,))
            
            saved_count = 0
            for (row, col), cell in self.cells.items():
                if isinstance(cell, tuple):
                    text_widget, _, _ = cell
                    if text_widget and text_widget.winfo_ismapped():
                        content = text_widget.get('1.0', tk.END).strip()
                        if content:
                            # Convert row/col to day_id/slot_id
                            day_id = col
                            slot_id = self._get_slot_id_from_row(row)
                            
                            # Insert new data
                            self.cursor.execute("""
                                INSERT INTO schedule_data (week_number, day_id, slot_id, content)
                                VALUES (?, ?, ?, ?)
                            """, (week_number, day_id, slot_id, content))
                            saved_count += 1
            
            self.conn.commit()
            self.unsaved_changes = False
            
            messagebox.showinfo("Succès", f"Emploi du temps sauvegardé!\n{saved_count} cellule(s) enregistrée(s).")
            logging.info(f"Schedule saved for week {week_number}: {saved_count} cells")
        
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error saving schedule: {e}")
            messagebox.showerror("Erreur", f"Échec de la sauvegarde :\n{str(e)}")
    
    def print_to_pdf(self):
        """Export schedule to PDF"""
        try:
            messagebox.showinfo("Info", "Fonctionnalité PDF à implémenter.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du PDF :\n{str(e)}")
