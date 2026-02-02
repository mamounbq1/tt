"""
Distribution Frame
Automatically distribute courses across the weekly schedule based on fixed schedule entries
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import datetime
from src.utils.theme import ThemeManager
from src.utils.config import DB_PATH
from src.core.course_distribution import CourseDistributionManager


class DistributionFrame(ttk.Frame):
    """Frame for automatically distributing courses"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.database
        self.dist_manager = CourseDistributionManager(DB_PATH)
        
        self.selected_week = 1
        self.current_year = self.get_current_school_year()
        
        self.build_ui()
        self.refresh_status()
    
    def get_current_school_year(self):
        """Get current school year (e.g., '2024-2025')"""
        now = datetime.now()
        if now.month >= 9:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
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
        instructions = ttk.LabelFrame(main_container, text='📖 Comment ça marche', padding=10)
        instructions.pack(fill='x', pady=(0, 10))
        
        inst_text = """Distribution automatique des cours basée sur l'emploi du temps fixe:

1. Le système utilise "ma_table" (contenu des cours) et "schedule_entries" (emploi du temps fixe)
2. Pour chaque semaine, il assigne séquentiellement les cours aux créneaux planifiés
3. Il respecte automatiquement les contraintes: vacances, jours fériés, absences enseignants
4. Il saute la pause déjeuner (12:30-14:30)
5. Chaque classe progresse dans le programme de manière séquentielle

Prérequis:
• Avoir créé l'emploi du temps fixe (schedule_entries)
• Avoir chargé les cours dans ma_table
• Avoir défini les classes"""
        
        ttk.Label(
            instructions,
            text=inst_text.strip(),
            font=('Arial', 9),
            justify='left'
        ).pack(anchor='w')
        
        # Configuration panel
        config_panel = ttk.LabelFrame(main_container, text='⚙️ Configuration', padding=10)
        config_panel.pack(fill='x', pady=(0, 10))
        
        # School year
        year_frame = ttk.Frame(config_panel)
        year_frame.pack(fill='x', pady=5)
        
        ttk.Label(year_frame, text='Année scolaire:', width=20).pack(side='left')
        
        self.year_var = tk.StringVar(value=self.current_year)
        year_entry = ttk.Entry(year_frame, textvariable=self.year_var, width=15)
        year_entry.pack(side='left', padx=5)
        
        ttk.Label(year_frame, text='(Format: 2024-2025)', font=('Arial', 8, 'italic')).pack(side='left', padx=5)
        
        # Week selection
        week_frame = ttk.Frame(config_panel)
        week_frame.pack(fill='x', pady=5)
        
        ttk.Label(week_frame, text='Semaine:', width=20).pack(side='left')
        
        self.week_var = tk.IntVar(value=1)
        week_spin = ttk.Spinbox(
            week_frame,
            from_=1,
            to=36,
            textvariable=self.week_var,
            width=10
        )
        week_spin.pack(side='left', padx=5)
        
        ttk.Label(week_frame, text='(1-36)', font=('Arial', 8, 'italic')).pack(side='left')
        
        # Actions frame
        actions_frame = ttk.Frame(main_container)
        actions_frame.pack(fill='x', pady=(0, 10))
        
        ThemeManager.create_button(
            actions_frame,
            text='📚 Charger Cours Exemple',
            command=self.load_sample_courses
        ).pack(side='left', padx=5)
        
        ThemeManager.create_button(
            actions_frame,
            text='🔄 Rafraîchir Statut',
            command=self.refresh_status
        ).pack(side='left', padx=5)
        
        ThemeManager.create_button(
            actions_frame,
            text='🎲 DISTRIBUER',
            command=self.distribute_courses,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        
        ThemeManager.create_button(
            actions_frame,
            text='📊 Voir Résumé',
            command=self.show_summary
        ).pack(side='left', padx=5)
        
        # Status panel
        status_panel = ttk.LabelFrame(main_container, text='📈 Statut du Système', padding=10)
        status_panel.pack(fill='both', expand=True)
        
        self.status_text = scrolledtext.ScrolledText(
            status_panel,
            width=80,
            height=15,
            font=('Courier', 9),
            state='disabled'
        )
        self.status_text.pack(fill='both', expand=True)
    
    def refresh_status(self):
        """Refresh system status display"""
        try:
            conn = self.dist_manager.get_connection()
            cursor = conn.cursor()
            
            # Count courses in ma_table
            cursor.execute("SELECT COUNT(*) as count FROM ma_table")
            course_count = cursor.fetchone()['count']
            
            # Count schedule entries
            cursor.execute("SELECT COUNT(*) as count FROM schedule_entries")
            entry_count = cursor.fetchone()['count']
            
            # Count classes
            cursor.execute("SELECT COUNT(*) as count FROM classes")
            class_count = cursor.fetchone()['count']
            
            # Get unique weeks distributed
            cursor.execute("SELECT DISTINCT week_number FROM schedule_data ORDER BY week_number")
            distributed_weeks = [row['week_number'] for row in cursor.fetchall()]
            
            # Count holidays
            cursor.execute("SELECT COUNT(*) as count FROM holidays")
            holiday_count = cursor.fetchone()['count']
            
            # Count vacations
            cursor.execute("SELECT COUNT(*) as count FROM vacations")
            vacation_count = cursor.fetchone()['count']
            
            # Build status text
            status = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    STATUT DU SYSTÈME DE DISTRIBUTION                 ║
╚══════════════════════════════════════════════════════════════════════╝

📚 CONTENU DES COURS (ma_table)
   ├─ Nombre de cours disponibles: {course_count}
   └─ {'✅ Prêt' if course_count > 0 else '⚠️ Aucun cours - Utilisez "Charger Cours Exemple"'}

📅 EMPLOI DU TEMPS FIXE (schedule_entries)
   ├─ Nombre d'entrées: {entry_count}
   └─ {'✅ Prêt' if entry_count > 0 else '⚠️ Aucune entrée - Créez l\'emploi du temps d\'abord'}

🏫 CLASSES
   ├─ Nombre de classes: {class_count}
   └─ {'✅ Prêt' if class_count > 0 else '⚠️ Aucune classe - Ajoutez des classes d\'abord'}

🚫 CONTRAINTES
   ├─ Jours fériés: {holiday_count}
   └─ Périodes de vacances: {vacation_count}

📊 DISTRIBUTION EFFECTUÉE
   ├─ Semaines distribuées: {len(distributed_weeks)}
   └─ Numéros: {', '.join(map(str, distributed_weeks)) if distributed_weeks else 'Aucune'}

⚙️ CONFIGURATION ACTUELLE
   ├─ Année scolaire: {self.year_var.get()}
   └─ Semaine sélectionnée: {self.week_var.get()}

{'✅ SYSTÈME PRÊT - Vous pouvez distribuer!' if course_count > 0 and entry_count > 0 and class_count > 0 else '⚠️ SYSTÈME NON PRÊT - Vérifiez les prérequis ci-dessus'}
"""
            
            self.status_text.config(state='normal')
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, status)
            self.status_text.config(state='disabled')
            
        except Exception as e:
            logging.error(f"Error refreshing status: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du rafraîchissement: {e}")
    
    def load_sample_courses(self):
        """Load sample courses into ma_table"""
        if messagebox.askyesno(
            "Charger des cours exemple",
            "Cela va charger 30 cours d'exemple dans ma_table.\n\n"
            "Continuer?"
        ):
            try:
                success, message = self.dist_manager.load_sample_courses()
                if success:
                    messagebox.showinfo("Succès", message)
                    self.refresh_status()
                else:
                    messagebox.showwarning("Information", message)
            except Exception as e:
                logging.error(f"Error loading sample courses: {e}")
                messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def distribute_courses(self):
        """Execute course distribution for selected week"""
        week = self.week_var.get()
        school_year = self.year_var.get()
        
        # Validate year format
        if not self.validate_school_year(school_year):
            messagebox.showerror(
                "Erreur",
                "Format d'année scolaire invalide.\nUtilisez le format: 2024-2025"
            )
            return
        
        # Confirm action
        if not messagebox.askyesno(
            "Confirmer Distribution",
            f"Distribuer les cours pour la semaine {week} de l'année {school_year}?\n\n"
            f"⚠️ Cela remplacera toute distribution existante pour cette semaine."
        ):
            return
        
        try:
            # Execute distribution
            success, message, distribution_data = self.dist_manager.distribute_courses(
                week, school_year
            )
            
            if success:
                messagebox.showinfo("Succès", message)
                self.refresh_status()
            else:
                messagebox.showerror("Erreur", message)
                
        except Exception as e:
            logging.error(f"Error distributing courses: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la distribution:\n{e}")
    
    def show_summary(self):
        """Show distribution summary for selected week"""
        week = self.week_var.get()
        
        try:
            summary = self.dist_manager.get_distribution_summary(week)
            
            if not summary:
                messagebox.showinfo(
                    "Aucune donnée",
                    f"Aucune distribution trouvée pour la semaine {week}"
                )
                return
            
            # Create summary window
            summary_window = tk.Toplevel(self)
            summary_window.title(f"Résumé - Semaine {week}")
            summary_window.geometry("800x600")
            
            # Title
            title_label = ThemeManager.create_label(
                summary_window,
                text=f'📊 Résumé de la Distribution - Semaine {week}',
                style='Heading.TLabel'
            )
            title_label.pack(pady=10)
            
            # Treeview
            tree_frame = ttk.Frame(summary_window)
            tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            columns = ('day', 'time', 'class', 'content')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
            
            tree.heading('day', text='Jour')
            tree.heading('time', text='Horaire')
            tree.heading('class', text='Classe')
            tree.heading('content', text='Contenu')
            
            tree.column('day', width=100)
            tree.column('time', width=120)
            tree.column('class', width=120)
            tree.column('content', width=400)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Populate data
            for row in summary:
                tree.insert('', 'end', values=(
                    row['day_name'],
                    row['time_range'],
                    row['class_name'] or '-',
                    row['content'] or '-'
                ))
            
            # Close button
            ThemeManager.create_button(
                summary_window,
                text='Fermer',
                command=summary_window.destroy
            ).pack(pady=10)
            
        except Exception as e:
            logging.error(f"Error showing summary: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage du résumé:\n{e}")
    
    def validate_school_year(self, year_str):
        """Validate school year format (YYYY-YYYY)"""
        try:
            parts = year_str.split('-')
            if len(parts) != 2:
                return False
            year1 = int(parts[0])
            year2 = int(parts[1])
            return year2 == year1 + 1 and 2000 <= year1 <= 2100
        except:
            return False
    
    def go_back(self):
        """Return to dashboard"""
        self.controller.show_frame('DashboardFrame')
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'dist_manager'):
            self.dist_manager.close()
