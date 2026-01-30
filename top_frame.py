import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import sqlite3
from datetime import datetime, timedelta
from db_manager import DatabaseManager
from constants import (
    COLORS, MORNING_SLOTS, AFTERNOON_SLOTS, DAYS,
    get_school_year, format_week_text, get_week_dates
)
from pdf_generator import generate_pdf

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
        self.root.minsize(800, 600)
        
        self.db = DatabaseManager()
        self.cells = {}
        self.vacation_cells = {}  # To store vacation merged cells
        self.colors = COLORS
        self.morning_slots = MORNING_SLOTS
        self.afternoon_slots = AFTERNOON_SLOTS
        self.columns = DAYS
        
        try:
            self.db.setup_database()
            self.db.initialize_basic_data(self.columns, self.morning_slots, self.afternoon_slots)
            self._create_main_layout()
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            messagebox.showerror("Error", f"Failed to initialize application: {e}")
            raise
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_main_layout(self):
        """Create the main application layout"""
        self.main_frame = ttk.Frame(self.root, padding="10")
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
        
        for i in range(4):
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
        
        # Set current week
        current_week = datetime.now().isocalendar()[1]
        for i, week in enumerate(weeks):
            if str(current_week) in week:
                self.week_selector.current(i)
                break
        
        # Control buttons
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
        school_start, school_end = get_school_year()
        vacations = self.db.get_vacations()
        vacations = [(datetime.strptime(start, '%Y-%m-%d'), 
                     datetime.strptime(end, '%Y-%m-%d'),
                     desc) for start, end, desc in vacations]
        
        weeks = []
        current_date = school_start
        while current_date <= school_end:
            week_start = current_date - timedelta(days=current_date.weekday())
            week_end = week_start + timedelta(days=5)
            
            vacation_text = ""
            for vac_start, vac_end, vac_desc in vacations:
                if (week_start <= vac_end and week_end >= vac_start):
                    vacation_text = f" ({vac_desc})"
                    break
            
            weeks.append(format_week_text(week_start, vacation_text))
            current_date += timedelta(days=7)
        
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
        """Create the main schedule grid with vacation handling"""
        # Clear existing cells and vacation cells
        self._clear_existing_cells()

        # Get schedule entries and vacation information
        schedule_entries = self.db.get_schedule_entries()
        selected_week = self.week_selector.get()
        week_start = datetime.strptime(selected_week.split("du ")[1].split(" au")[0], "%d/%m/%Y")
        dates = get_week_dates(week_start, self.columns)

        # Create grid
        class_schedule = {}
        for day_id, time_slot_id, class_name in schedule_entries:
            class_schedule[(day_id, time_slot_id)] = class_name

        # Check for vacation days
        vacation_days = {}
        for day, date_str in dates.items():
            event_type, event_msg = self.db.check_events(date_str)
            if event_type == 'vacation':
                vacation_days[self.columns.index(day) + 1] = event_msg

        # Group consecutive vacation days
        vacation_groups = []
        current_group = []
        for col in sorted(vacation_days.keys()):
            if not current_group or col == current_group[-1] + 1:
                current_group.append(col)
            else:
                if current_group:
                    vacation_groups.append(current_group)
                current_group = [col]
        if current_group:
            vacation_groups.append(current_group)

        # Create merged cells for consecutive vacation days
        for group in vacation_groups:
            start_col = group[0]
            end_col = group[-1]
            vacation_msg = vacation_days[start_col]  # Use the first day's message
            self._create_merged_vacation_cell(start_col, end_col, vacation_msg)

        # Create the grid
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

            for col in range(1, len(self.columns) + 1):
                # Skip if this column is part of a merged vacation cell
                is_vacation = any(start <= col <= end for (start, end) in self.vacation_cells.keys())
                if not is_vacation:
                    self._create_regular_cell(row, col, slot, class_schedule)

    def _create_merged_vacation_cell(self, start_col, end_col, vacation_msg):
        """Create a merged cell for consecutive vacation days"""
        total_rows = len(self.morning_slots) + 2 + len(self.afternoon_slots)
        vacation_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['vacation_bg'],
            relief="solid",
            borderwidth=2
        )
        vacation_frame.grid(
            row=2,  # Start from first time slot
            column=start_col,
            rowspan=total_rows - 1,  # Span all rows except lunch break
            columnspan=end_col - start_col + 1,  # Span all consecutive columns
            sticky='nsew',
            padx=1, pady=1
        )
        vacation_label = tk.Label(
            vacation_frame,
            text=vacation_msg,
            font=("Arial", 11, "bold"),
            fg=self.colors['cell_fg'],
            bg=self.colors['vacation_bg'],
            wraplength=150,
            justify='center'
        )
        vacation_label.pack(expand=True)
        self.vacation_cells[(start_col, end_col)] = vacation_frame
    def _clear_existing_cells(self):
        """Clear all existing cells in the grid"""
        # Clear regular cells
        for cell in self.cells.values():
            if isinstance(cell, tuple):  # If it's a tuple (text_widget, placeholder, class_label)
                for widget in cell:
                    if widget:
                        widget.destroy()
            elif cell:  # If it's a single widget (e.g., lunch break frame)
                cell.destroy()
        self.cells.clear()

        # Clear vacation cells
        for cell in self.vacation_cells.values():
            cell.destroy()
        self.vacation_cells.clear()


    def _create_vacation_cell(self, col, vacation_msg):
        """Create a merged cell for vacation days"""
        total_rows = len(self.morning_slots) + 1 + len(self.afternoon_slots)
        
        # Create frame that spans all time slots
        vacation_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['vacation_bg'],
            relief="solid",
            borderwidth=2
        )
        
        # Position the frame
        vacation_frame.grid(
            row=2,  # Start from first time slot
            column=col,
            rowspan=total_rows - 1,  # Span all rows except lunch break
            sticky='nsew',
            padx=1, pady=1
        )
        
        # Add vacation label
        vacation_label = tk.Label(
            vacation_frame,
            text=vacation_msg,
            font=("Arial", 11, "bold"),
            fg=self.colors['cell_fg'],
            bg=self.colors['vacation_bg'],
            wraplength=150,
            justify='center'
        )
        vacation_label.pack(expand=True)
        
        self.vacation_cells[col] = vacation_frame

    def _create_regular_cell(self, row, col, slot, class_schedule):
        """Create a regular schedule cell"""
        if slot == "Pause Déjeuner":
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
        
        # Regular class cell
        cell_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['cell_bg'],
            relief="raised",
            borderwidth=1
        )
        cell_frame.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
        
        time_slot_id = self._get_time_slot_id(slot)
        class_name = class_schedule.get((col, time_slot_id))
        
        if class_name:
            # Class label
            class_label = tk.Label(
                cell_frame,
                text=class_name,
                font=("Arial", 9, "bold"),
                fg=self.colors['cell_fg'],
                bg=self.colors['cell_bg']
            )
            class_label.pack(fill='x')
            
            # Text widget for content
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
            
            # Placeholder
            placeholder = tk.Label(
                cell_frame,
                text="Cliquez pour éditer",
                font=("Arial", 9, "italic"),
                fg=self.colors['empty_fg'],
                bg=self.colors['placeholder_bg']
            )
            placeholder.pack(fill='both', expand=True)
            
            # Bind events
            placeholder.bind('<Button-1>', lambda e, r=row, c=col: self._on_cell_click(r, c))
            text_widget.bind('<FocusOut>', lambda e, r=row, c=col: self._on_cell_focus_out(r, c))
            
            self.cells[(row, col)] = (text_widget, placeholder, class_label)
        else:
            empty_label = tk.Label(
                cell_frame,
                text="",
                font=("Arial", 9),
                fg=self.colors['empty_fg'],
                bg=self.colors['placeholder_bg']
            )
            empty_label.pack(fill='both', expand=True)
            self.cells[(row, col)] = cell_frame
            
    def _get_time_slot_id(self, time_slot):
        """Get time slot ID from time slot string"""
        return self.db.get_time_slot_id(time_slot)

    def _on_cell_click(self, row, col):
        """Handle cell click event"""
        if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
            text_widget, placeholder, _ = self.cells[(row, col)]
            if text_widget:
                placeholder.pack_forget()
                text_widget.pack(fill='both', expand=True)
                text_widget.focus_set()

    def _on_cell_focus_out(self, row, col):
        """Handle cell focus out event"""
        if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
            text_widget, placeholder, _ = self.cells[(row, col)]
            if text_widget and not text_widget.get('1.0', tk.END).strip():
                text_widget.pack_forget()
                placeholder.pack(fill='both', expand=True)

    def _on_week_change(self, event=None):
        """Handle week change event"""
        self.reload_schedule()

    def reload_schedule(self):
        """Reload the schedule for the selected week"""
        try:
            selected_week = self.week_selector.get()
            week_start = datetime.strptime(selected_week.split("du ")[1].split(" au")[0], "%d/%m/%Y")
            dates = get_week_dates(week_start, self.columns)
            
            if not dates:
                messagebox.showerror("Error", "Failed to parse week dates")
                return
            
            week_number = int(selected_week.split("Semaine ")[1].split(" -")[0])
            
            # Clear current display
            self._create_schedule_grid()
            
            # Load saved data if exists
            saved_data = self.db.get_saved_schedule(week_number)
            if saved_data:
                self._load_saved_data(saved_data)
            else:
                self._distribute_ma_table_values(week_number)
            
        except Exception as e:
            logging.error(f"Error reloading schedule: {e}")
            messagebox.showerror("Error", f"Failed to reload schedule: {e}")

    def _load_saved_data(self, saved_data):
        """Load saved data into the grid"""
        for row, col, value in saved_data:
            if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
                text_widget, placeholder, _ = self.cells[(row, col)]
                if text_widget:
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', value)
                    text_widget.pack(fill='both', expand=True)
                    placeholder.pack_forget()

    def _distribute_ma_table_values(self, week_number):
        """Distribute values from ma_table across the grid, skipping vacation days"""
        ma_table_values = self.db.get_ma_table_values()
        if not ma_table_values:
            messagebox.showwarning("Warning", "No values found in ma_table")
            return
        
        # Get valid cells (excluding vacation days and lunch break)
        valid_cells = []
        for (row, col), cell in self.cells.items():
            if row != 6 and isinstance(cell, tuple):  # Skip lunch break row and non-editable cells
                if col not in self.vacation_cells:  # Skip vacation days
                    valid_cells.append((row, col))
        
        # Sort cells by column then row for consistent distribution
        valid_cells.sort(key=lambda x: (x[1], x[0]))
        
        # Calculate starting index for distribution
        total_values = len(ma_table_values)
        start_index = ((week_number - 1) * len(valid_cells)) % total_values
        
        # Distribute values
        for i, (row, col) in enumerate(valid_cells):
            value_index = (start_index + i) % total_values
            value = ma_table_values[value_index][1]
            
            text_widget, placeholder, _ = self.cells[(row, col)]
            if text_widget:
                text_widget.delete('1.0', tk.END)
                text_widget.insert('1.0', value)
                text_widget.pack(fill='both', expand=True)
                placeholder.pack_forget()

    def save_schedule(self):
        """Save the current schedule"""
        try:
            week_number = int(self.week_selector.get().split("Semaine ")[1].split(" -")[0])
            schedule_data = []
            
            for (row, col), cell in self.cells.items():
                if isinstance(cell, tuple):
                    text_widget, _, _ = cell
                    if text_widget and text_widget.winfo_ismapped():
                        content = text_widget.get('1.0', tk.END).strip()
                        if content:
                            schedule_data.append((row, col, content))
            
            if self.db.save_schedule(week_number, schedule_data):
                messagebox.showinfo("Success", "Schedule saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save schedule")
                
        except Exception as e:
            logging.error(f"Error saving schedule: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def print_to_pdf(self):
        """Generate PDF of the current schedule"""
        try:
            data = []
            
            # Get class info for header
            class_info = self.db.get_class_info()
            if class_info:
                class_name, level, school_year = class_info
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
            for col in range(1, len(self.columns) + 1):
                cell_row = list(row_range)[i]
                cell = self.cells.get((cell_row, col))
                
                if isinstance(cell, tuple):
                    text_widget, _, class_label = cell
                    if text_widget and text_widget.winfo_ismapped():
                        content = text_widget.get('1.0', tk.END).strip()
                        class_text = class_label.cget('text') if class_label else ""
                        content = f"{class_text}\n{content}" if content else class_text
                    else:
                        content = class_label.cget('text') if class_label else ""
                elif col in self.vacation_cells:
                    vacation_label = self.vacation_cells[col].winfo_children()[0]
                    content = vacation_label.cget('text')
                else:
                    content = ""
                    
                row.append(content)
            data.append(row)
        return data

    def _on_closing(self):
        """Handle application closing"""
        try:
            if messagebox.askokcancel("Quit", "Do you want to save before quitting?"):
                self.save_schedule()
            self.db.close()
            self.root.destroy()
        except Exception as e:
            logging.error(f"Error during application closing: {e}")
            self.root.destroy()


# Entry point
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CahierTextApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application crashed: {e}")
        messagebox.showerror("Critical Error", "Application crashed. Please check the logs.")