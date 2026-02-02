"""
Constraints Management Frame
Manages holidays, vacations, absences, classes, and modules
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import datetime
from src.utils.theme import ThemeManager
from src.utils.config import DB_PATH


class ConstraintsFrame(ttk.Frame):
    """Frame for managing all constraints (holidays, vacations, absences, classes, modules)"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.database
        
        # Current selected tab
        self.current_tab = None
        
        self.build_ui()
        self.load_all_data()
    
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
            text='🚫 Gestion des Contraintes',
            style='Heading.TLabel'
        )
        title.pack(side='left', padx=20)
        
        # Notebook (tabs) for different constraint types
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.holidays_tab = self.create_holidays_tab()
        self.vacations_tab = self.create_vacations_tab()
        self.absences_tab = self.create_absences_tab()
        self.classes_tab = self.create_classes_tab()
        self.modules_tab = self.create_modules_tab()
        
        self.notebook.add(self.holidays_tab, text='📅 Jours Fériés')
        self.notebook.add(self.vacations_tab, text='🏖️ Vacances')
        self.notebook.add(self.absences_tab, text='👤 Absences Enseignants')
        self.notebook.add(self.classes_tab, text='🎓 Classes')
        self.notebook.add(self.modules_tab, text='📚 Modules')
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_holidays_tab(self):
        """Create holidays management tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Action buttons
        action_bar = ttk.Frame(tab)
        action_bar.pack(fill='x', pady=(0, 10))
        
        add_btn = ThemeManager.create_button(
            action_bar,
            text='➕ Ajouter Jour Férié',
            command=self.add_holiday
        )
        add_btn.pack(side='left', padx=5)
        
        delete_btn = ThemeManager.create_button(
            action_bar,
            text='🗑️ Supprimer Sélectionné',
            command=lambda: self.delete_selected('holidays')
        )
        delete_btn.pack(side='left', padx=5)
        
        # Treeview for holidays
        columns = ('date', 'label', 'type')
        self.holidays_tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        self.holidays_tree.heading('date', text='Date')
        self.holidays_tree.heading('label', text='Nom')
        self.holidays_tree.heading('type', text='Type')
        
        self.holidays_tree.column('date', width=150)
        self.holidays_tree.column('label', width=300)
        self.holidays_tree.column('type', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.holidays_tree.yview)
        self.holidays_tree.configure(yscrollcommand=scrollbar.set)
        
        self.holidays_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return tab
    
    def create_vacations_tab(self):
        """Create vacations management tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Action buttons
        action_bar = ttk.Frame(tab)
        action_bar.pack(fill='x', pady=(0, 10))
        
        add_btn = ThemeManager.create_button(
            action_bar,
            text='➕ Ajouter Vacances',
            command=self.add_vacation
        )
        add_btn.pack(side='left', padx=5)
        
        delete_btn = ThemeManager.create_button(
            action_bar,
            text='🗑️ Supprimer Sélectionné',
            command=lambda: self.delete_selected('vacations')
        )
        delete_btn.pack(side='left', padx=5)
        
        # Treeview for vacations
        columns = ('start_date', 'end_date', 'label')
        self.vacations_tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        self.vacations_tree.heading('start_date', text='Date Début')
        self.vacations_tree.heading('end_date', text='Date Fin')
        self.vacations_tree.heading('label', text='Nom')
        
        self.vacations_tree.column('start_date', width=150)
        self.vacations_tree.column('end_date', width=150)
        self.vacations_tree.column('label', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.vacations_tree.yview)
        self.vacations_tree.configure(yscrollcommand=scrollbar.set)
        
        self.vacations_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return tab
    
    def create_absences_tab(self):
        """Create teacher absences management tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Action buttons
        action_bar = ttk.Frame(tab)
        action_bar.pack(fill='x', pady=(0, 10))
        
        add_btn = ThemeManager.create_button(
            action_bar,
            text='➕ Ajouter Absence',
            command=self.add_absence
        )
        add_btn.pack(side='left', padx=5)
        
        delete_btn = ThemeManager.create_button(
            action_bar,
            text='🗑️ Supprimer Sélectionné',
            command=lambda: self.delete_selected('absences')
        )
        delete_btn.pack(side='left', padx=5)
        
        # Treeview for absences
        columns = ('date', 'teacher', 'reason')
        self.absences_tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        self.absences_tree.heading('date', text='Date')
        self.absences_tree.heading('teacher', text='Enseignant')
        self.absences_tree.heading('reason', text='Motif')
        
        self.absences_tree.column('date', width=150)
        self.absences_tree.column('teacher', width=200)
        self.absences_tree.column('reason', width=250)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.absences_tree.yview)
        self.absences_tree.configure(yscrollcommand=scrollbar.set)
        
        self.absences_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return tab
    
    def create_classes_tab(self):
        """Create classes management tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Action buttons
        action_bar = ttk.Frame(tab)
        action_bar.pack(fill='x', pady=(0, 10))
        
        add_btn = ThemeManager.create_button(
            action_bar,
            text='➕ Ajouter Classe',
            command=self.add_class
        )
        add_btn.pack(side='left', padx=5)
        
        delete_btn = ThemeManager.create_button(
            action_bar,
            text='🗑️ Supprimer Sélectionné',
            command=lambda: self.delete_selected('classes')
        )
        delete_btn.pack(side='left', padx=5)
        
        # Treeview for classes
        columns = ('name', 'level', 'school_year')
        self.classes_tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        self.classes_tree.heading('name', text='Nom')
        self.classes_tree.heading('level', text='Niveau')
        self.classes_tree.heading('school_year', text='Année Scolaire')
        
        self.classes_tree.column('name', width=200)
        self.classes_tree.column('level', width=150)
        self.classes_tree.column('school_year', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.classes_tree.yview)
        self.classes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.classes_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return tab
    
    def create_modules_tab(self):
        """Create modules management tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Action buttons
        action_bar = ttk.Frame(tab)
        action_bar.pack(fill='x', pady=(0, 10))
        
        add_btn = ThemeManager.create_button(
            action_bar,
            text='➕ Ajouter Module',
            command=self.add_module
        )
        add_btn.pack(side='left', padx=5)
        
        delete_btn = ThemeManager.create_button(
            action_bar,
            text='🗑️ Supprimer Sélectionné',
            command=lambda: self.delete_selected('modules')
        )
        delete_btn.pack(side='left', padx=5)
        
        # Treeview for modules
        columns = ('name', 'description')
        self.modules_tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        self.modules_tree.heading('name', text='Nom')
        self.modules_tree.heading('description', text='Description')
        
        self.modules_tree.column('name', width=200)
        self.modules_tree.column('description', width=400)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.modules_tree.yview)
        self.modules_tree.configure(yscrollcommand=scrollbar.set)
        
        self.modules_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return tab
    
    def load_all_data(self):
        """Load data for all tabs"""
        self.load_holidays()
        self.load_vacations()
        self.load_absences()
        self.load_classes()
        self.load_modules()
    
    def load_holidays(self):
        """Load holidays from database"""
        try:
            # Clear existing items
            for item in self.holidays_tree.get_children():
                self.holidays_tree.delete(item)
            
            # Load from database
            query = "SELECT * FROM holidays ORDER BY date"
            results = self.db.execute_query(query)
            
            for row in results:
                self.holidays_tree.insert('', 'end', values=(
                    row['date'],
                    row['label'],
                    row['holiday_type']
                ), tags=(row['id'],))
            
            logging.info(f"Loaded {len(results)} holidays")
        except Exception as e:
            logging.error(f"Error loading holidays: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les jours fériés:\n{str(e)}")
    
    def load_vacations(self):
        """Load vacations from database"""
        try:
            # Clear existing items
            for item in self.vacations_tree.get_children():
                self.vacations_tree.delete(item)
            
            # Load from database
            query = "SELECT * FROM vacations ORDER BY start_date"
            results = self.db.execute_query(query)
            
            for row in results:
                self.vacations_tree.insert('', 'end', values=(
                    row['start_date'],
                    row['end_date'],
                    row['label']
                ), tags=(row['id'],))
            
            logging.info(f"Loaded {len(results)} vacations")
        except Exception as e:
            logging.error(f"Error loading vacations: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les vacances:\n{str(e)}")
    
    def load_absences(self):
        """Load teacher absences from database"""
        try:
            # Clear existing items
            for item in self.absences_tree.get_children():
                self.absences_tree.delete(item)
            
            # Load from database with teacher names
            query = """
                SELECT a.id, a.date, a.reason, t.name as teacher_name
                FROM absences a
                LEFT JOIN teachers t ON a.teacher_id = t.id
                ORDER BY a.date DESC
            """
            results = self.db.execute_query(query)
            
            for row in results:
                teacher_name = row['teacher_name'] if row['teacher_name'] else 'N/A'
                self.absences_tree.insert('', 'end', values=(
                    row['date'],
                    teacher_name,
                    row['reason']
                ), tags=(row['id'],))
            
            logging.info(f"Loaded {len(results)} absences")
        except Exception as e:
            logging.error(f"Error loading absences: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les absences:\n{str(e)}")
    
    def load_classes(self):
        """Load classes from database"""
        try:
            # Clear existing items
            for item in self.classes_tree.get_children():
                self.classes_tree.delete(item)
            
            # Load from database
            query = "SELECT * FROM classes ORDER BY name"
            results = self.db.execute_query(query)
            
            for row in results:
                self.classes_tree.insert('', 'end', values=(
                    row['name'],
                    row['level'] if row['level'] else '',
                    row['school_year'] if row['school_year'] else ''
                ), tags=(row['id'],))
            
            logging.info(f"Loaded {len(results)} classes")
        except Exception as e:
            logging.error(f"Error loading classes: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les classes:\n{str(e)}")
    
    def load_modules(self):
        """Load modules from database"""
        try:
            # Clear existing items
            for item in self.modules_tree.get_children():
                self.modules_tree.delete(item)
            
            # Load from database
            query = "SELECT * FROM modules ORDER BY name"
            results = self.db.execute_query(query)
            
            for row in results:
                self.modules_tree.insert('', 'end', values=(
                    row['name'],
                    row['description'] if row['description'] else ''
                ), tags=(row['id'],))
            
            logging.info(f"Loaded {len(results)} modules")
        except Exception as e:
            logging.error(f"Error loading modules: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les modules:\n{str(e)}")
    
    def add_holiday(self):
        """Add a new holiday"""
        dialog = tk.Toplevel(self)
        dialog.title('Ajouter Jour Férié')
        dialog.geometry('400x250')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields
        ttk.Label(dialog, text='Date (JJ/MM/AAAA):').pack(pady=5)
        date_entry = ttk.Entry(dialog, width=30)
        date_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Nom:').pack(pady=5)
        label_entry = ttk.Entry(dialog, width=30)
        label_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Type:').pack(pady=5)
        type_var = tk.StringVar(value='public')
        type_combo = ttk.Combobox(dialog, textvariable=type_var, width=28)
        type_combo['values'] = ('public', 'religious', 'national', 'regional')
        type_combo.pack(pady=5)
        
        def save():
            date_str = date_entry.get().strip()
            label = label_entry.get().strip()
            holiday_type = type_var.get()
            
            if not date_str or not label:
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
                return
            
            # Validate date format
            try:
                date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erreur", "Format de date invalide. Utilisez JJ/MM/AAAA")
                return
            
            try:
                query = "INSERT INTO holidays (date, label, holiday_type) VALUES (?, ?, ?)"
                self.db.execute_update(query, (formatted_date, label, holiday_type))
                
                self.load_holidays()
                messagebox.showinfo("Succès", "Jour férié ajouté avec succès!")
                dialog.destroy()
            except Exception as e:
                logging.error(f"Error adding holiday: {e}")
                messagebox.showerror("Erreur", f"Impossible d'ajouter le jour férié:\n{str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        save_btn = ThemeManager.create_button(btn_frame, text='✓ Enregistrer', command=save)
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ThemeManager.create_button(btn_frame, text='✗ Annuler', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
    
    def add_vacation(self):
        """Add a new vacation period"""
        dialog = tk.Toplevel(self)
        dialog.title('Ajouter Vacances')
        dialog.geometry('400x300')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields
        ttk.Label(dialog, text='Date Début (JJ/MM/AAAA):').pack(pady=5)
        start_entry = ttk.Entry(dialog, width=30)
        start_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Date Fin (JJ/MM/AAAA):').pack(pady=5)
        end_entry = ttk.Entry(dialog, width=30)
        end_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Nom:').pack(pady=5)
        label_entry = ttk.Entry(dialog, width=30)
        label_entry.pack(pady=5)
        
        def save():
            start_str = start_entry.get().strip()
            end_str = end_entry.get().strip()
            label = label_entry.get().strip()
            
            if not start_str or not end_str or not label:
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
                return
            
            # Validate date formats
            try:
                start_obj = datetime.strptime(start_str, '%d/%m/%Y')
                end_obj = datetime.strptime(end_str, '%d/%m/%Y')
                formatted_start = start_obj.strftime('%Y-%m-%d')
                formatted_end = end_obj.strftime('%Y-%m-%d')
                
                if end_obj < start_obj:
                    messagebox.showerror("Erreur", "La date de fin doit être après la date de début")
                    return
            except ValueError:
                messagebox.showerror("Erreur", "Format de date invalide. Utilisez JJ/MM/AAAA")
                return
            
            try:
                query = "INSERT INTO vacations (start_date, end_date, label) VALUES (?, ?, ?)"
                self.db.execute_update(query, (formatted_start, formatted_end, label))
                
                self.load_vacations()
                messagebox.showinfo("Succès", "Vacances ajoutées avec succès!")
                dialog.destroy()
            except Exception as e:
                logging.error(f"Error adding vacation: {e}")
                messagebox.showerror("Erreur", f"Impossible d'ajouter les vacances:\n{str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        save_btn = ThemeManager.create_button(btn_frame, text='✓ Enregistrer', command=save)
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ThemeManager.create_button(btn_frame, text='✗ Annuler', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
    
    def add_absence(self):
        """Add a new teacher absence"""
        dialog = tk.Toplevel(self)
        dialog.title('Ajouter Absence')
        dialog.geometry('400x300')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields
        ttk.Label(dialog, text='Date (JJ/MM/AAAA):').pack(pady=5)
        date_entry = ttk.Entry(dialog, width=30)
        date_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Enseignant:').pack(pady=5)
        
        # Get teachers list
        teachers = self.db.execute_query("SELECT id, name FROM teachers ORDER BY name")
        teacher_names = [t['name'] for t in teachers]
        teacher_ids = {t['name']: t['id'] for t in teachers}
        
        teacher_var = tk.StringVar()
        teacher_combo = ttk.Combobox(dialog, textvariable=teacher_var, width=28)
        teacher_combo['values'] = teacher_names
        teacher_combo.pack(pady=5)
        
        ttk.Label(dialog, text='Motif:').pack(pady=5)
        reason_entry = ttk.Entry(dialog, width=30)
        reason_entry.pack(pady=5)
        
        def save():
            date_str = date_entry.get().strip()
            teacher_name = teacher_var.get()
            reason = reason_entry.get().strip()
            
            if not date_str or not teacher_name or not reason:
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
                return
            
            # Validate date format
            try:
                date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erreur", "Format de date invalide. Utilisez JJ/MM/AAAA")
                return
            
            teacher_id = teacher_ids.get(teacher_name)
            if not teacher_id:
                messagebox.showerror("Erreur", "Enseignant non trouvé")
                return
            
            try:
                query = "INSERT INTO absences (date, teacher_id, reason) VALUES (?, ?, ?)"
                self.db.execute_update(query, (formatted_date, teacher_id, reason))
                
                self.load_absences()
                messagebox.showinfo("Succès", "Absence ajoutée avec succès!")
                dialog.destroy()
            except Exception as e:
                logging.error(f"Error adding absence: {e}")
                messagebox.showerror("Erreur", f"Impossible d'ajouter l'absence:\n{str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        save_btn = ThemeManager.create_button(btn_frame, text='✓ Enregistrer', command=save)
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ThemeManager.create_button(btn_frame, text='✗ Annuler', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
    
    def add_class(self):
        """Add a new class"""
        dialog = tk.Toplevel(self)
        dialog.title('Ajouter Classe')
        dialog.geometry('400x300')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields
        ttk.Label(dialog, text='Nom de la classe:').pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Niveau:').pack(pady=5)
        level_var = tk.StringVar()
        level_combo = ttk.Combobox(dialog, textvariable=level_var, width=28)
        level_combo['values'] = ('6ème', '5ème', '4ème', '3ème', '2nde', '1ère', 'Terminale')
        level_combo.pack(pady=5)
        
        ttk.Label(dialog, text='Année Scolaire:').pack(pady=5)
        year_entry = ttk.Entry(dialog, width=30)
        year_entry.insert(0, '2025-2026')
        year_entry.pack(pady=5)
        
        def save():
            name = name_entry.get().strip()
            level = level_var.get()
            year = year_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Attention", "Veuillez entrer le nom de la classe")
                return
            
            try:
                query = "INSERT INTO classes (name, level, school_year) VALUES (?, ?, ?)"
                self.db.execute_update(query, (name, level, year))
                
                self.load_classes()
                messagebox.showinfo("Succès", "Classe ajoutée avec succès!")
                dialog.destroy()
            except Exception as e:
                logging.error(f"Error adding class: {e}")
                messagebox.showerror("Erreur", f"Impossible d'ajouter la classe:\n{str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        save_btn = ThemeManager.create_button(btn_frame, text='✓ Enregistrer', command=save)
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ThemeManager.create_button(btn_frame, text='✗ Annuler', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
    
    def add_module(self):
        """Add a new module"""
        dialog = tk.Toplevel(self)
        dialog.title('Ajouter Module')
        dialog.geometry('400x300')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields
        ttk.Label(dialog, text='Nom du module:').pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Description:').pack(pady=5)
        desc_text = tk.Text(dialog, height=5, width=30, wrap='word')
        desc_text.pack(pady=5)
        
        def save():
            name = name_entry.get().strip()
            description = desc_text.get('1.0', 'end-1c').strip()
            
            if not name:
                messagebox.showwarning("Attention", "Veuillez entrer le nom du module")
                return
            
            try:
                query = "INSERT INTO modules (name, description) VALUES (?, ?)"
                self.db.execute_update(query, (name, description))
                
                self.load_modules()
                messagebox.showinfo("Succès", "Module ajouté avec succès!")
                dialog.destroy()
            except Exception as e:
                logging.error(f"Error adding module: {e}")
                messagebox.showerror("Erreur", f"Impossible d'ajouter le module:\n{str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        save_btn = ThemeManager.create_button(btn_frame, text='✓ Enregistrer', command=save)
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ThemeManager.create_button(btn_frame, text='✗ Annuler', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
    
    def delete_selected(self, table_type):
        """Delete selected item from specified table"""
        # Map table type to tree and table name
        tree_map = {
            'holidays': (self.holidays_tree, 'holidays'),
            'vacations': (self.vacations_tree, 'vacations'),
            'absences': (self.absences_tree, 'absences'),
            'classes': (self.classes_tree, 'classes'),
            'modules': (self.modules_tree, 'modules')
        }
        
        if table_type not in tree_map:
            return
        
        tree, table_name = tree_map[table_type]
        
        # Get selected item
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à supprimer")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cet élément?"
        )
        
        if not result:
            return
        
        try:
            # Get item ID from tags
            item_id = tree.item(selection[0])['tags'][0]
            
            # Delete from database
            query = f"DELETE FROM {table_name} WHERE id = ?"
            self.db.execute_update(query, (item_id,))
            
            # Reload data
            if table_type == 'holidays':
                self.load_holidays()
            elif table_type == 'vacations':
                self.load_vacations()
            elif table_type == 'absences':
                self.load_absences()
            elif table_type == 'classes':
                self.load_classes()
            elif table_type == 'modules':
                self.load_modules()
            
            messagebox.showinfo("Succès", "Élément supprimé avec succès!")
            logging.info(f"Deleted item from {table_name}")
        except Exception as e:
            logging.error(f"Error deleting from {table_name}: {e}")
            messagebox.showerror("Erreur", f"Impossible de supprimer l'élément:\n{str(e)}")
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        current = self.notebook.index(self.notebook.select())
        tab_names = ['holidays', 'vacations', 'absences', 'classes', 'modules']
        if current < len(tab_names):
            self.current_tab = tab_names[current]
            logging.info(f"Switched to tab: {self.current_tab}")
    
    def go_back(self):
        """Return to dashboard"""
        self.controller.show_frame('DashboardFrame')
