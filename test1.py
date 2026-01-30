import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog, Text
import sqlite3
from pdf_generator import generate_pdf
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='cahier_texte.log'
)

class CahierTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cahier de Texte")
        # Set minimum window size
        self.root.minsize(800, 600)
        self.cells = {}
        
        # Initialize database connection
        try:
            self.conn = sqlite3.connect('cahier_texte.db')
            self.cursor = self.conn.cursor()
            self._setup_database()
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            raise

        # Define color scheme
        self.colors = {
            'header_bg': '#2C3E50',
            'header_fg': 'white',
            'time_bg': '#34495E',
            'time_fg': 'white',
            'cell_bg': 'white',
            'cell_fg': '#2C3E50',
            'empty_fg': '#95A5A6',
            'hover_bg': '#ECF0F1',
            'hover_empty_fg': '#7F8C8D',
            'placeholder_bg': '#F0F0F0',
            'holiday_bg': '#FFB6C1',
            'absence_bg': '#FFE4E1',
            'vacation_bg': '#E0FFFF'
        }

        # Define time slots
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
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Handle application closing"""
        try:
            if messagebox.askokcancel("Quit", "Do you want to save before quitting?"):
                self.save_schedule()
            self.conn.close()
            self.root.destroy()
        except Exception as e:
            logging.error(f"Error during application closing: {e}")
            self.root.destroy()

    def _setup_database(self):
        """Initialize database tables"""
        try:
            # Create tables with proper error handling
            tables = [
                """CREATE TABLE IF NOT EXISTS week_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_number INTEGER,
                    cell_row INTEGER,
                    cell_col INTEGER,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS ma_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    valeur TEXT
                )""",
                """CREATE TABLE IF NOT EXISTS absences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    motif TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS jours_feries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    label TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS vacances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    level TEXT,
                    school_year TEXT
                )""",
                """CREATE TABLE IF NOT EXISTS days (
                    day_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS time_slots (
                    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS schedule_entries (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id INTEGER,
                    day_id INTEGER,
                    time_slot_id INTEGER,
                    FOREIGN KEY (class_id) REFERENCES classes (id),
                    FOREIGN KEY (day_id) REFERENCES days (day_id),
                    FOREIGN KEY (time_slot_id) REFERENCES time_slots (slot_id)
                )"""
            ]

            for table in tables:
                self.cursor.execute(table)

            self.conn.commit()
            self._initialize_basic_data()

        except sqlite3.Error as e:
            logging.error(f"Database setup error: {e}")
            messagebox.showerror("Database Error", f"Failed to setup database: {e}")
            raise

    def _initialize_basic_data(self):
        """Initialize basic data in the database"""
        try:
            # Initialize days
            self.cursor.execute("SELECT COUNT(*) FROM days")
            if self.cursor.fetchone()[0] == 0:
                for day in self.columns:
                    self.cursor.execute("INSERT INTO days (name) VALUES (?)", (day,))

            # Initialize time slots
            self.cursor.execute("SELECT COUNT(*) FROM time_slots")
            if self.cursor.fetchone()[0] == 0:
                all_slots = self.morning_slots + self.afternoon_slots
                for slot in all_slots:
                    start_time, end_time = slot.split(" - ")
                    self.cursor.execute(
                        "INSERT INTO time_slots (start_time, end_time) VALUES (?, ?)",
                        (start_time, end_time)
                    )

            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Data initialization error: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize basic data: {e}")
            raise


    def _create_main_layout(self):
        """Create the main application layout"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill='both', expand=True)
        
        # Configure grid weights
        for i in range(len(self.columns) + 1):
            self.main_frame.grid_columnconfigure(i, weight=1)
        
        self._create_top_frame()
        self._create_header_row()
        self._create_schedule_grid()



    def _create_schedule_grid(self):
        """Create the main schedule grid"""
        self.cells = {}
        
        # First, get the schedule entries from database
        self.cursor.execute("""
            SELECT se.day_id, se.time_slot_id, c.name 
            FROM schedule_entries se
            JOIN classes c ON se.class_id = c.id
            ORDER BY se.day_id, se.time_slot_id
        """)
        schedule_entries = self.cursor.fetchall()
        
        # Create a lookup dictionary for easier access
        class_schedule = {}
        for day_id, time_slot_id, class_name in schedule_entries:
            class_schedule[(day_id, time_slot_id)] = class_name

        for row, slot in enumerate(self.morning_slots + ["Pause Déjeuner"] + self.afternoon_slots, start=2):
            # Time slot label
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

            # Get time_slot_id for current row
            if slot != "Pause Déjeuner":
                current_slot = slot
            else:
                current_slot = None

            # Create cells for each day
            for col, day in enumerate(self.columns, start=1):
                cell_frame = tk.Frame(
                    self.main_frame,
                    bg=self.colors['cell_bg'],
                    relief="raised",
                    borderwidth=1
                )
                cell_frame.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)

                # Check if this slot has a class scheduled
                class_name = None
                if current_slot:
                    class_name = class_schedule.get((col, self._get_time_slot_id(current_slot)))

                if slot == "Pause Déjeuner":
                    # Create lunch break label
                    lunch_label = tk.Label(
                        cell_frame,
                        text="Pause Déjeuner",
                        font=("Arial", 9),
                        fg=self.colors['cell_fg'],
                        bg=self.colors['placeholder_bg']
                    )
                    lunch_label.pack(fill='both', expand=True)
                    self.cells[(row, col-1)] = (None, lunch_label, None)
                    continue

                if class_name:
                    # Create editable cell for scheduled classes
                    class_label = tk.Label(
                        cell_frame,
                        text=class_name,
                        font=("Arial", 9, "bold"),
                        fg=self.colors['cell_fg'],
                        bg=self.colors['cell_bg']
                    )
                    class_label.pack(fill='x')

                    text_widget = tk.Text(
                        cell_frame,
                        font=("Arial", 9),
                        fg=self.colors['cell_fg'],
                        bg=self.colors['cell_bg'],
                        wrap=tk.WORD,
                        height=3,
                        width=15
                    )
                    text_widget.pack_forget()

                    placeholder = tk.Label(
                        cell_frame,
                        text="Cliquez pour éditer",
                        font=("Arial", 9, "italic"),
                        fg=self.colors['empty_fg'],
                        bg=self.colors['placeholder_bg']
                    )
                    placeholder.pack(fill='both', expand=True)

                    # Bind click events only for editable cells
                    placeholder.bind('<Button-1>', lambda e, r=row, c=col-1: self._on_cell_click(r, c))
                    text_widget.bind('<FocusOut>', lambda e, r=row, c=col-1: self._on_cell_focus_out(r, c))

                    self.cells[(row, col-1)] = (text_widget, placeholder, class_label)
                else:
                    # Create non-editable cell for unscheduled slots
                    empty_label = tk.Label(
                        cell_frame,
                        text="",
                        font=("Arial", 9),
                        fg=self.colors['empty_fg'],
                        bg=self.colors['placeholder_bg']
                    )
                    empty_label.pack(fill='both', expand=True)
                    self.cells[(row, col-1)] = (None, empty_label, None)

    def _get_time_slot_id(self, time_slot):
        """Get time slot ID from time slot string"""
        try:
            self.cursor.execute(
                "SELECT slot_id FROM time_slots WHERE start_time || ' - ' || end_time = ?",
                (time_slot,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logging.error(f"Error getting time slot ID: {e}")
            return None

    def _show_event(self, row, col, event_type, message):
        """Display an event in a cell"""
        try:
            text_widget, placeholder, class_label = self.cells.get((row, col), (None, None, None))
            
            # Only modify cells that have scheduled classes
            if text_widget is None:
                return
                
            if text_widget:
                text_widget.pack_forget()
            if placeholder:
                placeholder.pack_forget()
            if class_label:
                class_label.pack_forget()
                
            color = self.colors.get(f'{event_type}_bg', self.colors['placeholder_bg'])
            event_label = tk.Label(
                self.main_frame,
                text=f"{class_label.cget('text')}\n{message}",
                font=("Arial", 9, "bold"),
                fg=self.colors['cell_fg'],
                bg=color,
                wraplength=150
            )
            event_label.grid(row=row, column=col+1, sticky='nsew', padx=1, pady=1)
        except Exception as e:
            logging.error(f"Error showing event: {e}")

    def _check_events(self, date_str):
        """Check for events on a specific date"""
        try:
            # Check vacations first (they have priority)
            self.cursor.execute(
                "SELECT 'Vacances' FROM vacances WHERE ? BETWEEN start_date AND end_date",
                (date_str,)
            )
            if self.cursor.fetchone():
                return ('vacation', 'Vacances Scolaires')

            # Then check holidays
            self.cursor.execute("SELECT label FROM jours_feries WHERE date = ?", (date_str,))
            holiday = self.cursor.fetchone()
            if holiday:
                return ('holiday', holiday[0])

            # Finally check absences
            self.cursor.execute("SELECT motif FROM absences WHERE date = ?", (date_str,))
            absence = self.cursor.fetchone()
            if absence:
                return ('absence', absence[0])

            return (None, None)
        except sqlite3.Error as e:
            logging.error(f"Error checking events: {e}")
            return (None, None)

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

    def _on_cell_click(self, row, col):
        """Handle cell click event"""
        if (row, col) in self.cells:
            text_widget, placeholder, _ = self.cells[(row, col)]
            placeholder.pack_forget()
            text_widget.pack(fill='both', expand=True)
            text_widget.focus_set()

    def _on_cell_focus_out(self, row, col):
        """Handle cell focus out event"""
        if (row, col) in self.cells:
            text_widget, placeholder, _ = self.cells[(row, col)]
            if not text_widget.get('1.0', tk.END).strip():
                text_widget.pack_forget()
                placeholder.pack(fill='both', expand=True)



def _create_top_frame(self):
    """Create the top frame with controls and week selection"""
    buttons_top = tk.Frame(self.main_frame)
    buttons_top.grid(row=0, column=0, columnspan=7, sticky='ew', pady=(0, 5))
    
    for i in range(4):
        buttons_top.grid_columnconfigure(i, weight=1)
    
    week_label = tk.Label(
        buttons_top,
        text="Semaine:",
        font=("Arial", 11, "bold")
    )
    week_label.grid(row=0, column=0, padx=5)
    
    # Get all weeks for the current school year
    weeks = self._get_school_year_weeks()
    self.week_var = tk.StringVar()
    
    # Create week selector with formatted dates
    self.week_selector = ttk.Combobox(
        buttons_top,
        textvariable=self.week_var,
        values=weeks,
        state="readonly",
        width=30  # Increased width to accommodate dates
    )
    self.week_selector.grid(row=0, column=1, padx=5)
    self.week_selector.bind('<<ComboboxSelected>>', self._on_week_change)
    
    # Set current week as default
    current_week = self._get_current_week_number()
    for i, week in enumerate(weeks):
        if str(current_week) in week:
            self.week_selector.current(i)
            break
    
    btn_width = 15
    buttons = [
        ("Reload", self.reload_schedule),
        ("Save", self.save_schedule),
        ("Print to PDF", self.print_to_pdf)
    ]
    
    for idx, (text, command) in enumerate(buttons):
        btn = tk.Button(
            buttons_top,
            text=text,
            command=command,
            bg=self.colors['header_bg'],
            fg=self.colors['header_fg'],
            font=("Arial", 11, "bold"),
            width=btn_width
        )
        btn.grid(row=0, column=idx+2, padx=5)

def _get_school_year_weeks(self):
    """Get all weeks for the current school year with vacation status"""
    # Define school year dates (September to July)
    current_date = datetime.now()
    if current_date.month < 9:  # If current month is before September
        start_year = current_date.year - 1
    else:
        start_year = current_date.year
        
    school_start = datetime(start_year, 9, 1)
    school_end = datetime(start_year + 1, 7, 7)  # Usually around July 7
    
    # Get all vacations
    self.cursor.execute("SELECT start_date, end_date, description FROM vacances")
    vacations = self.cursor.fetchall()
    vacations = [(datetime.strptime(start, '%Y-%m-%d'), 
                  datetime.strptime(end, '%Y-%m-%d'),
                  desc) for start, end, desc in vacations]
    
    weeks = []
    current_date = school_start
    while current_date <= school_end:
        # Get week start (Monday) and end (Saturday)
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=5)  # Saturday
        
        # Check if this week intersects with any vacation
        vacation_text = ""
        for vac_start, vac_end, vac_desc in vacations:
            if (week_start <= vac_end and week_end >= vac_start):
                vacation_text = f" ({vac_desc})"
                break
        
        week_number = week_start.isocalendar()[1]
        week_text = (f"Semaine {week_number} - du {week_start.strftime('%d/%m/%Y')} "
                    f"au {week_end.strftime('%d/%m/%Y')}{vacation_text}")
        weeks.append(week_text)
        
        current_date += timedelta(days=7)
    
    return weeks

def _get_current_week_number(self):
    """Get the current week number"""
    return datetime.now().isocalendar()[1]

def _get_week_dates(self, week_str):
    """Extract dates from week string and return dictionary of dates"""
    # Extract dates from the string "Semaine XX - du DD/MM/YYYY au DD/MM/YYYY"
    try:
        start_date_str = week_str.split("du ")[1].split(" au")[0]
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        
        dates = {}
        for i, day in enumerate(self.columns):
            date = start_date + timedelta(days=i)
            dates[day] = date.strftime('%Y-%m-%d')
        return dates
    except Exception as e:
        logging.error(f"Error parsing week string: {e}")
        return {}

def _on_week_change(self, event=None):
    """Handle week change event"""
    selected_week = self.week_selector.get()
    if "Vacances" in selected_week:
        messagebox.showinfo("Vacances", "Cette semaine est pendant les vacances scolaires.")
    self.reload_schedule()

def reload_schedule(self):
    """Reload the schedule for the selected week"""
    try:
        selected_week = self.week_selector.get()
        dates = self._get_week_dates(selected_week)
        
        if not dates:
            messagebox.showerror("Error", "Failed to parse week dates")
            return
            
        # Clear existing content
        self._clear_all_cells()
        
        # Get the week number from the selected week string
        week_number = int(selected_week.split("Semaine ")[1].split(" -")[0])
        
        # Check for saved data
        self.cursor.execute("""
            SELECT cell_row, cell_col, value 
            FROM week_schedule 
            WHERE week_number = ?
            ORDER BY cell_row, cell_col
        """, (week_number,))
        saved_data = self.cursor.fetchall()
        
        if saved_data:
            self._load_saved_data(saved_data, dates)
        else:
            self._distribute_ma_table_values(week_number, dates)
            
    except sqlite3.Error as e:
        logging.error(f"Error reloading schedule: {e}")
        messagebox.showerror("Database Error", f"Failed to reload schedule: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during reload: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")





    def _clear_all_cells(self):
        """Clear all cells in the grid"""
        try:
            for text_widget, placeholder, _ in self.cells.values():
                if text_widget:
                    text_widget.delete('1.0', tk.END)
                    text_widget.pack_forget()
                if placeholder:
                    placeholder.pack(fill='both', expand=True)
        except Exception as e:
            logging.error(f"Error clearing cells: {e}")

    def _load_saved_data(self, saved_data, dates):
        """Load saved data into the grid"""
        try:
            for cell_row, cell_col, value in saved_data:
                if (cell_row, cell_col) not in self.cells:
                    continue
                    
                day = self.columns[cell_col]
                date_str = dates[day]
                event_type, event_msg = self._check_events(date_str)
                
                if event_type:
                    self._show_event(cell_row, cell_col, event_type, event_msg)
                else:
                    text_widget, placeholder, class_label = self.cells[(cell_row, cell_col)]
                    if text_widget:
                        text_widget.delete('1.0', tk.END)
                        text_widget.insert('1.0', value)
                        text_widget.pack(fill='both', expand=True)
                        placeholder.pack_forget()
        except Exception as e:
            logging.error(f"Error loading saved data: {e}")
            messagebox.showerror("Error", "Failed to load saved data")

    def _distribute_ma_table_values(self, week_number, dates):
        """Distribute values from ma_table across the grid"""
        try:
            self.cursor.execute("SELECT id, valeur FROM ma_table ORDER BY id")
            ma_table_values = self.cursor.fetchall()
            
            if not ma_table_values:
                logging.warning("No values found in ma_table")
                messagebox.showwarning("Warning", "No values found in ma_table")
                return
            
            valid_cells = []
            for (row, col), (text_widget, _, class_label) in sorted(
                self.cells.items(),
                key=lambda x: (x[0][1], x[0][0])
            ):
                if row != 6:  # Skip lunch break row
                    day = self.columns[col]
                    date_str = dates[day]
                    event_type, event_msg = self._check_events(date_str)
                    
                    if event_type:
                        self._show_event(row, col, event_type, event_msg)
                    else:
                        valid_cells.append((row, col))
            
            total_values = len(ma_table_values)
            start_index = ((week_number - 1) * len(valid_cells)) % total_values
            
            for i, (row, col) in enumerate(valid_cells):
                value_index = (start_index + i) % total_values
                value = ma_table_values[value_index][1]
                
                text_widget, placeholder, _ = self.cells[(row, col)]
                if text_widget:
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', value)
                    text_widget.pack(fill='both', expand=True)
                    placeholder.pack_forget()

        except sqlite3.Error as e:
            logging.error(f"Database error during distribution: {e}")
            messagebox.showerror("Error", "Failed to distribute values")
        except Exception as e:
            logging.error(f"Error distributing values: {e}")
            messagebox.showerror("Error", "An unexpected error occurred")

    def _show_event(self, row, col, event_type, message):
        """Display an event in a cell"""
        try:
            text_widget, placeholder, class_label = self.cells[(row, col)]
            if text_widget:
                text_widget.pack_forget()
            if placeholder:
                placeholder.pack_forget()
                
            color = self.colors.get(f'{event_type}_bg', self.colors['placeholder_bg'])
            event_label = tk.Label(
                self.main_frame,
                text=message,
                font=("Arial", 9, "bold"),
                fg=self.colors['cell_fg'],
                bg=color,
                wraplength=150
            )
            event_label.grid(row=row, column=col+1, sticky='nsew', padx=1, pady=1)
        except Exception as e:
            logging.error(f"Error showing event: {e}")

    def save_schedule(self):
        """Save the current schedule to the database"""
        try:
            week_number = int(self.week_var.get())
            
            # Begin transaction
            self.cursor.execute("BEGIN TRANSACTION")
            
            # Delete existing data for this week
            self.cursor.execute("DELETE FROM week_schedule WHERE week_number = ?", 
                              (week_number,))
            
            # Save current state
            for (row, col), (text_widget, placeholder, class_label) in self.cells.items():
                if row != 6:  # Skip lunch break row
                    if text_widget and text_widget.winfo_ismapped():
                        content = text_widget.get('1.0', tk.END).strip()
                        if content:  # Only save non-empty cells
                            self.cursor.execute("""
                                INSERT INTO week_schedule 
                                (week_number, cell_row, cell_col, value)
                                VALUES (?, ?, ?, ?)
                            """, (week_number, row, col, content))
            
            # Commit transaction
            self.conn.commit()
            messagebox.showinfo("Success", "Schedule saved successfully!")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logging.error(f"Database error during save: {e}")
            messagebox.showerror("Error", f"Failed to save schedule: {e}")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error saving schedule: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def print_to_pdf(self):
        """Generate PDF of the current schedule"""
        try:
            data = []
            
            # Get class info for header
            self.cursor.execute("SELECT name, level, school_year FROM classes WHERE id = 1")
            result = self.cursor.fetchone()
            if result:
                class_name, level, school_year = result
                header = f"Cahier de Texte - {class_name} ({level} - {school_year})"
            else:
                header = "Cahier de Texte"
                
            data.append([header])
            
            # Column headers
            headers = ["Horaire"] + self.columns
            data.append(headers)
            
            # Add all schedule data
            morning_data = self._get_schedule_data(self.morning_slots, range(2, 6))
            data.extend(morning_data)
            
            # Add lunch break
            data.append(["12:30 - 14:30"] + ["Pause Déjeuner"] * len(self.columns))
            
            # Add afternoon data
            afternoon_data = self._get_schedule_data(self.afternoon_slots, range(7, 11))
            data.extend(afternoon_data)

            # Get save location from user
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"cahier_texte_week_{self.week_var.get()}.pdf"
            )
            
            if filename:
                generate_pdf(data, filename)
                messagebox.showinfo("Success", "PDF generated successfully!")
                
        except Exception as e:
            logging.error(f"Error generating PDF: {e}")
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")

    def _get_schedule_data(self, time_slots, row_range):
        """Helper method to get schedule data for PDF generation"""
        data = []
        for i, horaire in enumerate(time_slots):
            row = [horaire]
            for j in range(len(self.columns)):
                cell_row = list(row_range)[i]
                text_widget, _, _ = self.cells[(cell_row, j)]
                if text_widget and text_widget.winfo_ismapped():
                    content = text_widget.get('1.0', tk.END).strip()
                else:
                    content = ""
                row.append(content)
            data.append(row)
        return data


# Entry point
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CahierTextApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application crashed: {e}")
        messagebox.showerror("Critical Error", "Application crashed. Please check the logs.")