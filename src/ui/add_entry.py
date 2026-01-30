import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import create_connection

class AddEntryWindow:
    def __init__(self, root, enseignant):
        self.root = root
        self.enseignant = enseignant
        
        self.window = tk.Toplevel(root)
        self.window.title("Nouvelle Entrée")
        
        self.create_form()
    
    def create_form(self):
        fields = [
            ("Date (JJ/MM/AAAA)", "date_entry"),
            ("Classe", "classe_entry"),
            ("Matière", "matiere_entry"),
            ("Contenu du cours", "contenu_entry"),
            ("Devoirs", "devoirs_entry"),
            ("Examen", "examen_entry")
        ]
        
        self.entries = {}
        
        for i, (label, name) in enumerate(fields):
            ttk.Label(self.window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(self.window, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[name] = entry
        
        ttk.Button(self.window, text="Enregistrer", command=self.save_entry).grid(row=len(fields), column=1, pady=10)
    
    def save_entry(self):
        try:
            date = datetime.strptime(self.entries['date_entry'].get(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide!")
            return
        
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO entries (
                date, classe, matiere, contenu, devoirs, examen, enseignant_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            date,
            self.entries['classe_entry'].get(),
            self.entries['matiere_entry'].get(),
            self.entries['contenu_entry'].get(),
            self.entries['devoirs_entry'].get(),
            self.entries['examen_entry'].get(),
            self.enseignant[0]
        ))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Succès", "Entrée sauvegardée!")
        self.window.destroy()