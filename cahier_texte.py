import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime, timedelta
from db_manager import DatabaseManager
from course_distribution import CourseDistributionManager
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
        logging.info("Initializing CourseDistributionManager...")
        self.course_distributor = CourseDistributionManager("cahier_texte.db")  # Ensure the DB path is correct
        logging.info("CourseDistributionManager initialized successfully.")
        
        self.cells = {}
        self.unsaved_changes = False
        self.vacation_cells = {}
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
        """Create the main schedule grid with vacation, holiday, and absence handling."""
        self._clear_existing_cells()
        schedule_entries = self.db.get_schedule_entries()
        selected_week = self.week_selector.get()
        week_start = datetime.strptime(selected_week.split("du ")[1].split(" au")[0], "%d/%m/%Y")
        dates = get_week_dates(week_start, self.columns)

        # Check for events (vacations, holidays, absences)
        event_days = {}
        for day, date_str in dates.items():
            event_type, event_msg = self.db.check_events(date_str)
            if event_type:  # If there's an event (vacation, holiday, or absence)
                event_days[self.columns.index(day) + 1] = (event_type, event_msg)

        # Create merged cells for consecutive event days
        self._create_merged_vacation_cells(event_days)

        # Create the grid
        class_schedule = {}
        for day_id, time_slot_id, class_name in schedule_entries:
            class_schedule[(day_id, time_slot_id)] = class_name

        for row, slot in enumerate(self.morning_slots + ["Pause Déjeuner"] + self.afternoon_slots, start=2):
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
                if not any(start <= col <= end for (start, end) in self.vacation_cells.keys()):
                    self._create_regular_cell(row, col, slot, class_schedule)

    def _create_merged_vacation_cells(self, event_days):
        """Create merged cells for consecutive vacation, holiday, or absence days."""
        total_rows = len(self.morning_slots) + 2 + len(self.afternoon_slots)
        
        for col, (event_type, event_msg) in event_days.items():
            # Determine the background color based on the event type
            if event_type == 'vacation':
                bg_color = self.colors['vacation_bg']
            elif event_type == 'holiday':
                bg_color = self.colors['holiday_bg']
            elif event_type == 'absence':
                bg_color = self.colors['absence_bg']
            else:
                bg_color = self.colors['default_bg']  # Fallback color
            
            # Create the merged cell
            event_frame = tk.Frame(
                self.main_frame,
                bg=bg_color,
                relief="solid",
                borderwidth=2
            )
            event_frame.grid(
                row=2,
                column=col,
                rowspan=total_rows - 1,
                sticky='nsew',
                padx=1, pady=1
            )
            
            event_label = tk.Label(
                event_frame,
                text=event_msg,
                font=("Arial", 11, "bold"),
                fg=self.colors['cell_fg'],
                bg=bg_color,
                wraplength=150,
                justify='center'
            )
            event_label.pack(expand=True)
            
            # Store the merged cell for later reference
            self.vacation_cells[(col, col)] = event_frame
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

        for cell in self.vacation_cells.values():
            cell.destroy()
        self.vacation_cells.clear()












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
            
            placeholder.bind('<Button-1>', lambda e, r=row, c=col: self._on_cell_click(r, c))
            text_widget.bind('<FocusOut>', lambda e, r=row, c=col: self._on_cell_focus_out(r, c))
            
            # Detect changes in the text widget
            text_widget.bind('<KeyRelease>', lambda e: self._on_cell_change())
            
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

    def _on_cell_change(self):
        """Handle cell content change"""
        self.unsaved_changes = True






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
        if self.unsaved_changes:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before switching weeks?",
                icon="warning"
            )
            if response is None:  # User clicked "Cancel"
                return
            elif response:  # User clicked "Yes"
                self.save_schedule()
            # If user clicked "No", proceed without saving
        
        self.reload_schedule()
        self.unsaved_changes = False  # Reset the flag after reloading

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
            
            self._create_schedule_grid()
            
            self.db.cursor.execute("""
                SELECT cell_row, cell_col, value
                FROM schedule_data
                WHERE week_number = ?
            """, (week_number,))
            saved_data = self.db.cursor.fetchall()
            
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
        try:
            selected_week = self.week_selector.get()
            week_start = datetime.strptime(selected_week.split("du ")[1].split(" au")[0], "%d/%m/%Y")
            week_end = week_start + timedelta(days=5)  # Assuming the week ends 6 days after the start

            logging.info(f"Distributing courses for week {week_number}...")
            distribution = self.course_distributor.distribute_courses(week_number, week_start, week_end)
            logging.info(f"Distribution: {distribution}")
            
            for group, slots in distribution.items():
                for day_id, time_slot_id, course_id in slots:
                    # Fetch course_value from the table using course_id
                    course_value = self.db._fetch_course_value_by_id(course_id)  # Implement this method
                    
                    if not course_value:
                        logging.warning(f"No course_value found for course_id: {course_id}")
                        continue  # Skip if no course_value is found
                    
                    row = self._get_row_from_time_slot(time_slot_id)
                    col = day_id
                    
                    logging.info(f"Assigning course value {course_value} to row {row}, col {col}")
                    
                    if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
                        text_widget, placeholder, _ = self.cells[(row, col)]
                        if text_widget:
                            text_widget.delete('1.0', tk.END)
                            text_widget.insert('1.0', course_value)  # Assign course_value
                            text_widget.pack(fill='both', expand=True)
                            placeholder.pack_forget()
        except Exception as e:
            logging.error(f"Error distributing ma_table values: {e}")
            messagebox.showerror("Error", f"Failed to distribute values: {e}")
   
    def _get_row_from_time_slot(self, time_slot_id):
        """Map time_slot_id to the corresponding row in the grid"""
        if time_slot_id <= len(self.morning_slots):
            return 2 + time_slot_id - 1
        else:
            return 2 + len(self.morning_slots) + 1 + (time_slot_id - len(self.morning_slots) - 1)

















    def save_schedule(self):
        try:
            week_number = int(self.week_selector.get().split("Semaine ")[1].split(" -")[0])
            schedule_data = []
            course_progress = {}
            
            for (row, col), cell in self.cells.items():
                if isinstance(cell, tuple):
                    text_widget, _, class_label = cell
                    if text_widget and text_widget.winfo_ismapped():
                        content = text_widget.get('1.0', tk.END).strip()
                        if content:
                            # Delete existing data first
                            self.db.cursor.execute("""
                                DELETE FROM schedule_data 
                                WHERE week_number = ? AND cell_row = ? AND cell_col = ?
                            """, (week_number, row, col))
                            
                            # Then insert new data
                            self.db.cursor.execute("""
                                INSERT INTO schedule_data (week_number, cell_row, cell_col, value)
                                VALUES (?, ?, ?, ?)
                            """, (week_number, row, col, content))
                            
                            class_name = class_label.cget('text')
                            if class_name:
                                class_id = int(class_name.replace('TCSF', ''))
                                current_course = int(content)
                                course_progress[class_id] = max(current_course, 
                                    course_progress.get(class_id, 0))
            
            for class_id, last_course in course_progress.items():
                # Delete existing progress first
                self.db.cursor.execute("""
                    DELETE FROM class_course_progress
                    WHERE class_id = ? AND last_week = ?
                """, (class_id, week_number))
                
                # Then insert new progress
                self.db.cursor.execute("""
                    INSERT INTO class_course_progress (class_id, last_course_id, last_week)
                    VALUES (?, ?, ?)
                """, (class_id, last_course, week_number))
                
            self.db.conn.commit()
            self.unsaved_changes = False  # Reset the flag after saving
            messagebox.showinfo("Success", "Schedule saved successfully!")
            
        except Exception as e:
            logging.error(f"Error saving schedule: {e}")
            messagebox.showerror("Error", f"Failed to save schedule: {e}")
            self.db.conn.rollback()





















    def print_to_pdf(self):
        """Generate PDF of the current schedule"""
        try:
            logging.info("Starting PDF generation...")
            data = []
            
            # Add title row
            selected_week = self.week_selector.get()
            title = f"{selected_week}"
            data.append([title])

            # Add column headers
            headers = ["Horaire"] + self.columns
            data.append(headers)
            logging.info(f"Added headers: {headers}")
            
            # Get current schedule state
            schedule_state = []
            
            # Create mapping between time slots and grid rows
            grid_mapping = {}
            current_grid_row = 2  # Start after header
            
            # Map morning slots
            for idx, slot in enumerate(self.morning_slots):
                grid_mapping[current_grid_row] = idx
                current_grid_row += 1
            
            # Skip lunch break row
            current_grid_row += 1
            
            # Map afternoon slots
            for idx, slot in enumerate(self.afternoon_slots, start=len(self.morning_slots) + 1):
                grid_mapping[current_grid_row] = idx
                current_grid_row += 1
            
            # Initialize schedule state with time slots
            for slot in self.morning_slots:
                schedule_state.append([slot])
            schedule_state.append(["12:30 - 14:30"])  # Lunch break
            for slot in self.afternoon_slots:
                schedule_state.append([slot])
                
            logging.info(f"Initial schedule state created with {len(schedule_state)} rows")
            
            # Fill in the data for each day
            for col_idx, day in enumerate(self.columns, start=1):
                logging.info(f"Processing day: {day} at column {col_idx}")
                
                # Check if this is a vacation day
                is_vacation_day = False
                vacation_text = None
                
                for vac_range, vac_frame in self.vacation_cells.items():
                    if col_idx >= vac_range[0] and col_idx <= vac_range[1]:
                        is_vacation_day = True
                        if vac_frame and vac_frame.winfo_children():
                            vacation_text = vac_frame.winfo_children()[0].cget('text')
                        break
                
                # Fill column for this day
                for row_idx in range(len(schedule_state)):
                    if is_vacation_day:
                        if row_idx == 0:
                            schedule_state[row_idx].append({
                                'text': vacation_text or "Vacation",
                                'type': 'vacation',
                                'merge': len(schedule_state)
                            })
                        else:
                            schedule_state[row_idx].append("")
                    else:
                        if row_idx == len(self.morning_slots):  # Lunch break
                            schedule_state[row_idx].append("Pause Déjeuner")
                        else:
                            # Get the correct grid row for this time slot
                            grid_row = next(
                                (grid_row for grid_row, idx in grid_mapping.items() 
                                 if idx == row_idx),
                                None
                            )
                            
                            if grid_row is not None:
                                cell = self.cells.get((grid_row, col_idx))
                                content = self._get_cell_content(cell) if cell else ""
                                schedule_state[row_idx].append(content)
                            else:
                                schedule_state[row_idx].append("")
            
            # Add processed schedule state to data
            data.extend(schedule_state)
            
            logging.info(f"Final data structure has {len(data)} rows")
            for idx, row in enumerate(data):
                logging.info(f"Row {idx}: {row}")
            
            if len(data) < 2:
                raise ValueError("Not enough data to generate PDF")
            
            # Get save filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"cahier_texte_week_{self.week_var.get()}.pdf"
            )
            
            if filename:
                generate_pdf(data, filename)
                messagebox.showinfo("Success", "PDF generated successfully!")
                
        except Exception as e:
            logging.error(f"Error in print_to_pdf: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

    def _get_cell_content(self, cell):
        """Helper method to extract content from a cell"""
        try:
            if cell is None:
                return ""
                
            if isinstance(cell, tuple):
                text_widget, _, class_label = cell
                if text_widget and text_widget.winfo_ismapped():
                    content = text_widget.get('1.0', tk.END).strip()
                    class_text = class_label.cget('text') if class_label else ""
                    return f"{class_text}\n{content}" if content else class_text
                else:
                    return class_label.cget('text') if class_label else ""
            elif hasattr(cell, 'winfo_children') and cell.winfo_children():
                return cell.winfo_children()[0].cget('text')
            
            return ""
            
        except Exception as e:
            logging.error(f"Error getting cell content: {str(e)}")
            return ""

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
    
    def _get_time_slot_id(self, time_slot):
        """Get time slot ID from time slot string"""
        return self.db.get_time_slot_id(time_slot)

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



