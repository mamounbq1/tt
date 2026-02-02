"""
Add Entry Frame - Form to add homework and course entries
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging
from src.utils.theme import ThemeManager


class AddEntryFrame(ttk.Frame):
    """Frame for adding new homework/course entries"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.database = controller.database
        self.build_ui()
    
    def build_ui(self):
        """Build the add entry interface"""
        # Main container
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill='both')
        
        # Header with back button
        header = ttk.Frame(container)
        header.pack(fill='x', pady=(0, 20))
        
        back_btn = ThemeManager.create_button(
            header,
            text='← Retour',
            command=self.go_back
        )
        back_btn.pack(side='left')
        
        title = ThemeManager.create_label(
            container,
            text='Ajouter une Entrée',
            style='Heading.TLabel'
        )
        title.pack(pady=(0, 20))
        
        # Form frame
        form = ttk.Frame(container)
        form.pack(fill='both', expand=True)
        form.columnconfigure(1, weight=1)
        
        # Form fields
        self.fields = {}
        field_definitions = [
            ('Date (JJ/MM/AAAA)', 'date', 'entry', 'DD/MM/YYYY'),
            ('Classe', 'class', 'entry', 'Ex: 6ème A'),
            ('Matière', 'subject', 'entry', 'Ex: Mathématiques'),
            ('Contenu du cours', 'content', 'text', 'Description du cours...'),
            ('Devoirs', 'homework', 'text', 'Exercices à faire...'),
            ('Examen', 'exam', 'text', 'Date et type d\'examen...')
        ]
        
        for idx, (label_text, field_name, field_type, placeholder) in enumerate(field_definitions):
            # Label
            label = ThemeManager.create_label(form, text=label_text)
            label.grid(row=idx, column=0, sticky='ne', padx=10, pady=10)
            
            # Input widget
            if field_type == 'entry':
                widget = ThemeManager.create_entry(form, width=40)
                widget.insert(0, placeholder)
                widget.bind('<FocusIn>', lambda e, w=widget, p=placeholder: self.clear_placeholder(w, p))
                widget.bind('<FocusOut>', lambda e, w=widget, p=placeholder: self.restore_placeholder(w, p))
                widget.config(foreground='gray')
            else:  # text widget
                widget = tk.Text(form, width=40, height=4, wrap='word', font=ThemeManager.FONTS['body'])
                widget.insert('1.0', placeholder)
                widget.bind('<FocusIn>', lambda e, w=widget, p=placeholder: self.clear_text_placeholder(w, p))
                widget.bind('<FocusOut>', lambda e, w=widget, p=placeholder: self.restore_text_placeholder(w, p))
                widget.config(foreground='gray')
            
            widget.grid(row=idx, column=1, sticky='ew', padx=10, pady=10)
            self.fields[field_name] = {'widget': widget, 'type': field_type, 'placeholder': placeholder}
        
        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=20)
        
        save_btn = ThemeManager.create_button(
            button_frame,
            text='💾 Enregistrer',
            command=self.save_entry,
            style='Primary.TButton'
        )
        save_btn.pack(side='left', padx=5)
        
        clear_btn = ThemeManager.create_button(
            button_frame,
            text='🗑️ Effacer',
            command=self.clear_form
        )
        clear_btn.pack(side='left', padx=5)
    
    def clear_placeholder(self, widget, placeholder):
        """Clear placeholder text on focus"""
        if widget.get() == placeholder and widget.cget('foreground') == 'gray':
            widget.delete(0, 'end')
            widget.config(foreground='black')
    
    def restore_placeholder(self, widget, placeholder):
        """Restore placeholder if empty"""
        if not widget.get().strip():
            widget.insert(0, placeholder)
            widget.config(foreground='gray')
    
    def clear_text_placeholder(self, widget, placeholder):
        """Clear placeholder in Text widget"""
        content = widget.get('1.0', 'end-1c')
        if content == placeholder and widget.cget('foreground') == 'gray':
            widget.delete('1.0', 'end')
            widget.config(foreground='black')
    
    def restore_text_placeholder(self, widget, placeholder):
        """Restore placeholder in Text widget"""
        content = widget.get('1.0', 'end-1c').strip()
        if not content:
            widget.insert('1.0', placeholder)
            widget.config(foreground='gray')
    
    def get_field_value(self, field_name):
        """Get actual value from field (excluding placeholder)"""
        field_data = self.fields[field_name]
        widget = field_data['widget']
        field_type = field_data['type']
        
        if widget.cget('foreground') == 'gray':
            return ''
        
        if field_type == 'entry':
            return widget.get().strip()
        else:  # text widget
            return widget.get('1.0', 'end-1c').strip()
    
    def validate_form(self):
        """Validate form inputs"""
        # Validate date
        date_str = self.get_field_value('date')
        if not date_str:
            messagebox.showerror('Erreur', 'Veuillez saisir une date')
            return False
        
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            messagebox.showerror('Erreur', 'Format de date invalide! Utilisez JJ/MM/AAAA')
            return False
        
        # Validate required fields
        if not self.get_field_value('class'):
            messagebox.showerror('Erreur', 'Veuillez saisir une classe')
            return False
        
        if not self.get_field_value('subject'):
            messagebox.showerror('Erreur', 'Veuillez saisir une matière')
            return False
        
        if not self.get_field_value('content'):
            messagebox.showerror('Erreur', 'Veuillez saisir le contenu du cours')
            return False
        
        return True
    
    def save_entry(self):
        """Save the entry to database"""
        if not self.validate_form():
            return
        
        try:
            # Get and format values
            date_str = self.get_field_value('date')
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            iso_date = date_obj.strftime('%Y-%m-%d')
            
            class_name = self.get_field_value('class')
            subject = self.get_field_value('subject')
            content = self.get_field_value('content')
            homework = self.get_field_value('homework')
            exam = self.get_field_value('exam')
            
            # Insert into database
            query = """
                INSERT INTO homework_entries 
                (date, class_name, subject, content, homework, exam, teacher_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.database.execute_update(query, (iso_date, class_name, subject, content, homework, exam, 1))
            
            logging.info(f"Entry saved: {iso_date} - {class_name} - {subject}")
            
            messagebox.showinfo(
                'Succès',
                f'Entrée sauvegardée avec succès!\n\nDate: {date_str}\nClasse: {class_name}\nMatière: {subject}'
            )
            
            self.clear_form()
            
        except Exception as e:
            logging.error(f"Error saving entry: {e}", exc_info=True)
            messagebox.showerror('Erreur', f'Erreur lors de l\'enregistrement:\n{str(e)}')
    
    def clear_form(self):
        """Clear all form fields"""
        for field_name, field_data in self.fields.items():
            widget = field_data['widget']
            placeholder = field_data['placeholder']
            field_type = field_data['type']
            
            if field_type == 'entry':
                widget.delete(0, 'end')
                widget.insert(0, placeholder)
            else:  # text widget
                widget.delete('1.0', 'end')
                widget.insert('1.0', placeholder)
            
            widget.config(foreground='gray')
    
    def go_back(self):
        """Return to dashboard"""
        self.controller.show_frame('DashboardFrame')
