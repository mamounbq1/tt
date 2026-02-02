"""
Schedule/Timetable Management Frame
Allows viewing and editing the weekly schedule
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from src.utils.theme import ThemeManager
from src.utils.config import DB_PATH


class ScheduleFrame(ttk.Frame):
    """Frame for managing weekly schedules"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.database
        
        # Schedule data
        self.current_week = 1
        self.max_weeks = 36  # School year weeks
        self.selected_cell = None
        self.cell_frames = {}  # Store references to schedule cells
        
        self.build_ui()
        self.load_schedule_data()
    
    def build_ui(self):
        """Build the user interface"""
        # Main container with padding
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill='both', expand=True)
        
        # Top bar with back button and title
        top_bar = ttk.Frame(main_container)
        top_bar.pack(fill='x', pady=(0, 10))
        
        back_btn = ThemeManager.create_button(
            top_bar,
            text='← Retour',
            command=self.go_back
        )
        back_btn.pack(side='left')
        
        title = ThemeManager.create_label(
            top_bar,
            text='📅 Emploi du Temps',
            style='Heading.TLabel'
        )
        title.pack(side='left', padx=20)
        
        # Week selector
        week_frame = ttk.Frame(top_bar)
        week_frame.pack(side='right')
        
        ttk.Label(week_frame, text='Semaine:').pack(side='left', padx=5)
        
        prev_btn = ThemeManager.create_button(
            week_frame,
            text='←',
            command=self.previous_week
        )
        prev_btn.pack(side='left')
        
        self.week_label = ttk.Label(
            week_frame,
            text=f'{self.current_week}/{self.max_weeks}',
            font=('Arial', 12, 'bold')
        )
        self.week_label.pack(side='left', padx=10)
        
        next_btn = ThemeManager.create_button(
            week_frame,
            text='→',
            command=self.next_week
        )
        next_btn.pack(side='left')
        
        # Action buttons bar
        action_bar = ttk.Frame(main_container)
        action_bar.pack(fill='x', pady=(0, 10))
        
        save_btn = ThemeManager.create_button(
            action_bar,
            text='💾 Sauvegarder',
            command=self.save_schedule
        )
        save_btn.pack(side='left', padx=5)
        
        clear_btn = ThemeManager.create_button(
            action_bar,
            text='🗑️ Effacer la semaine',
            command=self.clear_week
        )
        clear_btn.pack(side='left', padx=5)
        
        edit_btn = ThemeManager.create_button(
            action_bar,
            text='✏️ Modifier cellule',
            command=self.edit_cell
        )
        edit_btn.pack(side='left', padx=5)
        
        # Schedule grid container with scrollbar
        grid_container = ttk.Frame(main_container)
        grid_container.pack(fill='both', expand=True)
        
        # Canvas with scrollbar for large schedule
        canvas = tk.Canvas(grid_container, bg='white')
        scrollbar = ttk.Scrollbar(grid_container, orient='vertical', command=canvas.yview)
        
        self.schedule_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        
        canvas_frame = canvas.create_window((0, 0), window=self.schedule_frame, anchor='nw')
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Adjust canvas window width to fill canvas
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        self.schedule_frame.bind('<Configure>', configure_scroll_region)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        
        # Build the schedule grid
        self.build_schedule_grid()
    
    def build_schedule_grid(self):
        """Build the weekly schedule grid"""
        # Clear existing grid
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        self.cell_frames.clear()
        
        # Load days and time slots from database
        days = self.get_days()
        time_slots = self.get_time_slots()
        
        if not days or not time_slots:
            error_label = ttk.Label(
                self.schedule_frame,
                text='⚠️ Erreur: Impossible de charger les données',
                font=('Arial', 14)
            )
            error_label.grid(row=0, column=0, padx=20, pady=20)
            return
        
        # Header row - Days
        ttk.Label(
            self.schedule_frame,
            text='Horaires',
            font=('Arial', 10, 'bold'),
            background='#2c3e50',
            foreground='white',
            anchor='center'
        ).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        
        for col_idx, day in enumerate(days, start=1):
            day_label = ttk.Label(
                self.schedule_frame,
                text=day['name'],
                font=('Arial', 10, 'bold'),
                background='#3498db',
                foreground='white',
                anchor='center'
            )
            day_label.grid(row=0, column=col_idx, sticky='nsew', padx=1, pady=1)
        
        # Grid rows - Time slots and cells
        for row_idx, slot in enumerate(time_slots, start=1):
            # Time slot header
            slot_text = f"{slot['start_time']}\n{slot['end_time']}"
            
            if slot['is_lunch']:
                bg_color = '#e74c3c'  # Red for lunch
                fg_color = 'white'
            else:
                bg_color = '#34495e'
                fg_color = 'white'
            
            time_label = ttk.Label(
                self.schedule_frame,
                text=slot_text,
                font=('Arial', 9),
                background=bg_color,
                foreground=fg_color,
                anchor='center'
            )
            time_label.grid(row=row_idx, column=0, sticky='nsew', padx=1, pady=1)
            
            # Schedule cells for each day
            for col_idx, day in enumerate(days, start=1):
                cell_key = (day['id'], slot['id'])
                
                # Create cell frame
                cell_frame = tk.Frame(
                    self.schedule_frame,
                    bg='white',
                    relief='solid',
                    borderwidth=1
                )
                cell_frame.grid(row=row_idx, column=col_idx, sticky='nsew', padx=1, pady=1)
                
                # Cell text widget
                cell_text = tk.Text(
                    cell_frame,
                    height=3,
                    width=15,
                    wrap='word',
                    font=('Arial', 9),
                    relief='flat',
                    bg='#ecf0f1' if slot['is_lunch'] else 'white'
                )
                cell_text.pack(fill='both', expand=True, padx=2, pady=2)
                
                # Make cells read-only by default (will enable editing on double-click)
                cell_text.config(state='disabled')
                
                # Bind click event for selection
                cell_text.bind('<Button-1>', lambda e, key=cell_key: self.select_cell(key))
                cell_text.bind('<Double-Button-1>', lambda e, key=cell_key: self.edit_cell_inline(key))
                
                # Store cell reference
                self.cell_frames[cell_key] = cell_text
        
        # Configure grid weights for proper resizing
        for col in range(len(days) + 1):
            self.schedule_frame.grid_columnconfigure(col, weight=1, minsize=120)
        
        for row in range(len(time_slots) + 1):
            self.schedule_frame.grid_rowconfigure(row, weight=1, minsize=60)
    
    def get_days(self):
        """Get days from database"""
        try:
            query = "SELECT * FROM days ORDER BY display_order"
            results = self.db.execute_query(query)
            return [dict(row) for row in results]
        except Exception as e:
            logging.error(f"Error loading days: {e}")
            return []
    
    def get_time_slots(self):
        """Get time slots from database"""
        try:
            query = "SELECT * FROM time_slots ORDER BY display_order"
            results = self.db.execute_query(query)
            return [dict(row) for row in results]
        except Exception as e:
            logging.error(f"Error loading time slots: {e}")
            return []
    
    def load_schedule_data(self):
        """Load schedule data from database for current week"""
        try:
            query = """
                SELECT day_id, slot_id, content, class_id
                FROM schedule_data
                WHERE week_number = ?
            """
            results = self.db.execute_query(query, (self.current_week,))
            
            # Clear all cells first
            for cell_text in self.cell_frames.values():
                cell_text.config(state='normal')
                cell_text.delete('1.0', 'end')
                cell_text.config(state='disabled')
            
            # Populate cells with data
            for row in results:
                cell_key = (row['day_id'], row['slot_id'])
                if cell_key in self.cell_frames:
                    cell_text = self.cell_frames[cell_key]
                    cell_text.config(state='normal')
                    cell_text.insert('1.0', row['content'] or '')
                    cell_text.config(state='disabled')
            
            logging.info(f"Loaded schedule for week {self.current_week}")
        except Exception as e:
            logging.error(f"Error loading schedule data: {e}")
            messagebox.showerror(
                "Erreur",
                f"Impossible de charger l'emploi du temps:\n{str(e)}"
            )
    
    def save_schedule(self):
        """Save current schedule to database"""
        try:
            # Delete existing data for this week
            delete_query = "DELETE FROM schedule_data WHERE week_number = ?"
            self.db.execute_update(delete_query, (self.current_week,))
            
            # Insert current data
            insert_query = """
                INSERT INTO schedule_data (week_number, day_id, slot_id, content)
                VALUES (?, ?, ?, ?)
            """
            
            saved_count = 0
            for (day_id, slot_id), cell_text in self.cell_frames.items():
                content = cell_text.get('1.0', 'end-1c').strip()
                if content:  # Only save non-empty cells
                    self.db.execute_update(
                        insert_query,
                        (self.current_week, day_id, slot_id, content)
                    )
                    saved_count += 1
            
            messagebox.showinfo(
                "Succès",
                f"Emploi du temps sauvegardé!\n{saved_count} cellule(s) enregistrée(s) pour la semaine {self.current_week}"
            )
            logging.info(f"Schedule saved for week {self.current_week}: {saved_count} cells")
            
        except Exception as e:
            logging.error(f"Error saving schedule: {e}")
            messagebox.showerror(
                "Erreur",
                f"Impossible de sauvegarder l'emploi du temps:\n{str(e)}"
            )
    
    def select_cell(self, cell_key):
        """Select a cell for editing"""
        # Deselect previous cell
        if self.selected_cell and self.selected_cell in self.cell_frames:
            prev_cell = self.cell_frames[self.selected_cell]
            prev_cell.config(bg='white' if not self.is_lunch_slot(self.selected_cell[1]) else '#ecf0f1')
        
        # Select new cell
        self.selected_cell = cell_key
        current_cell = self.cell_frames[cell_key]
        current_cell.config(bg='#ffffcc')  # Highlight color
        
        logging.info(f"Cell selected: Day {cell_key[0]}, Slot {cell_key[1]}")
    
    def is_lunch_slot(self, slot_id):
        """Check if a slot is a lunch break"""
        try:
            query = "SELECT is_lunch FROM time_slots WHERE id = ?"
            result = self.db.execute_query(query, (slot_id,))
            return result[0]['is_lunch'] if result else False
        except Exception as e:
            logging.error(f"Error checking lunch slot: {e}")
            return False
    
    def edit_cell_inline(self, cell_key):
        """Enable inline editing for a cell"""
        self.select_cell(cell_key)
        cell_text = self.cell_frames[cell_key]
        cell_text.config(state='normal')
        cell_text.focus_set()
        
        # Bind save on focus out
        def save_on_leave(event):
            cell_text.config(state='disabled')
        
        cell_text.bind('<FocusOut>', save_on_leave)
    
    def edit_cell(self):
        """Open edit dialog for selected cell"""
        if not self.selected_cell:
            messagebox.showwarning(
                "Aucune sélection",
                "Veuillez d'abord sélectionner une cellule en cliquant dessus."
            )
            return
        
        # Get current content
        cell_text = self.cell_frames[self.selected_cell]
        current_content = cell_text.get('1.0', 'end-1c')
        
        # Create edit dialog
        dialog = tk.Toplevel(self)
        dialog.title('Modifier la cellule')
        dialog.geometry('400x300')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        ttk.Label(
            dialog,
            text='Contenu de la cellule:',
            font=('Arial', 10, 'bold')
        ).pack(pady=10)
        
        text_widget = scrolledtext.ScrolledText(
            dialog,
            height=10,
            width=40,
            font=('Arial', 10),
            wrap='word'
        )
        text_widget.pack(padx=10, pady=10, fill='both', expand=True)
        text_widget.insert('1.0', current_content)
        text_widget.focus_set()
        
        def save_and_close():
            new_content = text_widget.get('1.0', 'end-1c')
            cell_text.config(state='normal')
            cell_text.delete('1.0', 'end')
            cell_text.insert('1.0', new_content)
            cell_text.config(state='disabled')
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        save_btn = ThemeManager.create_button(
            btn_frame,
            text='✓ Enregistrer',
            command=save_and_close
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ThemeManager.create_button(
            btn_frame,
            text='✗ Annuler',
            command=dialog.destroy
        )
        cancel_btn.pack(side='left', padx=5)
    
    def clear_week(self):
        """Clear all cells for current week"""
        result = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir effacer toutes les données de la semaine {self.current_week}?"
        )
        
        if result:
            for cell_text in self.cell_frames.values():
                cell_text.config(state='normal')
                cell_text.delete('1.0', 'end')
                cell_text.config(state='disabled')
            
            logging.info(f"Week {self.current_week} cleared")
            messagebox.showinfo("Succès", "La semaine a été effacée.")
    
    def previous_week(self):
        """Navigate to previous week"""
        if self.current_week > 1:
            self.current_week -= 1
            self.week_label.config(text=f'{self.current_week}/{self.max_weeks}')
            self.load_schedule_data()
    
    def next_week(self):
        """Navigate to next week"""
        if self.current_week < self.max_weeks:
            self.current_week += 1
            self.week_label.config(text=f'{self.current_week}/{self.max_weeks}')
            self.load_schedule_data()
    
    def go_back(self):
        """Return to dashboard"""
        self.controller.show_frame('DashboardFrame')
