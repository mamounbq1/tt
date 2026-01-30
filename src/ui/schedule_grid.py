import tkinter as tk
from course_dist.constants import COLORS

class ScheduleGrid:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.cells = {}
        self._create_header_row()
        self._create_schedule_grid()

    def _create_header_row(self):
        """Create the header row with day labels"""
        for col, text in enumerate(["Horaire"] + self.app.columns):
            label = tk.Label(
                self.parent,
                text=text,
                font=("Arial", 11, "bold"),
                bg=self.app.colors['header_bg'],
                fg=self.app.colors['header_fg'],
                relief="raised",
                height=2,
                borderwidth=1
            )
            label.grid(row=1, column=col, sticky='nsew', padx=1, pady=1)

    def _create_schedule_grid(self):
        """Create the main schedule grid"""
        schedule_entries = self.app.db.get_schedule_entries()
        
        # Create a lookup dictionary for easier access
        class_schedule = {}
        for day_id, time_slot_id, class_name in schedule_entries:
            class_schedule[(day_id, time_slot_id)] = class_name

        for row, slot in enumerate(self.app.morning_slots + ["Pause Déjeuner"] + self.app.afternoon_slots, start=2):
            # Time slot label
            time_label = tk.Label(
                self.parent,
                text=slot,
                font=("Arial", 10),
                bg=self.app.colors['time_bg'],
                fg=self.app.colors['time_fg'],
                relief="raised",
                borderwidth=1
            )
            time_label.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)

            # Get time_slot_id for current row
            current_slot = None if slot == "Pause Déjeuner" else slot

            # Create cells for each day
            for col, day in enumerate(self.app.columns, start=1):
                cell_frame = tk.Frame(
                    self.parent,
                    bg=self.app.colors['cell_bg'],
                    relief="raised",
                    borderwidth=1
                )
                cell_frame.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)

                if slot == "Pause Déjeuner":
                    lunch_label = tk.Label(
                        cell_frame,
                        text="Pause Déjeuner",
                        font=("Arial", 9),
                        fg=self.app.colors['cell_fg'],
                        bg=self.app.colors['placeholder_bg']
                    )
                    lunch_label.pack(fill='both', expand=True)
                    self.cells[(row, col-1)] = (None, lunch_label, None)
                    continue

                # Check if this slot has a class scheduled
                class_name = class_schedule.get((col, self.app._get_time_slot_id(current_slot))) if current_slot else None

                if class_name:
                    # Create editable cell for scheduled classes
                    class_label = tk.Label(
                        cell_frame,
                        text=class_name,
                        font=("Arial", 9, "bold"),
                        fg=self.app.colors['cell_fg'],
                        bg=self.app.colors['cell_bg']
                    )
                    class_label.pack(fill='x')

                    text_widget = tk.Text(
                        cell_frame,
                        font=("Arial", 9),
                        fg=self.app.colors['cell_fg'],
                        bg=self.app.colors['cell_bg'],
                        wrap=tk.WORD,
                        height=3,
                        width=15
                    )
                    text_widget.pack_forget()

                    placeholder = tk.Label(
                        cell_frame,
                        text="Cliquez pour éditer",
                        font=("Arial", 9, "italic"),
                        fg=self.app.colors['empty_fg'],
                        bg=self.app.colors['placeholder_bg']
                    )
                    placeholder.pack(fill='both', expand=True)

                    # Bind click events only for editable cells
                    placeholder.bind('<Button-1>', lambda e, r=row, c=col-1: self.app._on_cell_click(r, c))
                    text_widget.bind('<FocusOut>', lambda e, r=row, c=col-1: self.app._on_cell_focus_out(r, c))

                    self.cells[(row, col-1)] = (text_widget, placeholder, class_label)
                else:
                    # Create non-editable cell for unscheduled slots
                    empty_label = tk.Label(
                        cell_frame,
                        text="",
                        font=("Arial", 9),
                        fg=self.app.colors['empty_fg'],
                        bg=self.app.colors['placeholder_bg']
                    )
                    empty_label.pack(fill='both', expand=True)
                    self.cells[(row, col-1)] = (None, empty_label, None)