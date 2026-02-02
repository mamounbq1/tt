"""
Schedule/Timetable Management Frame - FIXED SCHEDULE
Manages schedule_entries table (which class at which time slot)
Based on EmploiDuTempsApp from old app
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import logging
from src.utils.theme import ThemeManager
from src.utils.config import DB_PATH


class ScheduleFrame(ttk.Frame):
    """Frame for managing the FIXED weekly schedule (schedule_entries)"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Use theme colors
        self.colors = {
            'header_bg': '#2c3e50',
            'header_fg': 'white',
            'time_bg': '#34495e',
            'time_fg': 'white',
            'cell_bg': 'white',
            'cell_fg': '#2c3e50',
            'empty_fg': '#95a5a6',
            'hover_bg': '#3498db',
        }
        
        self.setup_ui()
        
        # Database connection
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.cursor = self.conn.cursor()
            self.cursor.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            messagebox.showerror("Erreur Base de Données", f"Une erreur est survenue : {e}")
        
        # Load initial schedule
        self.reload_schedule()
    
    def setup_ui(self):
        """Build the user interface"""
        # Top navigation frame
        nav_frame = ttk.Frame(self, padding="10")
        nav_frame.pack(fill='x', pady=(0, 10))
        
        # Back button on the left
        back_button = ttk.Button(
            nav_frame,
            text="← Retour au tableau de bord",
            command=lambda: self.controller.show_frame("DashboardFrame")
        )
        back_button.pack(side='left', padx=5)
        
        # Action buttons on the right
        action_frame = ttk.Frame(nav_frame)
        action_frame.pack(side='right')
        
        self.reload_button = ttk.Button(
            action_frame,
            text="🔄 Recharger",
            command=self.reload_schedule
        )
        self.reload_button.pack(side='left', padx=5)
        
        self.save_button = ttk.Button(
            action_frame,
            text="💾 Sauvegarder",
            command=self.save_schedule
        )
        self.save_button.pack(side='left', padx=5)
        
        self.print_button = ttk.Button(
            action_frame,
            text="🖨️ Imprimer PDF",
            command=self.print_to_pdf
        )
        self.print_button.pack(side='left', padx=5)

        # Main frame for the schedule grid
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill='both', expand=True)

        # Define the days of the week (columns)
        self.columns = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

        # Create header labels (first column is "Horaire")
        for col, text in enumerate(["Horaire"] + self.columns):
            label = tk.Label(
                self.main_frame,
                text=text,
                font=('Arial', 10, 'bold'),
                bg=self.colors['header_bg'],
                fg=self.colors['header_fg'],
                relief='solid',
                borderwidth=1
            )
            label.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)

        # Time slots configuration
        self.morning_slots = [
            "08:30 - 09:30", "09:30 - 10:30", 
            "10:30 - 11:30", "11:30 - 12:30"
        ]
        self.afternoon_slots = [
            "14:30 - 15:30", "15:30 - 16:30", 
            "16:30 - 17:30", "17:30 - 18:30"
        ]

        # Create the cells for each time slot and day
        self.cells = {}
        current_row = 1

        # Create rows for morning slots
        for horaire in self.morning_slots:
            self._create_row(current_row, horaire)
            current_row += 1
        
        # Separator row (for lunch break)
        separator = tk.Frame(
            self.main_frame,
            bg='#e74c3c',
            height=30
        )
        separator.grid(row=current_row, column=0, columnspan=len(self.columns) + 1, sticky='ew', pady=5)
        
        lunch_label = tk.Label(
            separator,
            text="🍽️ PAUSE DÉJEUNER (12:30 - 14:30)",
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white'
        )
        lunch_label.pack(expand=True)
        current_row += 1

        # Create rows for afternoon slots
        for horaire in self.afternoon_slots:
            self._create_row(current_row, horaire)
            current_row += 1

        # Configure grid weights so cells expand appropriately
        for i in range(current_row):
            self.main_frame.grid_rowconfigure(i, weight=1, minsize=60)
        for i in range(len(self.columns) + 1):
            self.main_frame.grid_columnconfigure(i, weight=1, minsize=120)
    
    def _create_row(self, row, horaire):
        """Create a row with time label and cells"""
        # Create a label for the time slot (first column)
        time_label = tk.Label(
            self.main_frame,
            text=horaire,
            font=('Arial', 9),
            bg=self.colors['time_bg'],
            fg=self.colors['time_fg'],
            relief='solid',
            borderwidth=1
        )
        time_label.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
        
        # Create one cell for each day (columns 1 to N)
        for col in range(len(self.columns)):
            cell_frame = tk.Frame(
                self.main_frame,
                bg=self.colors['cell_bg'],
                relief='solid',
                borderwidth=1
            )
            cell_frame.grid(row=row, column=col + 1, sticky='nsew', padx=1, pady=1)
            
            cell = tk.Label(
                cell_frame,
                text="",
                font=('Arial', 9),
                bg=self.colors['cell_bg'],
                fg=self.colors['empty_fg'],
                wraplength=150,
                justify='center'
            )
            cell.pack(fill='both', expand=True, padx=5, pady=5)
            
            self._set_placeholder_text(cell)
            self.cells[(row, col)] = cell

            # Bind hover and click events
            for widget in (cell, cell_frame):
                widget.bind("<Enter>", lambda e, r=row, c=col: self.on_enter(r, c))
                widget.bind("<Leave>", lambda e, r=row, c=col: self.on_leave(r, c))
                widget.bind("<Button-1>", lambda e, r=row, c=col: self.on_click(r, c, e))
    
    def _set_placeholder_text(self, cell):
        """Set placeholder text for empty cell"""
        cell.configure(text="- - - - - - - - - -", fg=self.colors['empty_fg'])

    def on_enter(self, row, col):
        """Handle mouse enter event"""
        cell = self.cells[(row, col)]
        cell.configure(bg=self.colors['hover_bg'], fg='white')

    def on_leave(self, row, col):
        """Handle mouse leave event"""
        cell = self.cells[(row, col)]
        if cell['text'] == "- - - - - - - - - -":
            cell.configure(bg=self.colors['cell_bg'], fg=self.colors['empty_fg'])
        else:
            cell.configure(bg=self.colors['cell_bg'], fg=self.colors['cell_fg'])

    def on_click(self, row, col, event):
        """Handle cell click event"""
        cell = self.cells[(row, col)]
        if cell['text'] != "- - - - - - - - - -":
            # Cell is not empty - show modify/delete menu
            popup = tk.Menu(self, tearoff=0)
            popup.add_command(label="✏️ Modifier", command=lambda: self._change_class(row, col))
            popup.add_separator()
            popup.add_command(label="🗑️ Supprimer", command=lambda: self._delete_class(row, col))
            
            try:
                popup.tk_popup(event.x_root, event.y_root)
            finally:
                popup.grab_release()
        else:
            # Cell is empty - add new class
            self._add_new_class(row, col)

    def _add_new_class(self, row, col):
        """Add a new class to the schedule"""
        try:
            self.cursor.execute("SELECT name, level, school_year FROM classes ORDER BY name")
            classes = self.cursor.fetchall()
            
            if not classes:
                messagebox.showwarning("Attention", "Aucune classe trouvée dans la base de données.\n\nVeuillez d'abord créer des classes dans la section Contraintes.")
                return

            selected_class = self._show_class_selection_dialog(classes)
            if selected_class:
                class_name, level, school_year = selected_class
                day_name = self.columns[col]
                
                # Determine time slot
                if row <= 4:
                    time_slot = self.morning_slots[row - 1]
                else:
                    time_slot = self.afternoon_slots[row - 6]
                
                start_time, end_time = time_slot.split(" - ")
                
                # Insert into schedule_entries
                self.cursor.execute("""
                    INSERT INTO schedule_entries (class_id, day_id, time_slot_id)
                    SELECT 
                        (SELECT id FROM classes WHERE name = ?),
                        (SELECT id FROM days WHERE name = ?),
                        (SELECT id FROM time_slots WHERE start_time = ? AND end_time = ?)
                """, (class_name, day_name, start_time, end_time))
                
                self.conn.commit()
                
                # Update cell display
                cell = self.cells[(row, col)]
                cell.configure(
                    text=f"{class_name}\n{level} - {school_year}",
                    fg=self.colors['cell_fg']
                )
                
                logging.info(f"Added class {class_name} to schedule at {day_name} {time_slot}")
                
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erreur", f"Impossible d'ajouter la classe :\n{str(e)}")
            logging.error(f"Error adding class: {e}")

    def _change_class(self, row, col):
        """Change the class assigned to a time slot"""
        try:
            self.cursor.execute("SELECT name, level, school_year FROM classes ORDER BY name")
            classes = self.cursor.fetchall()
            
            if not classes:
                messagebox.showwarning("Attention", "Aucune classe trouvée dans la base de données.")
                return

            selected_class = self._show_class_selection_dialog(classes)
            if selected_class:
                class_name, level, school_year = selected_class
                day_name = self.columns[col]
                
                # Determine time slot
                if row <= 4:
                    time_slot = self.morning_slots[row - 1]
                else:
                    time_slot = self.afternoon_slots[row - 6]
                
                start_time, end_time = time_slot.split(" - ")
                
                # Update schedule_entries
                self.cursor.execute("""
                    UPDATE schedule_entries 
                    SET class_id = (SELECT id FROM classes WHERE name = ?)
                    WHERE day_id = (SELECT id FROM days WHERE name = ?)
                    AND time_slot_id = (SELECT id FROM time_slots 
                                    WHERE start_time = ? AND end_time = ?)
                """, (class_name, day_name, start_time, end_time))
                
                self.conn.commit()
                
                # Update cell display
                cell = self.cells[(row, col)]
                cell.configure(
                    text=f"{class_name}\n{level} - {school_year}",
                    fg=self.colors['cell_fg']
                )
                
                logging.info(f"Changed class to {class_name} at {day_name} {time_slot}")
                
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erreur", f"Impossible de modifier la classe :\n{str(e)}")
            logging.error(f"Error changing class: {e}")

    def _delete_class(self, row, col):
        """Delete a class from the schedule"""
        if messagebox.askyesno("Confirmer la suppression", 
                             "Êtes-vous sûr de vouloir supprimer cette classe de l'emploi du temps ?"):
            try:
                day_name = self.columns[col]
                
                # Determine time slot
                if row <= 4:
                    time_slot = self.morning_slots[row - 1]
                else:
                    time_slot = self.afternoon_slots[row - 6]
                
                start_time, end_time = time_slot.split(" - ")
                
                # Delete from schedule_entries
                self.cursor.execute("""
                    DELETE FROM schedule_entries 
                    WHERE day_id = (SELECT id FROM days WHERE name = ?)
                    AND time_slot_id = (SELECT id FROM time_slots 
                                    WHERE start_time = ? AND end_time = ?)
                """, (day_name, start_time, end_time))
                
                self.conn.commit()
                
                # Reset cell to placeholder
                cell = self.cells[(row, col)]
                self._set_placeholder_text(cell)
                
                logging.info(f"Deleted class from {day_name} {time_slot}")
                messagebox.showinfo("Succès", "Classe supprimée avec succès!")
                
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Erreur", f"Échec de la suppression :\n{str(e)}")
                logging.error(f"Error deleting class: {e}")

    def _show_class_selection_dialog(self, classes):
        """Show dialog to select a class"""
        dialog = tk.Toplevel(self)
        dialog.title("Sélectionner une classe")
        dialog.geometry("400x400")
        dialog.transient(self)
        dialog.grab_set()

        selected_class = None
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(
            frame,
            text="Choisissez une classe :",
            font=('Arial', 10, 'bold')
        ).pack(pady=10)

        listbox = tk.Listbox(
            frame,
            width=50,
            height=15,
            font=('Arial', 10)
        )
        
        for class_name, level, school_year in classes:
            display_text = f"{class_name} ({level} - {school_year})"
            listbox.insert(tk.END, display_text)
        
        listbox.pack(padx=10, pady=10, fill='both', expand=True)

        def on_select():
            nonlocal selected_class
            if listbox.curselection():
                index = listbox.curselection()[0]
                selected_class = classes[index]
                dialog.destroy()

        def on_double_click(event):
            on_select()
        
        listbox.bind('<Double-Button-1>', on_double_click)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        select_button = ttk.Button(
            button_frame,
            text="✓ Sélectionner",
            command=on_select
        )
        select_button.pack(side='left', padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="✗ Annuler",
            command=dialog.destroy
        )
        cancel_button.pack(side='left', padx=5)
        
        dialog.wait_window()
        return selected_class

    def reload_schedule(self):
        """Reload schedule from database (schedule_entries)"""
        try:
            # Clear all cells first
            for cell in self.cells.values():
                self._set_placeholder_text(cell)
            
            # Load schedule_entries
            query = """
                SELECT ts.start_time, ts.end_time, c.name, c.level, c.school_year,
                       ts.is_lunch, d.name as day_name
                FROM schedule_entries se
                JOIN days d ON se.day_id = d.id
                JOIN time_slots ts ON se.time_slot_id = ts.id
                JOIN classes c ON se.class_id = c.id
                ORDER BY d.display_order, ts.display_order
            """
            self.cursor.execute(query)
            entries = self.cursor.fetchall()

            count = 0
            for entry in entries:
                start_time = entry['start_time']
                end_time = entry['end_time']
                class_name = entry['name']
                level = entry['level']
                school_year = entry['school_year']
                is_lunch = entry['is_lunch']
                day_name = entry['day_name']
                
                time_str = f"{start_time} - {end_time}"
                col = self.columns.index(day_name)
                
                # Determine row
                if time_str in self.morning_slots:
                    row = self.morning_slots.index(time_str) + 1
                elif time_str in self.afternoon_slots:
                    row = self.afternoon_slots.index(time_str) + 6
                else:
                    continue

                cell = self.cells[(row, col)]
                if is_lunch:
                    display_text = "Pause Déjeuner"
                else:
                    display_text = f"{class_name}\n{level} - {school_year}"
                
                cell.configure(
                    text=display_text,
                    fg=self.colors['cell_fg']
                )
                count += 1
            
            messagebox.showinfo("Succès", f"Emploi du temps rechargé avec succès!\n{count} entrée(s) chargée(s).")
            logging.info(f"Schedule reloaded: {count} entries")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Échec du rechargement :\n{str(e)}")
            logging.error(f"Error reloading schedule: {e}")

    def save_schedule(self):
        """Save current schedule to database"""
        try:
            saved_count = 0
            
            for (row, col), cell in self.cells.items():
                cell_text = cell['text']
                if cell_text and cell_text != "- - - - - - - - - -" and cell_text != "Pause Déjeuner":
                    day_name = self.columns[col]

                    # Determine time slot
                    if row <= 4:
                        time_slot = self.morning_slots[row - 1]
                    else:
                        time_slot = self.afternoon_slots[row - 6]
                    
                    start_time, end_time = time_slot.split(" - ")
                    class_name = cell_text.split('\n')[0]
                    
                    # Insert or update schedule_entries
                    self.cursor.execute("""
                        INSERT INTO schedule_entries (class_id, day_id, time_slot_id)
                        SELECT 
                            (SELECT id FROM classes WHERE name = ?),
                            (SELECT id FROM days WHERE name = ?),
                            (SELECT id FROM time_slots WHERE start_time = ? AND end_time = ?)
                        WHERE NOT EXISTS (
                            SELECT 1 FROM schedule_entries 
                            WHERE day_id = (SELECT id FROM days WHERE name = ?)
                            AND time_slot_id = (SELECT id FROM time_slots WHERE start_time = ? AND end_time = ?)
                        )
                    """, (class_name, day_name, start_time, end_time, day_name, start_time, end_time))
                    
                    if self.cursor.rowcount > 0:
                        saved_count += 1
            
            self.conn.commit()
            messagebox.showinfo("Succès", f"Emploi du temps sauvegardé avec succès!\n{saved_count} nouvelle(s) entrée(s).")
            logging.info(f"Schedule saved: {saved_count} entries")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erreur", f"Échec de la sauvegarde :\n{str(e)}")
            logging.error(f"Error saving schedule: {e}")

    def print_to_pdf(self):
        """Export schedule to PDF"""
        try:
            messagebox.showinfo("Info", "Fonctionnalité PDF à implémenter.\n\nPour l'instant, utilisez Imprimer depuis le menu Fichier de votre navigateur après avoir affiché l'emploi du temps.")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du PDF :\n{str(e)}")
            logging.error(f"Error generating PDF: {e}")
    
    def go_back(self):
        """Return to dashboard"""
        self.controller.show_frame('DashboardFrame')
