"""
Distribution Frame
Automatically distribute courses across the weekly schedule
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from src.utils.theme import ThemeManager
from src.utils.config import DB_PATH


class DistributionFrame(ttk.Frame):
    """Frame for automatically distributing courses"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.database
        
        self.selected_week = 1
        self.selected_class = None
        
        self.build_ui()
        self.load_classes()
    
    def build_ui(self):
        """Build the user interface"""
        # Main container
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill='both', expand=True)
        
        # Top bar
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
            text='🎲 Distribuer les Cours',
            style='Heading.TLabel'
        )
        title.pack(side='left', padx=20)
        
        # Instructions
        instructions = ttk.LabelFrame(main_container, text='Instructions', padding=10)
        instructions.pack(fill='x', pady=(0, 10))
        
        inst_text = """
Cette fonctionnalité permet de distribuer automatiquement les cours sur l'emploi du temps.

Fonctionnement:
1. Sélectionnez une classe
2. Choisissez une semaine
3. Configurez les paramètres de distribution
4. Cliquez sur "Distribuer" pour générer automatiquement l'emploi du temps
        """
        
        ttk.Label(
            instructions,
            text=inst_text.strip(),
            font=('Arial', 9),
            justify='left'
        )        .pack(anchor='w')
        
        # Configuration panel
        config_panel = ttk.LabelFrame(main_container, text='Configuration', padding=10)
        config_panel.pack(fill='x', pady=(0, 10))
        
        # Class selection
        class_frame = ttk.Frame(config_panel)
        class_frame.pack(fill='x', pady=5)
        
        ttk.Label(class_frame, text='Classe:', width=15).pack(side='left')
        
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(
            class_frame,
            textvariable=self.class_var,
            state='readonly',
            width=30
        )
        self.class_combo.pack(side='left', padx=5)
        
        # Week selection
        week_frame = ttk.Frame(config_panel)
        week_frame.pack(fill='x', pady=5)
        
        ttk.Label(week_frame, text='Semaine:', width=15).pack(side='left')
        
        self.week_var = tk.IntVar(value=1)
        week_spin = ttk.Spinbox(
            week_frame,
            from_=1,
            to=36,
            textvariable=self.week_var,
            width=10
        )
        week_spin.pack(side='left', padx=5)
        
        # Distribution mode
        mode_frame = ttk.Frame(config_panel)
        mode_frame.pack(fill='x', pady=5)
        
        ttk.Label(mode_frame, text='Mode:', width=15).pack(side='left')
        
        self.mode_var = tk.StringVar(value='auto')
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.mode_var,
            state='readonly',
            width=30
        )
        mode_combo['values'] = ('Auto - Distribution équilibrée', 'Manuel - Sélection interactive')
        mode_combo.current(0)
        mode_combo.pack(side='left', padx=5)
        
        # Subjects configuration
        subjects_frame = ttk.LabelFrame(main_container, text='Matières à Distribuer', padding=10)
        subjects_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Subject list with treeview
        columns = ('subject', 'hours_per_week')
        self.subjects_tree = ttk.Treeview(
            subjects_frame,
            columns=columns,
            show='headings',
            height=8
        )
        
        self.subjects_tree.heading('subject', text='Matière')
        self.subjects_tree.heading('hours_per_week', text='Heures/Semaine')
        
        self.subjects_tree.column('subject', width=300)
        self.subjects_tree.column('hours_per_week', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            subjects_frame,
            orient='vertical',
            command=self.subjects_tree.yview
        )
        self.subjects_tree.configure(yscrollcommand=scrollbar.set)
        
        self.subjects_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Add/remove subject buttons
        subject_btn_frame = ttk.Frame(subjects_frame)
        subject_btn_frame.pack(side='bottom', fill='x', pady=(5, 0))
        
        add_subject_btn = ThemeManager.create_button(
            subject_btn_frame,
            text='➕ Ajouter Matière',
            command=self.add_subject
        )
        add_subject_btn.pack(side='left', padx=5)
        
        remove_subject_btn = ThemeManager.create_button(
            subject_btn_frame,
            text='➖ Retirer',
            command=self.remove_subject
        )
        remove_subject_btn.pack(side='left', padx=5)
        
        # Load default subjects
        self.load_default_subjects()
        
        # Action buttons
        action_bar = ttk.Frame(main_container)
        action_bar.pack(fill='x', pady=(10, 0))
        
        distribute_btn = ThemeManager.create_button(
            action_bar,
            text='🎲 Distribuer',
            command=self.distribute_courses
        )
        distribute_btn.pack(side='left', padx=5)
        
        preview_btn = ThemeManager.create_button(
            action_bar,
            text='👁️ Aperçu',
            command=self.preview_distribution
        )
        preview_btn.pack(side='left', padx=5)
        
        clear_btn = ThemeManager.create_button(
            action_bar,
            text='🗑️ Effacer Semaine',
            command=self.clear_week
        )
        clear_btn.pack(side='left', padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            main_container,
            text='Prêt à distribuer',
            font=('Arial', 9, 'italic'),
            foreground='green'
        )
        self.status_label.pack(side='bottom', anchor='w', pady=5)
    
    def load_classes(self):
        """Load classes from database"""
        try:
            query = "SELECT name FROM classes ORDER BY name"
            results = self.db.execute_query(query)
            
            class_names = [row['name'] for row in results]
            
            if class_names:
                self.class_combo['values'] = class_names
                self.class_combo.current(0)
            else:
                # Add default classes if none exist
                default_classes = ['6ème A', '5ème B', '4ème C', '3ème D']
                self.class_combo['values'] = default_classes
                self.class_combo.current(0)
                
                self.status_label.config(
                    text='Aucune classe trouvée - Veuillez d\'abord ajouter des classes',
                    foreground='orange'
                )
            
            logging.info(f"Loaded {len(class_names)} classes for distribution")
            
        except Exception as e:
            logging.error(f"Error loading classes: {e}")
    
    def load_default_subjects(self):
        """Load default subject distribution"""
        default_subjects = [
            ('Mathématiques', 4),
            ('Français', 4),
            ('Histoire-Géographie', 3),
            ('Sciences (SVT/PC)', 3),
            ('Anglais', 3),
            ('Éducation Physique', 2),
            ('Arts Plastiques', 1),
            ('Musique', 1),
        ]
        
        for subject, hours in default_subjects:
            self.subjects_tree.insert('', 'end', values=(subject, hours))
    
    def add_subject(self):
        """Add a subject to distribution list"""
        dialog = tk.Toplevel(self)
        dialog.title('Ajouter Matière')
        dialog.geometry('350x200')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        ttk.Label(dialog, text='Nom de la matière:').pack(pady=5)
        subject_entry = ttk.Entry(dialog, width=30)
        subject_entry.pack(pady=5)
        
        ttk.Label(dialog, text='Heures par semaine:').pack(pady=5)
        hours_var = tk.IntVar(value=2)
        hours_spin = ttk.Spinbox(dialog, from_=1, to=10, textvariable=hours_var, width=10)
        hours_spin.pack(pady=5)
        
        def save():
            subject = subject_entry.get().strip()
            hours = hours_var.get()
            
            if not subject:
                messagebox.showwarning("Attention", "Veuillez entrer le nom de la matière")
                return
            
            self.subjects_tree.insert('', 'end', values=(subject, hours))
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        save_btn = ThemeManager.create_button(btn_frame, text='✓ Ajouter', command=save)
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ThemeManager.create_button(btn_frame, text='✗ Annuler', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
    
    def remove_subject(self):
        """Remove selected subject"""
        selection = self.subjects_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une matière à retirer")
            return
        
        for item in selection:
            self.subjects_tree.delete(item)
    
    def distribute_courses(self):
        """Distribute courses across the week"""
        # Get configuration
        selected_class = self.class_var.get()
        week = self.week_var.get()
        
        if not selected_class:
            messagebox.showwarning("Attention", "Veuillez sélectionner une classe")
            return
        
        # Get subjects
        subjects = []
        for item in self.subjects_tree.get_children():
            values = self.subjects_tree.item(item)['values']
            subjects.append({'name': values[0], 'hours': values[1]})
        
        if not subjects:
            messagebox.showwarning("Attention", "Veuillez ajouter au moins une matière")
            return
        
        # Confirm distribution
        total_hours = sum(s['hours'] for s in subjects)
        result = messagebox.askyesno(
            "Confirmation",
            f"Distribuer {total_hours} heures de cours pour {selected_class} sur la semaine {week}?\n\n"
            f"Attention: Cela écrasera l'emploi du temps existant pour cette semaine."
        )
        
        if not result:
            return
        
        try:
            # Get available slots (excluding lunch)
            days = self.db.execute_query("SELECT id FROM days ORDER BY display_order")
            slots = self.db.execute_query(
                "SELECT id FROM time_slots WHERE is_lunch = 0 ORDER BY display_order"
            )
            
            # Clear existing schedule for this week
            delete_query = "DELETE FROM schedule_data WHERE week_number = ?"
            self.db.execute_update(delete_query, (week,))
            
            # Distribute subjects across available slots
            slot_index = 0
            available_slots = [(d['id'], s['id']) for d in days for s in slots]
            
            for subject in subjects:
                hours_to_distribute = subject['hours']
                
                for _ in range(hours_to_distribute):
                    if slot_index >= len(available_slots):
                        messagebox.showwarning(
                            "Attention",
                            f"Pas assez de créneaux disponibles.\n"
                            f"Distribué {slot_index} créneaux sur {total_hours} demandés."
                        )
                        break
                    
                    day_id, slot_id = available_slots[slot_index]
                    content = f"{subject['name']}\n{selected_class}"
                    
                    insert_query = """
                        INSERT INTO schedule_data (week_number, day_id, slot_id, content)
                        VALUES (?, ?, ?, ?)
                    """
                    self.db.execute_update(insert_query, (week, day_id, slot_id, content))
                    
                    slot_index += 1
                
                if slot_index >= len(available_slots):
                    break
            
            self.status_label.config(
                text=f'Distribution terminée: {slot_index} créneaux attribués',
                foreground='green'
            )
            
            messagebox.showinfo(
                "Succès",
                f"Distribution terminée!\n\n"
                f"Classe: {selected_class}\n"
                f"Semaine: {week}\n"
                f"Créneaux attribués: {slot_index}/{total_hours}"
            )
            
            logging.info(f"Distributed {slot_index} slots for {selected_class} week {week}")
            
        except Exception as e:
            logging.error(f"Error distributing courses: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la distribution:\n{str(e)}")
            self.status_label.config(text='Erreur lors de la distribution', foreground='red')
    
    def preview_distribution(self):
        """Preview the distribution without saving"""
        selected_class = self.class_var.get()
        week = self.week_var.get()
        
        if not selected_class:
            messagebox.showwarning("Attention", "Veuillez sélectionner une classe")
            return
        
        # Get subjects
        subjects = []
        for item in self.subjects_tree.get_children():
            values = self.subjects_tree.item(item)['values']
            subjects.append({'name': values[0], 'hours': values[1]})
        
        if not subjects:
            messagebox.showwarning("Attention", "Veuillez ajouter au moins une matière")
            return
        
        # Build preview message
        total_hours = sum(s['hours'] for s in subjects)
        
        preview_text = f"Aperçu de la distribution:\n\n"
        preview_text += f"Classe: {selected_class}\n"
        preview_text += f"Semaine: {week}\n"
        preview_text += f"Total: {total_hours} heures\n\n"
        preview_text += "Matières:\n"
        
        for subject in subjects:
            preview_text += f"  • {subject['name']}: {subject['hours']}h/semaine\n"
        
        messagebox.showinfo("Aperçu de la Distribution", preview_text)
    
    def clear_week(self):
        """Clear schedule for selected week"""
        week = self.week_var.get()
        
        result = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir effacer l'emploi du temps de la semaine {week}?"
        )
        
        if not result:
            return
        
        try:
            delete_query = "DELETE FROM schedule_data WHERE week_number = ?"
            self.db.execute_update(delete_query, (week,))
            
            messagebox.showinfo("Succès", f"Semaine {week} effacée")
            self.status_label.config(text=f'Semaine {week} effacée', foreground='green')
            logging.info(f"Cleared week {week}")
            
        except Exception as e:
            logging.error(f"Error clearing week: {e}")
            messagebox.showerror("Erreur", f"Impossible d'effacer la semaine:\n{str(e)}")
    
    def go_back(self):
        """Return to dashboard"""
        self.controller.show_frame('DashboardFrame')
