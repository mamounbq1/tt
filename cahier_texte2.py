from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import sys
import os
import logging
from datetime import datetime, timedelta
from course_dist.db_manager import DatabaseManager
from course_dist.constants import (
    MORNING_SLOTS, AFTERNOON_SLOTS, DAYS,
    get_school_year, format_week_text, get_week_dates
)
from course_dist.pdf_generator import generate_pdf
from test import generate_pdf_grouped

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='cahier_texte.log'
)

class CahierTextFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.db = DatabaseManager()
        # Automatic course distribution is now disabled; no CourseDistributionManager needed.
        self.cells = {}           # Dictionary for the table cells
        self.unsaved_changes = False
        self.vacation_cells = {}  # For storing merged cells (vacations, holidays, absences)
        self.morning_slots = MORNING_SLOTS
        self.afternoon_slots = AFTERNOON_SLOTS
        self.columns = DAYS
        
        try:
            self.db.setup_database()
            self.db.initialize_basic_data(self.columns, self.morning_slots, self.afternoon_slots)
            self.setup_ui()
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            raise

    def setup_ui(self):
        nav_frame = ttk.Frame(self, padding="10") 
        nav_frame.pack(fill='x', pady=(0, 10))
        
        back_button = ttk.Button(
            nav_frame,
            text="Retour au tableau de bord",
            command=lambda: self.controller.show_frame("HomeFrame")
        )
        back_button.pack(side='left', padx=5)
        
        week_frame = ttk.Frame(nav_frame)
        week_frame.pack(side='left', expand=True, padx=20)
        
        ttk.Label(week_frame, text="Semaine:", style='Body.TLabel').pack(side='left', padx=5)
        
        self.week_var = tk.StringVar()
        weeks = self._get_school_year_weeks()
        self.week_selector = ttk.Combobox(
            week_frame,
            textvariable=self.week_var,
            values=weeks,
            state="readonly",
            width=30,
            style='Combo.TCombobox'
        )
        self.week_selector.pack(side='left', padx=5)
        self.week_selector.bind('<<ComboboxSelected>>', self._on_week_change)
        
        action_frame = ttk.Frame(nav_frame)
        action_frame.pack(side='right')
        
        buttons = [
            ("Recharger", self.reload_schedule),
            ("Sauvegarder", self.save_schedule),
            ("Imprimer PDF", self.print_pdf_choice)
        ]
        for text, command in buttons:
            ttk.Button(
                action_frame,
                text=text,
                command=command,
                style='Action.TButton'
            ).pack(side='left', padx=5)

        # Scrollable container
        grid_container = ttk.Frame(self)
        grid_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(grid_container)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(grid_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.main_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig('win', width=e.width-4))
        self.canvas.addtag_all('win')
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            
        for i in range(len(self.columns) + 1):
            self.main_frame.grid_columnconfigure(i, weight=1)
        
        self._create_header_row()
        self._create_schedule_grid()
        
        # Update the scroll region after content is added
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Set the current week in the week selector
        current_week = datetime.now().isocalendar()[1]
        for i, week in enumerate(weeks):
            if str(current_week) in week:
                self.week_selector.current(i)
                break

    def print_pdf_choice(self):
        """Opens a dialog that lets the user choose which PDF design to use via graphical previews with hover effects."""
        choice_window = tk.Toplevel(self.winfo_toplevel())
        choice_window.title("Choisissez le design d'impression PDF")
        choice_window.geometry("600x400")
        choice_window.configure(bg="#f5f5f7")
        choice_window.transient(self.winfo_toplevel())
        choice_window.grab_set()

        style = ttk.Style()
        style.configure("Modern.TLabel",
                    font=("Helvetica", 14),
                    background="#f5f5f7",
                    foreground="#1d1d1f")

        header_label = ttk.Label(
            choice_window,
            text="Sélectionnez le design d'impression PDF",
            style="Modern.TLabel"
        )
        header_label.pack(pady=20)

        previews_frame = tk.Frame(choice_window, bg="#f5f5f7")
        previews_frame.pack(pady=20)

        def create_shadow(canvas, x1, y1, x2, y2, shadow_width=3):
            for i in range(shadow_width):
                shadow_color = f"#{int(0 * 255):02x}{int(0 * 255):02x}{int(0 * 255):02x}"
                canvas.create_rectangle(
                    x1 + i, y1 + i, x2 + i, y2 + i,
                    fill="", outline=shadow_color,
                    stipple="gray50"
                )

        # ---------- Standard PDF Preview ----------
        standard_frame = tk.Frame(previews_frame, bg="#f5f5f7")
        standard_frame.grid(row=0, column=0, padx=30)
        
        standard_canvas = tk.Canvas(standard_frame, width=220, height=220, bg="white",
                                highlightthickness=0)
        standard_canvas.pack()
        
        create_shadow(standard_canvas, 12, 12, 208, 208)
        
        standard_canvas.create_rectangle(10, 10, 210, 210, fill="white", outline="#e1e1e1", width=2)
        standard_canvas.create_rectangle(10, 10, 210, 40, fill="#007AFF", outline="")
        standard_canvas.create_text(50, 25, text="Horaire", font=("Helvetica", 10, "bold"), fill="white")
        standard_canvas.create_text(130, 25, text="Lundi", font=("Helvetica", 10, "bold"), fill="white")
        
        standard_canvas.create_rectangle(10, 40, 210, 80, fill="#f8f8f8", outline="#e1e1e1")
        standard_canvas.create_text(50, 60, text="08:00", font=("Helvetica", 10))
        standard_canvas.create_text(130, 60, text="Math", font=("Helvetica", 10))
        
        standard_canvas.create_rectangle(10, 80, 210, 120, fill="white", outline="#e1e1e1")
        standard_canvas.create_text(50, 100, text="09:00", font=("Helvetica", 10))
        standard_canvas.create_text(130, 100, text="Phys", font=("Helvetica", 10))
        
        standard_label = tk.Label(standard_frame, text="PDF Standard", font=("Helvetica", 12, "bold"),
                                bg="#f5f5f7", fg="#1d1d1f")
        standard_label.pack(pady=10)

        # ---------- Grouped PDF Preview ----------
        grouped_frame = tk.Frame(previews_frame, bg="#f5f5f7")
        grouped_frame.grid(row=0, column=1, padx=30)
        
        grouped_canvas = tk.Canvas(grouped_frame, width=220, height=220, bg="white",
                                highlightthickness=0)
        grouped_canvas.pack()
        
        create_shadow(grouped_canvas, 12, 12, 208, 208)
        
        grouped_canvas.create_rectangle(10, 10, 210, 210, fill="white", outline="#e1e1e1", width=2)
        grouped_canvas.create_rectangle(10, 10, 210, 40, fill="#FF2D55", outline="")
        grouped_canvas.create_text(110, 25, text="TCSF1", font=("Helvetica", 12, "bold"), fill="white")
        
        grouped_canvas.create_rectangle(10, 40, 210, 70, fill="#f8f8f8", outline="#e1e1e1")
        grouped_canvas.create_text(40, 55, text="Lundi", font=("Helvetica", 9))
        grouped_canvas.create_text(110, 55, text="08:00-09:30", font=("Helvetica", 9))
        grouped_canvas.create_text(170, 55, text="Math", font=("Helvetica", 9, "bold"))
        
        grouped_canvas.create_rectangle(10, 70, 210, 100, fill="white", outline="#e1e1e1")
        grouped_canvas.create_text(40, 85, text="Mardi", font=("Helvetica", 9))
        grouped_canvas.create_text(110, 85, text="09:00-10:30", font=("Helvetica", 9))
        grouped_canvas.create_text(170, 85, text="Phys", font=("Helvetica", 9, "bold"))
        
        grouped_label = tk.Label(grouped_frame, text="PDF Groupé", font=("Helvetica", 12, "bold"),
                            bg="#f5f5f7", fg="#1d1d1f")
        grouped_label.pack(pady=10)

        def on_enter(event):
            widget = event.widget
            widget.configure(bg="#fafafa")
            widget.scale("all", 110, 110, 1.02, 1.02)
            items = widget.find_all()
            for item in items:
                if widget.type(item) == "rectangle":
                    current_fill = widget.itemcget(item, "fill")
                    if current_fill == "#007AFF":
                        widget.itemconfig(item, fill="#1e90ff")
                    elif current_fill == "#FF2D55":
                        widget.itemconfig(item, fill="#ff4d79")

        def on_leave(event):
            widget = event.widget
            widget.configure(bg="white")
            widget.scale("all", 110, 110, 1/1.02, 1/1.02)
            items = widget.find_all()
            for item in items:
                if widget.type(item) == "rectangle":
                    current_fill = widget.itemcget(item, "fill")
                    if current_fill == "#1e90ff":
                        widget.itemconfig(item, fill="#007AFF")
                    elif current_fill == "#ff4d79":
                        widget.itemconfig(item, fill="#FF2D55")

        standard_canvas.bind("<Enter>", on_enter)
        standard_canvas.bind("<Leave>", on_leave)
        grouped_canvas.bind("<Enter>", on_enter)
        grouped_canvas.bind("<Leave>", on_leave)

        def select_standard(event):
            choice_window.destroy()
            self.print_to_pdf()

        def select_grouped(event):
            choice_window.destroy()
            self.print_to_pdf_grouped()

        standard_canvas.bind("<Button-1>", select_standard)
        grouped_canvas.bind("<Button-1>", select_grouped)

        info_label = tk.Label(
            choice_window,
            text="Cliquez sur un design pour sélectionner",
            font=("Helvetica", 10),
            fg="#666666",
            bg="#f5f5f7"
        )
        info_label.pack(pady=10)

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
                if week_start <= vac_end and week_end >= vac_start:
                    vacation_text = f" ({vac_desc})"
                    break
            weeks.append(format_week_text(week_start, vacation_text))
            current_date += timedelta(days=7)
        return weeks

    def _clear_existing_cells(self):
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

    def _create_header_row(self):
        for col, text in enumerate(["Horaire"] + self.columns):
            label = ttk.Label(
                self.main_frame,
                text=text,
                style='Header.TLabel'
            )
            label.grid(row=1, column=col, sticky='nsew', padx=1, pady=1)

    def _create_schedule_grid(self):
        self._clear_existing_cells()
        schedule_entries = self.db.get_schedule_entries()
        selected_week = self.week_selector.get()
        
        try:
            week_start = datetime.strptime(selected_week.split("du ")[1].split(" au")[0], "%d/%m/%Y")
        except Exception as e:
            logging.error("Error parsing week: " + str(e))
            messagebox.showerror("Erreur", "Erreur lors de la création de la grille")
            return

        dates = get_week_dates(week_start, self.columns)
        event_days = {}
        
        # Check for events (vacation, holiday, absence) on each day
        for day, date_str in dates.items():
            event_type, event_msg = self.db.check_events(date_str)
            if event_type:
                event_days[self.columns.index(day) + 1] = (event_type, event_msg)
        
        # Create regular grid first
        class_schedule = {}
        for day_id, time_slot_id, class_name in schedule_entries:
            class_schedule[(day_id, time_slot_id)] = class_name

        current_row = 2
        for horaire in self.morning_slots:
            self._create_row(current_row, horaire, class_schedule)
            current_row += 1

        separator = ttk.Frame(self.main_frame, style='Separator.TFrame')
        separator.grid(row=current_row, column=0, columnspan=len(self.columns) + 1, sticky='ew', pady=5)
        current_row += 1

        for horaire in self.afternoon_slots:
            self._create_row(current_row, horaire, class_schedule)
            current_row += 1

        # Hide cells for vacation days and create merged cells
        for col in event_days.keys():
            for key in list(self.cells.keys()):
                if key[1] == col:
                    cell = self.cells[key]
                    if isinstance(cell, tuple):
                        text_widget, placeholder, class_label = cell
                        for widget in (text_widget, placeholder, class_label):
                            if widget:
                                widget.grid_remove()
                    else:
                        cell.grid_remove()

        self._create_merged_vacation_cells(event_days)

    def _create_merged_vacation_cells(self, event_days):
        total_rows = len(self.morning_slots) + 2 + len(self.afternoon_slots)
        for col, (event_type, event_msg) in event_days.items():
            if event_type == 'vacation':
                bg_color = self.controller.colors['vacation_bg'] if hasattr(self.controller, 'colors') else "#FFC0CB"
            elif event_type == 'holiday':
                bg_color = self.controller.colors['holiday_bg'] if hasattr(self.controller, 'colors') else "#ADD8E6"
            elif event_type == 'absence':
                bg_color = self.controller.colors['absence_bg'] if hasattr(self.controller, 'colors') else "#90EE90"
            else:
                bg_color = self.controller.colors.get('default_bg', "#ffffff")
            
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
                fg=self.controller.colors['cell_fg'] if hasattr(self.controller, 'colors') else "#000000",
                bg=bg_color,
                wraplength=150,
                justify='center'
            )
            event_label.pack(expand=True, fill='both')
            self.vacation_cells[(col, col)] = event_frame

    def _create_row(self, row, horaire, class_schedule):
        time_label = ttk.Label(
            self.main_frame,
            text=horaire,
            style='Time.TLabel'
        )
        time_label.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
        
        for col in range(len(self.columns)):
            cell_frame = ttk.Frame(
                self.main_frame,
                style='Cell.TFrame'
            )
            cell_frame.grid(row=row, column=col + 1, sticky='nsew', padx=1, pady=1)
            cell_frame.grid_rowconfigure(1, weight=1)
            cell_frame.grid_columnconfigure(0, weight=1)

            time_slot_id = self._get_time_slot_id(horaire)
            class_name = None
            for entry in self.db.get_schedule_entries():
                if entry[0] == col + 1 and entry[1] == time_slot_id:
                    class_name = entry[2]
                    break

            if class_name:
                class_label = ttk.Label(
                    cell_frame,
                    text=class_name,
                    style='Cell.TLabel'
                )
                class_label.grid(row=0, column=0, sticky='nsew')
                
                container_frame = ttk.Frame(cell_frame)
                container_frame.grid(row=1, column=0, sticky='nsew', pady=1)
                container_frame.grid_columnconfigure(0, weight=1)
                container_frame.grid_rowconfigure(0, weight=1)
                
                text_widget = tk.Text(
                    container_frame,
                    wrap=tk.WORD,
                    height=3,
                    width=15
                )
                text_widget.grid(row=0, column=0, sticky='nsew')
                text_widget.grid_remove()
                
                placeholder = ttk.Label(
                    container_frame,
                    text="Cliquez pour éditer",
                    style='Empty.TLabel'
                )
                placeholder.grid(row=0, column=0, sticky='nsew')
                
                self.cells[(row, col + 1)] = (text_widget, placeholder, class_label)
                
                # Bind left-click to open the modal window
                for widget in (cell_frame, class_label, placeholder):
                    widget.bind('<Button-1>', lambda e, r=row, c=col+1: self._open_cell_edit_window(r, c))
                text_widget.bind('<FocusOut>', lambda e, r=row, c=col+1: self._on_cell_focus_out(r, c))
                text_widget.bind('<KeyRelease>', lambda e: self._on_cell_change())
            else:
                empty_label = ttk.Label(
                    cell_frame,
                    text="",
                    style='Empty.TLabel'
                )
                empty_label.grid(row=0, column=0, sticky='nsew', rowspan=2)
                
                empty_label.bind('<Button-1>', lambda e, r=row, c=col+1: self._open_cell_edit_window(r, c))
                
                self.cells[(row, col + 1)] = cell_frame

    def _on_cell_change(self):
        self.unsaved_changes = True

    def _on_cell_focus_out(self, row, col):
        if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
            text_widget, placeholder, _ = self.cells[(row, col)]
            if text_widget and not text_widget.get('1.0', tk.END).strip():
                text_widget.grid_remove()
                placeholder.grid()

    def _on_week_change(self, event=None):
        if self.unsaved_changes:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before switching weeks?",
                icon="warning"
            )
            if response is None:
                return
            elif response:
                self.save_schedule()
        self.reload_schedule()
        self.unsaved_changes = False

    def reload_schedule(self):
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
            # Automatic course distribution is disabled; cells remain empty until manually edited.
        except Exception as e:
            logging.error(f"Error reloading schedule: {e}")
            messagebox.showerror("Error", f"Failed to reload schedule: {e}")

    def _load_saved_data(self, saved_data):
        for row, col, value in saved_data:
            if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
                text_widget, placeholder, _ = self.cells[(row, col)]
                if text_widget:
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', value)
                    text_widget.grid()
                    placeholder.grid_remove()

    def _get_row_from_time_slot(self, time_slot_id):
        if time_slot_id <= len(self.morning_slots):
            return 2 + time_slot_id - 1
        else:
            return 2 + len(self.morning_slots) + 1 + (time_slot_id - len(self.morning_slots) - 1)

    def _get_time_slot_id(self, time_slot):
        return self.db.get_time_slot_id(time_slot)

    def print_to_pdf(self):
        try:
            logging.info("Starting PDF generation...")
            data = []
            selected_week = self.week_selector.get()
            title = f"{selected_week}"
            data.append([title])
            headers = ["Horaire"] + self.columns
            data.append(headers)
            logging.info(f"Added headers: {headers}")
            grid_mapping = {}
            current_grid_row = 2
            for idx, slot in enumerate(self.morning_slots):
                grid_mapping[current_grid_row] = idx
                current_grid_row += 1
            current_grid_row += 1
            for idx, slot in enumerate(self.afternoon_slots, start=len(self.morning_slots)+1):
                grid_mapping[current_grid_row] = idx
                current_grid_row += 1
            schedule_state = []
            for slot in self.morning_slots:
                schedule_state.append([slot])
            schedule_state.append(["12:30 - 14:30"])
            for slot in self.afternoon_slots:
                schedule_state.append([slot])
            logging.info(f"Initial schedule state created with {len(schedule_state)} rows")
            for col_idx, day in enumerate(self.columns, start=1):
                logging.info(f"Processing day: {day} at column {col_idx}")
                is_vacation_day = False
                vacation_text = None
                for vac_range, vac_frame in self.vacation_cells.items():
                    if col_idx >= vac_range[0] and col_idx <= vac_range[1]:
                        is_vacation_day = True
                        if vac_frame and vac_frame.winfo_children():
                            vacation_text = vac_frame.winfo_children()[0].cget('text')
                        break
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
                        if row_idx == len(self.morning_slots):
                            schedule_state[row_idx].append("Pause Déjeuner")
                        else:
                            grid_row = next((grid_row for grid_row, idx in grid_mapping.items() if idx == row_idx), None)
                            if grid_row is not None:
                                cell = self.cells.get((grid_row, col_idx))
                                content = self._get_cell_content(cell) if cell else ""
                                schedule_state[row_idx].append(content)
                            else:
                                schedule_state[row_idx].append("")
            data.extend(schedule_state)
            logging.info(f"Final data structure has {len(data)} rows")
            for idx, row in enumerate(data):
                logging.info(f"Row {idx}: {row}")
            if len(data) < 2:
                raise ValueError("Not enough data to generate PDF")
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"cahier_texte_week_{int(self.week_selector.get().split('Semaine ')[1].split(' -')[0])}.pdf"
            )
            if filename:
                generate_pdf(data, filename)
                messagebox.showinfo("Success", "PDF generated successfully!")
        except Exception as e:
            logging.error(f"Error in print_to_pdf: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

    def print_to_pdf_grouped(self):
        try:
            logging.info("Starting grouped PDF generation...")
            selected_week = self.week_selector.get()
            week_start = datetime.strptime(selected_week.split("du ")[1].split(" au")[0], "%d/%m/%Y")
            week_dates = get_week_dates(week_start, self.columns)
            grid_mapping = {}
            current_grid_row = 2
            for idx, slot in enumerate(self.morning_slots):
                grid_mapping[current_grid_row] = idx
                current_grid_row += 1
            current_grid_row += 1
            for idx, slot in enumerate(self.afternoon_slots, start=len(self.morning_slots) + 1):
                grid_mapping[current_grid_row] = idx
                current_grid_row += 1
            schedule_state = []
            for slot in self.morning_slots:
                schedule_state.append([slot])
            schedule_state.append(["12:30 - 14:30"])
            for slot in self.afternoon_slots:
                schedule_state.append([slot])
            logging.info("Initial schedule state created with {} rows".format(len(schedule_state)))
            for col_idx, day in enumerate(self.columns, start=1):
                logging.info("Processing day: {} at column {}".format(day, col_idx))
                is_vacation_day = False
                vacation_text = None
                for vac_range, vac_frame in self.vacation_cells.items():
                    if col_idx >= vac_range[0] and col_idx <= vac_range[1]:
                        is_vacation_day = True
                        if vac_frame and vac_frame.winfo_children():
                            vacation_text = vac_frame.winfo_children()[0].cget('text')
                        break
                for row_idx in range(len(schedule_state)):
                    if is_vacation_day:
                        if row_idx == 0:
                            grid_row = next((gr for gr, idx in grid_mapping.items() if idx == row_idx), None)
                            normal_content = ""
                            if grid_row is not None:
                                cell = self.cells.get((grid_row, col_idx))
                                normal_content = self._get_cell_content(cell) if cell else ""
                            if normal_content:
                                orig_class = normal_content.split("\n", 1)[0].strip()
                            else:
                                orig_class = "Unknown"
                            schedule_state[row_idx].append({
                                'class': orig_class,
                                'text': vacation_text or "Vacation",
                                'type': 'vacation',
                                'merge': len(schedule_state)
                            })
                        else:
                            schedule_state[row_idx].append("")
                    else:
                        if row_idx == len(self.morning_slots):
                            schedule_state[row_idx].append("Pause Déjeuner")
                        else:
                            grid_row = next((gr for gr, idx in grid_mapping.items() if idx == row_idx), None)
                            if grid_row is not None:
                                cell = self.cells.get((grid_row, col_idx))
                                content = self._get_cell_content(cell) if cell else ""
                                schedule_state[row_idx].append(content)
                            else:
                                schedule_state[row_idx].append("")
            logging.info("Final schedule state has {} rows".format(len(schedule_state)))
            pdf_data = {}
            for row in schedule_state:
                time_slot = row[0]
                if time_slot == "12:30 - 14:30":
                    continue
                for col in range(1, len(row)):
                    cell_val = row[col]
                    if not cell_val:
                        continue
                    day_name = self.columns[col - 1]
                    date_str = week_dates.get(day_name, day_name)
                    if isinstance(cell_val, dict) and cell_val.get('type') in ['vacation', 'holiday', 'absence']:
                        group_key = cell_val.get('class', cell_val.get('type').title())
                        entry = {
                            "date": date_str,
                            "time": time_slot,
                            "content": "",
                            "observation": cell_val.get('text', cell_val.get('type'))
                        }
                        if group_key not in pdf_data:
                            pdf_data[group_key] = []
                        pdf_data[group_key].append(entry)
                    else:
                        parts = cell_val.split("\n", 1)
                        group_key = parts[0].strip()
                        content = parts[1].strip() if len(parts) > 1 else ""
                        entry = {
                            "date": date_str,
                            "time": time_slot,
                            "content": content,
                            "observation": ""
                        }
                        if group_key not in pdf_data:
                            pdf_data[group_key] = []
                        pdf_data[group_key].append(entry)
            logging.info("PDF data grouped by class/event: {}".format(pdf_data))
            if not pdf_data:
                messagebox.showerror("Error", "No schedule entries found to generate grouped PDF.")
                return
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile="cahier_texte_week_{}_grouped.pdf".format(
                    int(self.week_selector.get().split("Semaine ")[1].split(" -")[0])
                )
            )
            if filename:
                generate_pdf_grouped(pdf_data, filename)
                messagebox.showinfo("Success", "Grouped PDF generated successfully!")
        except Exception as e:
            logging.error("Error in print_to_pdf_grouped: " + str(e), exc_info=True)
            messagebox.showerror("Error", "Failed to generate grouped PDF: " + str(e))

    def _get_cell_content(self, cell):
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
  
    def _open_cell_edit_window(self, row, col):
        """
        Opens a modern, beautifully styled modal window for cell editing.
        The window offers three options:
        - Custom Content: Enter free text.
        - Choose Course: Select a course from a list (from ma_table) and edit its details.
        - Select Type: Pick from preset types (Controle, Soutien, Projet, Autre).
        The OS title bar is removed and replaced with a custom draggable title bar.
        """
        # Create the modal window and remove OS decorations.
        edit_window = tk.Toplevel(self)
        edit_window.overrideredirect(True)  # Remove the native title bar (and its close button)
        edit_window.title("Edit Cell")
        edit_window.geometry("520x640")
        edit_window.configure(bg="#ecf0f1")  # Light, modern background color
        edit_window.transient(self.winfo_toplevel())
        edit_window.grab_set()
        edit_window.minsize(500, 600)
        edit_window.update_idletasks()

        # Ensure the window is visible
        edit_window.deiconify()
        edit_window.lift()

        # Retrieve initial content if available
        initial_content = ""
        if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
            text_widget = self.cells[(row, col)][0]
            initial_content = text_widget.get("1.0", tk.END).strip()

        # Create unique style names based on the window id
        window_id = str(edit_window.winfo_id())
        local_style = {
            'frame': f"Modern.TFrame.{window_id}",
            'label': f"Modern.TLabel.{window_id}",
            'header': f"Header.TLabel.{window_id}",
            'radio': f"Modern.TRadiobutton.{window_id}",
            'button': f"Modern.TButton.{window_id}"
        }

        style = ttk.Style()
        # Configure custom styles and explicitly set layouts
        style.configure(local_style['frame'], background="#ecf0f1")
        style.layout(local_style['frame'], style.layout("TFrame"))
        
        style.configure(local_style['label'], background="#ecf0f1", foreground="#34495e", font=("Segoe UI", 11))
        style.layout(local_style['label'], style.layout("TLabel"))
        
        style.configure(local_style['header'], background="#ecf0f1", foreground="#2c3e50", font=("Segoe UI", 16, "bold"))
        style.layout(local_style['header'], style.layout("TLabel"))
        
        style.configure(local_style['radio'], background="#ecf0f1", foreground="#34495e", font=("Segoe UI", 11))
        style.layout(local_style['radio'], style.layout("TRadiobutton"))
        
        style.configure(local_style['button'], font=("Segoe UI", 11), padding=10,
                        foreground="#ffffff", background="#3498db")
        style.layout(local_style['button'], style.layout("TButton"))

        # Create new styles for the Cancel and Apply buttons
        style.configure("Cancel.TButton", background="#ff9999", foreground="white",
                        font=("Segoe UI", 11), padding=10)
        style.map("Cancel.TButton", background=[("active", "#ff7777")])
        style.configure("Apply.TButton", background="#99ff99", foreground="white",
                        font=("Segoe UI", 11), padding=10)
        style.map("Apply.TButton", background=[("active", "#77ff77")])

        # Cleanup function to reset styles and close the window
        def cleanup_styles():
            for key in local_style.values():
                try:
                    style.configure(key, {})
                except tk.TclError:
                    pass
            edit_window.destroy()
        edit_window.protocol("WM_DELETE_WINDOW", cleanup_styles)

        # --- Custom Title Bar ---
        # Create a custom title bar to replace the OS one.
        title_bar = tk.Frame(edit_window, bg="#34495e", relief="raised", bd=0)
        title_bar.pack(fill="x")
        title_label = tk.Label(title_bar, text="Edit Cell Content", bg="#34495e",
                            fg="white", font=("Segoe UI", 14, "bold"))
        title_label.pack(expand=True)
        # Enable dragging of the window using the custom title bar.
        def start_move(event):
            edit_window.x = event.x
            edit_window.y = event.y
        def do_move(event):
            x = edit_window.winfo_x() - edit_window.x + event.x
            y = edit_window.winfo_y() - edit_window.y + event.y
            edit_window.geometry(f"+{x}+{y}")
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        # Main container below the custom title bar with padding
        main_container = ttk.Frame(edit_window, style=local_style['frame'])
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Separator (no header here since we have the title bar)
        ttk.Separator(main_container, orient="horizontal").pack(fill="x", pady=(0, 20))

        # Variable to track the selected option; default is "custom"
        selected_option = tk.StringVar(value="custom")

        # Options (Radio Buttons)
        options_frame = ttk.Frame(main_container, style=local_style['frame'])
        options_frame.pack(fill="x", pady=(0, 20))
        radio_custom = ttk.Radiobutton(
            options_frame, text="Custom Content", variable=selected_option,
            value="custom", style=local_style['radio'], command=lambda: show_frame("custom")
        )
        radio_custom.pack(side="left", padx=10)
        radio_course = ttk.Radiobutton(
            options_frame, text="Choose Course", variable=selected_option,
            value="course", style=local_style['radio'], command=lambda: show_frame("course")
        )
        radio_course.pack(side="left", padx=10)
        radio_type = ttk.Radiobutton(
            options_frame, text="Select Type", variable=selected_option,
            value="type", style=local_style['radio'], command=lambda: show_frame("type")
        )
        radio_type.pack(side="left", padx=10)

        # Create separate frames for each editing option
        frames = {}

        # --- Custom Content Frame ---
        custom_frame = ttk.Frame(main_container, style=local_style['frame'])
        frames["custom"] = custom_frame
        custom_label = ttk.Label(custom_frame, text="Enter your custom content below:", style=local_style['label'])
        custom_label.pack(anchor="w", pady=(0, 10))
        custom_text = tk.Text(custom_frame, height=10, width=50, font=("Segoe UI", 11),
                            wrap="word", relief="solid", borderwidth=1)
        if initial_content:
            custom_text.insert("1.0", initial_content)
        custom_text.pack(fill="both", expand=True)

        # --- Course Selection Frame ---
        course_frame = ttk.Frame(main_container, style=local_style['frame'])
        frames["course"] = course_frame
        course_label = ttk.Label(course_frame, text="Select a course:", style=local_style['label'])
        course_label.pack(anchor="w", pady=(0, 10))
        # Query courses from the "ma_table" (assumed structure: id, valeur)
        try:
            courses = [row[0] for row in self.db.cursor.execute("SELECT valeur FROM ma_table").fetchall()]
        except Exception as e:
            logging.error(f"Error querying courses from ma_table: {e}")
            courses = []
        course_var = tk.StringVar()
        course_combobox = ttk.Combobox(
            course_frame, textvariable=course_var, values=courses, state="readonly",
            font=("Segoe UI", 11), width=45
        )
        course_combobox.pack(fill="x", pady=(0, 10))
        course_details_label = ttk.Label(course_frame, text="Course details:", style=local_style['label'])
        course_details_label.pack(anchor="w", pady=(10, 10))
        course_text = tk.Text(course_frame, height=8, width=50, font=("Segoe UI", 11),
                            wrap="word", relief="solid", borderwidth=1)
        course_text.pack(fill="both", expand=True)
        def on_course_select(event):
            selected_course = course_combobox.get()
            course_text.delete("1.0", tk.END)
            course_text.insert(tk.END, selected_course)
        course_combobox.bind("<<ComboboxSelected>>", on_course_select)

        # --- Type Selection Frame ---
        type_frame = ttk.Frame(main_container, style=local_style['frame'])
        frames["type"] = type_frame
        type_label = ttk.Label(type_frame, text="Select the type:", style=local_style['label'])
        type_label.pack(anchor="w", pady=(0, 10))
        type_options = ["Controle", "Soutien", "Projet", "Autre"]
        type_var = tk.StringVar(value=type_options[0])
        type_combobox = ttk.Combobox(
            type_frame, textvariable=type_var, values=type_options, state="readonly",
            font=("Segoe UI", 11), width=45
        )
        type_combobox.pack(fill="x")

        # Function to switch between option frames
        def show_frame(frame_key):
            for key, frame in frames.items():
                frame.pack_forget()
            frames[frame_key].pack(fill="both", expand=True, pady=(20, 0))
        # Show the default option frame
        show_frame("custom")

        # Button Frame
        button_frame = ttk.Frame(main_container, style=local_style['frame'])
        button_frame.pack(fill="x", pady=(30, 0))
        def apply_changes():
            option = selected_option.get()
            if option == "custom":
                content = custom_text.get("1.0", tk.END).strip()
            elif option == "course":
                content = course_text.get("1.0", tk.END).strip()
            elif option == "type":
                content = type_combobox.get().strip()
            else:
                content = ""
            if (row, col) in self.cells and isinstance(self.cells[(row, col)], tuple):
                text_widget, placeholder, _ = self.cells[(row, col)]
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", content)
                text_widget.grid()
                placeholder.grid_remove()
                self.unsaved_changes = True
            edit_window.destroy()
        apply_button = ttk.Button(button_frame, text="Apply Changes", style="Apply.TButton", command=apply_changes)
        apply_button.pack(side="right", padx=(5, 0))
        cancel_button = ttk.Button(button_frame, text="Cancel", style="Cancel.TButton", command=edit_window.destroy)
        cancel_button.pack(side="right", padx=5)

        # Center the window on the screen
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')

    def save_schedule(self):
        try:
            week_text = self.week_selector.get()
            week_number = int(week_text.split("Semaine ")[1].split(" -")[0])
            year = int(week_text.split("/")[-1].strip())
            course_progress = {}
            for (row, col), cell in self.cells.items():
                if isinstance(cell, tuple):
                    text_widget, _, class_label = cell
                    if text_widget and text_widget.winfo_ismapped():
                        content = text_widget.get('1.0', tk.END).strip()
                        if content:
                            self.db.cursor.execute("""
                                DELETE FROM schedule_data 
                                WHERE week_number = ? AND cell_row = ? AND cell_col = ? AND year = ?
                            """, (week_number, row, col, year))
                            self.db.cursor.execute("""
                                INSERT INTO schedule_data (week_number, cell_row, cell_col, value, year)
                                VALUES (?, ?, ?, ?, ?)
                            """, (week_number, row, col, content, year))
                            self.db.cursor.execute("""
                                SELECT id FROM ma_table WHERE valeur = ?
                            """, (content,))
                            result = self.db.cursor.fetchone()
                            if result:
                                cours_id = result[0]
                                class_name = class_label.cget('text')
                                if class_name:
                                    self.db.cursor.execute("""
                                        SELECT id FROM classes WHERE name = ?
                                    """, (class_name,))
                                    result = self.db.cursor.fetchone()
                                    if result:
                                        class_id = result[0]
                                        course_progress[class_id] = max(cours_id, course_progress.get(class_id, 0))
            for class_id, last_course in course_progress.items():
                self.db.cursor.execute("""
                    DELETE FROM class_course_progress
                    WHERE class_id = ? AND last_week = ? AND year = ?
                """, (class_id, week_number, year))
                self.db.cursor.execute("""
                    INSERT INTO class_course_progress (class_id, last_course_id, last_week, year)
                    VALUES (?, ?, ?, ?)
                """, (class_id, last_course, week_number, year))
            self.db.conn.commit()
            self.unsaved_changes = False
            messagebox.showinfo("Success", "Schedule saved successfully!")
        except Exception as e:
            logging.error(f"Error saving schedule: {e}")
            messagebox.showerror("Error", f"Failed to save schedule: {e}")
            self.db.conn.rollback()

    def _on_closing(self):
        try:
            if messagebox.askokcancel("Quit", "Do you want to save before quitting?"):
                self.save_schedule()
            self.db.close()
            self.Cahier_texte_window.destroy()
        except Exception as e:
            logging.error(f"Error during application closing: {e}")
            self.Cahier_texte_window.destroy()
