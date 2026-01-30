from tkinter import ttk
import sqlite3
import tkinter as tk
from tkinter import Toplevel, messagebox
from config import DB_PATH  # Use the shared database path

def create_class_window():
    top = Toplevel()
    top.title("Ajouter une Classe")
    
    # Nom de la classe
    label_name = tk.Label(top, text="Nom de la classe:", font=("Arial", 10))
    label_name.pack(padx=0, pady=5)
    
    name_entry = tk.Entry(top, width=40)
    name_entry.pack(padx=10, pady=5)
    
    # Niveau
    label_level = tk.Label(top, text="Niveau:", font=("Arial", 10))
    label_level.pack(padx=0, pady=5)
    
    level_entry = tk.Entry(top, width=40)
    level_entry.pack(padx=10, pady=5)
    
    # Année scolaire
    label_year = tk.Label(top, text="Année scolaire:", font=("Arial", 10))
    label_year.pack(padx=0, pady=5)
    
    year_entry = tk.Entry(top, width=40)
    year_entry.pack(padx=10, pady=5)
    
    def save_class():
        name = name_entry.get().strip()
        level = level_entry.get().strip()
        year = year_entry.get().strip()
        
        if not all([name, level, year]):
            messagebox.showerror("Erreur", "Tous les champs sont requis")
            return
            
        add_class_to_db(name, level, year, top)
    
    save_btn = ttk.Button(top, text='Enregistrer', width=20, command=save_class)
    save_btn.pack(padx=10, pady=10)

def add_class_to_db(name, level, year, window):
    try:
        # Use the shared DB_PATH so the same database is accessed everywhere.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO classes (name, level, school_year)
            VALUES (?, ?, ?)
        ''', (name, level, year))
        
        conn.commit()
        messagebox.showinfo("Succès", "Classe ajoutée avec succès!")
        window.destroy()
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout de la classe : {str(e)}")
    finally:
        if conn:
            conn.close()

def delete_class(class_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        conn.commit()
        messagebox.showinfo("Succès", "Classe supprimée avec succès!")
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")
    finally:
        if conn:
            conn.close()

def create_classes_tab(frame):
    # Clear existing widgets from the frame.
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Create a main frame inside the tab.
    main_frame = ttk.Frame(frame)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create a Treeview widget to display classes.
    classes_tree = ttk.Treeview(main_frame, 
                                columns=('ID', 'Name', 'Level', 'Year'), 
                                show='headings')
    classes_tree.heading('ID', text='ID')
    classes_tree.heading('Name', text='Nom')
    classes_tree.heading('Level', text='Niveau')
    classes_tree.heading('Year', text='Année')
    
    classes_tree.column('ID', width=50)
    classes_tree.column('Name', width=150)
    classes_tree.column('Level', width=100)
    classes_tree.column('Year', width=100)
    
    classes_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_classes():
        # Clear the Treeview.
        for item in classes_tree.get_children():
            classes_tree.delete(item)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, level, school_year 
            FROM classes 
            ORDER BY school_year DESC, level, name
        """)
        
        for class_data in cursor.fetchall():
            classes_tree.insert('', 'end', values=class_data)
        conn.close()
    
    # Frame for the action buttons.
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, padx=5, pady=5)
    
    add_class_btn = ttk.Button(button_frame, text='Ajouter Classe', 
                               command=create_class_window)
    add_class_btn.pack(side=tk.LEFT, padx=5)
    
    def delete_selected_class():
        selected = classes_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une classe")
            return
            
        class_id = classes_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette classe ?"):
            delete_class(class_id)
            refresh_classes()
    
    del_class_btn = ttk.Button(button_frame, text='Supprimer Classe',
                               command=delete_selected_class)
    del_class_btn.pack(side=tk.LEFT, padx=5)
    
    refresh_btn = ttk.Button(button_frame, text='Actualiser',
                             command=refresh_classes)
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    # Load the initial data.
    refresh_classes()
