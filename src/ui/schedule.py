import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import sqlite3
from pdf_generator import generate_pdf
from theme_manager import ThemeManager
from config import DB_PATH  # Import the shared database path

class EmploiDuTempsApp(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Use theme colors from the global theme manager
        self.colors = {
            'header_bg': ThemeManager.COLORS['primary'],
            'header_fg': 'white',
            'time_bg': ThemeManager.COLORS['secondary'],
            'time_fg': 'white',
            'cell_bg': ThemeManager.COLORS['surface'],
            'cell_fg': ThemeManager.COLORS['text_primary'],
            'empty_fg': ThemeManager.COLORS['text_secondary'],
            'hover_bg': ThemeManager.COLORS['primary_light'],
            'hover_empty_fg': ThemeManager.COLORS['secondary'],
            'placeholder_bg': ThemeManager.COLORS['background']
        }
        
        self.setup_ui()
        
        # Database setup: use DB_PATH from config.py
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        
        # Load initial schedule from the database
        self.reload_schedule()
    
    def setup_ui(self):
        # Top navigation frame
        nav_frame = ttk.Frame(self, padding="10")
        nav_frame.pack(fill='x', pady=(0, 10))
        
        # Back button on the left
        back_button = ttk.Button(
            nav_frame,
            text="Retour au tableau de bord",
            command=lambda: self.controller.show_frame("HomeFrame")
        )
        back_button.pack(side='left', padx=5)
        
        # Action buttons on the right
        action_frame = ttk.Frame(nav_frame)
        action_frame.pack(side='right')
        
        self.reload_button = ttk.Button(
            action_frame,
            text="Recharger",
            command=self.reload_schedule
        )
        self.reload_button.pack(side='left', padx=5)
        
        self.save_button = ttk.Button(
            action_frame,
            text="Sauvegarder",
            command=self.save_schedule
        )
        self.save_button.pack(side='left', padx=5)
        
        self.print_button = ttk.Button(
            action_frame,
            text="Imprimer PDF",
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
            label = ttk.Label(
                self.main_frame,
                text=text,
                style='Header.TLabel'
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

        # Create the cells (labels inside frames) for each time slot and day
        self.cells = {}
        current_row = 1

        # Create rows for morning slots
        for horaire in self.morning_slots:
            self._create_row(current_row, horaire)
            current_row += 1
        
        # Separator row (e.g., for lunch break)
        separator = ttk.Frame(
            self.main_frame,
            style='Separator.TFrame'
        )
        separator.grid(row=current_row, column=0, columnspan=len(self.columns) + 1, sticky='ew', pady=5)
        current_row += 1

        # Create rows for afternoon slots
        for horaire in self.afternoon_slots:
            self._create_row(current_row, horaire)
            current_row += 1

        # Configure grid weights so cells expand appropriately
        for i in range(current_row):
            self.main_frame.grid_rowconfigure(i, weight=1)
        for i in range(len(self.columns) + 1):
            self.main_frame.grid_columnconfigure(i, weight=1)
    
    def _create_row(self, row, horaire):
        # Create a label for the time slot (first column)
        time_label = ttk.Label(
            self.main_frame,
            text=horaire,
            style='Time.TLabel'
        )
        time_label.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
        
        # Create one cell for each day (columns 1 to N)
        for col in range(len(self.columns)):
            cell_frame = ttk.Frame(
                self.main_frame,
                style='Cell.TFrame'
            )
            cell_frame.grid(row=row, column=col + 1, sticky='nsew', padx=1, pady=1)
            
            # Ensure the cell's content expands properly
            cell_frame.grid_rowconfigure(0, weight=1)
            cell_frame.grid_columnconfigure(0, weight=1)

            cell = ttk.Label(
                cell_frame,
                text="",
                style='Empty.TLabel'
            )
            cell.grid(row=0, column=0, sticky='nsew')
            
            self._set_placeholder_text(cell)
            self.cells[(row, col)] = cell

            # Bind hover and click events to both the cell and its container
            for widget in (cell, cell_frame):
                widget.bind("<Enter>", lambda e, r=row, c=col: self.on_enter(r, c))
                widget.bind("<Leave>", lambda e, r=row, c=col: self.on_leave(r, c))
                widget.bind("<Button-1>", lambda e, r=row, c=col: self.on_click(r, c, e))
    
    def _set_placeholder_text(self, cell):
        cell.configure(text="- - - - - - - - - -", style='Empty.TLabel')

    def on_enter(self, row, col):
        cell = self.cells[(row, col)]
        cell.configure(style='CellHover.TLabel')

    def on_leave(self, row, col):
        cell = self.cells[(row, col)]
        if cell['text'] == "- - - - - - - - - -":
            cell.configure(style='Empty.TLabel')
        else:
            cell.configure(style='Cell.TLabel')

    def on_click(self, row, col, event):
        cell = self.cells[(row, col)]
        if cell['text'] != "- - - - - - - - - -":
            popup = tk.Menu(self.controller, tearoff=0)
            popup.add_command(label="Modifier", command=lambda: self._change_class(row, col))
            popup.add_separator()
            popup.add_command(label="Supprimer", command=lambda: self._delete_class(row, col))
            
            try:
                popup.tk_popup(event.x_root, event.y_root)
            finally:
                popup.grab_release()
        else:
            self._add_new_class(row, col)

    def _add_new_class(self, row, col):
        try:
            self.cursor.execute("SELECT name, level, school_year FROM classes")
            classes = self.cursor.fetchall()
            
            if not classes:
                messagebox.showwarning("Attention", "Aucune classe trouvée dans la base de données.")
                return

            selected_class = self._show_class_selection_dialog(classes)
            if selected_class:
                class_name, level, school_year = selected_class
                day_name = self.columns[col]
                if row <= 4:
                    time_slot = self.morning_slots[row - 1]
                else:
                    time_slot = self.afternoon_slots[row - 6]
                
                start_time, end_time = time_slot.split(" - ")
                
                self.cursor.execute("""
                    INSERT INTO schedule_entries (class_id, day_id, time_slot_id)
                    SELECT 
                        (SELECT id FROM classes WHERE name = ?),
                        (SELECT day_id FROM days WHERE name = ?),
                        (SELECT slot_id FROM time_slots WHERE start_time = ? AND end_time = ?)
                """, (class_name, day_name, start_time, end_time))
                
                self.conn.commit()
                
                cell = self.cells[(row, col)]
                cell.configure(
                    text=f"{class_name}\n{level} - {school_year}",
                    style='Cell.TLabel'
                )
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

    def _change_class(self, row, col):
        try:
            self.cursor.execute("SELECT name, level, school_year FROM classes")
            classes = self.cursor.fetchall()
            
            if not classes:
                messagebox.showwarning("Attention", "Aucune classe trouvée dans la base de données.")
                return

            selected_class = self._show_class_selection_dialog(classes)
            if selected_class:
                class_name, level, school_year = selected_class
                
                day_name = self.columns[col]
                if row <= 4:
                    time_slot = self.morning_slots[row - 1]
                else:
                    time_slot = self.afternoon_slots[row - 6]
                
                start_time, end_time = time_slot.split(" - ")
                
                self.cursor.execute("""
                    UPDATE schedule_entries 
                    SET class_id = (SELECT id FROM classes WHERE name = ?),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE day_id = (SELECT day_id FROM days WHERE name = ?)
                    AND time_slot_id = (SELECT slot_id FROM time_slots 
                                    WHERE start_time = ? AND end_time = ?)
                """, (class_name, day_name, start_time, end_time))
                
                self.conn.commit()
                
                cell = self.cells[(row, col)]
                cell.configure(
                    text=f"{class_name}\n{level} - {school_year}",
                    style='Cell.TLabel'
                )
                
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

    def _delete_class(self, row, col):
        if messagebox.askyesno("Confirmer la suppression", 
                             "Êtes-vous sûr de vouloir supprimer cette classe de l'emploi du temps ?"):
            try:
                day_name = self.columns[col]
                if row <= 4:
                    time_slot = self.morning_slots[row - 1]
                else:
                    time_slot = self.afternoon_slots[row - 6]
                
                start_time, end_time = time_slot.split(" - ")
                
                self.cursor.execute("""
                    DELETE FROM schedule_entries 
                    WHERE day_id = (SELECT day_id FROM days WHERE name = ?)
                    AND time_slot_id = (SELECT slot_id FROM time_slots 
                                    WHERE start_time = ? AND end_time = ?)
                """, (day_name, start_time, end_time))
                
                self.conn.commit()
                
                cell = self.cells[(row, col)]
                self._set_placeholder_text(cell)
                
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Erreur", f"Échec de la suppression : {str(e)}")

    def _show_class_selection_dialog(self, classes):
        dialog = tk.Toplevel(self.controller)
        dialog.title("Sélectionner une classe")
        dialog.configure(bg=ThemeManager.COLORS['background'])

        selected_class = None
        frame = ttk.Frame(dialog, style='Dialog.TFrame')
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        listbox = tk.Listbox(
            frame,
            width=40,
            font=ThemeManager.FONTS['body'],
            bg=ThemeManager.COLORS['surface'],
            fg=ThemeManager.COLORS['text_primary']
        )
        
        for class_name, level, school_year in classes:
            display_text = f"{class_name} ({level} - {school_year})"
            listbox.insert(tk.END, display_text)
        
        listbox.pack(padx=10, pady=10)

        def on_select():
            nonlocal selected_class
            if listbox.curselection():
                index = listbox.curselection()[0]
                selected_class = classes[index]
                dialog.destroy()

        select_button = ttk.Button(
            frame,
            text="Sélectionner",
            command=on_select
        )
        select_button.pack(pady=5)
        
        dialog.transient(self.controller)
        dialog.grab_set()
        dialog.wait_window()
        return selected_class

    def reload_schedule(self):
        try:
            for cell in self.cells.values():
                self._set_placeholder_text(cell)
            
            query = """
                SELECT ts.start_time, ts.end_time, c.name, c.level, c.school_year,
                       ts.is_lunch_break, d.name as day_name
                FROM schedule_entries se
                JOIN days d ON se.day_id = d.day_id
                JOIN time_slots ts ON se.time_slot_id = ts.slot_id
                JOIN classes c ON se.class_id = c.id
                ORDER BY ts.start_time
            """
            self.cursor.execute(query)
            entries = self.cursor.fetchall()

            for entry in entries:
                start_time, end_time, class_name, level, school_year, is_lunch_break, day_name = entry
                time_str = f"{start_time} - {end_time}"
                col = self.columns.index(day_name)
                
                if time_str in self.morning_slots:
                    row = self.morning_slots.index(time_str) + 1
                elif time_str in self.afternoon_slots:
                    row = self.afternoon_slots.index(time_str) + 6
                else:
                    continue

                cell = self.cells[(row, col)]
                if is_lunch_break:
                    display_text = "Pause Déjeuner"
                else:
                    display_text = f"{class_name}\n{level} - {school_year}"
                cell.configure(
                    text=display_text,
                    style='Cell.TLabel'
                )
            
            messagebox.showinfo("Succès", "Emploi du temps rechargé avec succès!")
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Échec du rechargement : {str(e)}")

    def save_schedule(self):
        try:
            for (row, col), cell in self.cells.items():
                cell_text = cell['text']
                if cell_text and cell_text != "- - - - - - - - - -" and cell_text != "Pause Déjeuner":
                    day_name = self.columns[col]

                    if row <= 4:
                        time_slot = self.morning_slots[row - 1]
                    else:
                        time_slot = self.afternoon_slots[row - 6]
                    
                    start_time, end_time = time_slot.split(" - ")
                    class_name = cell_text.split('\n')[0]
                    
                    self.cursor.execute("""
                        INSERT INTO schedule_entries (class_id, day_id, time_slot_id)
                        SELECT 
                            (SELECT id FROM classes WHERE name = ?),
                            (SELECT day_id FROM days WHERE name = ?),
                            (SELECT slot_id FROM time_slots WHERE start_time = ? AND end_time = ?)
                        ON CONFLICT(day_id, time_slot_id) DO UPDATE SET
                            class_id = (SELECT id FROM classes WHERE name = ?),
                            updated_at = CURRENT_TIMESTAMP
                    """, (class_name, day_name, start_time, end_time, class_name))
            
            self.conn.commit()
            messagebox.showinfo("Succès", "Emploi du temps sauvegardé avec succès!")
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erreur", f"Échec de la sauvegarde : {str(e)}")

    def print_to_pdf(self):
        try:
            data = []
            
            # Morning slots rows
            for i, horaire in enumerate(self.morning_slots):
                row = [horaire]
                for j in range(len(self.columns)):
                    cell = self.cells[(i + 1, j)]
                    row.append(cell['text'] if cell['text'] != "- - - - - - - - - -" else "")
                data.append(row)
            
            # Add lunch break row
            lunch_break = ["12:30 - 14:30"] + ["Pause Déjeuner"] * len(self.columns)
            data.append(lunch_break)
            
            # Afternoon slots rows
            for i, horaire in enumerate(self.afternoon_slots):
                row = [horaire]
                for j in range(len(self.columns)):
                    cell = self.cells[(i + 6, j)]
                    row.append(cell['text'] if cell['text'] != "- - - - - - - - - -" else "")
                data.append(row)

            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")]
            )
            
            if filename:
                generate_pdf(data, filename)
                messagebox.showinfo("Succès", "PDF généré avec succès!")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du PDF : {str(e)}")
