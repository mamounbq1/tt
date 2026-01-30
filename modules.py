from tkinter import ttk
import sqlite3
import tkinter as tk
from tkinter import Toplevel, messagebox
from config import DB_PATH  # Import the shared database path

def create_module_window():
    top = Toplevel()
    top.title("Ajouter un Module")
    
    label_module = tk.Label(top, text="Nom du module:", font=("Arial", 10))
    label_module.pack(padx=0, pady=5)
    
    module_entry = tk.Entry(top, width=40)
    module_entry.pack(padx=10, pady=5)
    
    label_desc = tk.Label(top, text="Description du module:", font=("Arial", 10))
    label_desc.pack(padx=0, pady=5)
    
    desc_entry = tk.Text(top, height=5, width=40)
    desc_entry.pack(padx=10, pady=5)
    
    def save_module():
        name = module_entry.get().strip()
        description = desc_entry.get("1.0", tk.END).strip()
        
        if not name:
            messagebox.showerror("Erreur", "Le nom du module est requis")
            return
            
        add_module_to_db(name, description, top)
    
    save_btn = ttk.Button(top, text='Enregistrer', width=20, command=save_module)
    save_btn.pack(padx=10, pady=10)

def create_sequence_window(module_id):
    top = Toplevel()
    top.title("Ajouter une Séquence")
    
    label_seq = tk.Label(top, text="Titre de la séquence:", font=("Arial", 10))
    label_seq.pack(padx=0, pady=5)
    
    seq_entry = tk.Entry(top, width=40)
    seq_entry.pack(padx=10, pady=5)
    
    label_desc = tk.Label(top, text="Description:", font=("Arial", 10))
    label_desc.pack(padx=0, pady=5)
    
    desc_entry = tk.Text(top, height=5, width=40)
    desc_entry.pack(padx=10, pady=5)
    
    def save_sequence():
        title = seq_entry.get().strip()
        description = desc_entry.get("1.0", tk.END).strip()
        
        if not title:
            messagebox.showerror("Erreur", "Le titre de la séquence est requis")
            return
            
        add_sequence_to_db(module_id, title, description, top)
    
    save_btn = ttk.Button(top, text='Enregistrer', width=20, command=save_sequence)
    save_btn.pack(padx=10, pady=10)

def create_seance_window(sequence_id):
    top = Toplevel()
    top.title("Ajouter une Séance")
    
    label_title = tk.Label(top, text="Titre de la séance:", font=("Arial", 10))
    label_title.pack(padx=0, pady=5)
    
    title_entry = tk.Entry(top, width=40)
    title_entry.pack(padx=10, pady=5)
    
    label_content = tk.Label(top, text="Contenu de la séance:", font=("Arial", 10))
    label_content.pack(padx=0, pady=5)
    
    content_entry = tk.Text(top, height=10, width=40)
    content_entry.pack(padx=10, pady=5)
    
    def save_seance():
        title = title_entry.get().strip()
        content = content_entry.get("1.0", tk.END).strip()
        
        if not title or not content:
            messagebox.showerror("Erreur", "Tous les champs sont requis")
            return
            
        add_seance_to_db(sequence_id, title, content, top)
    
    save_btn = ttk.Button(top, text='Enregistrer', width=20, command=save_seance)
    save_btn.pack(padx=10, pady=10)

def add_module_to_db(name, description, window):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO modules (name, description)
            VALUES (?, ?)
        ''', (name, description))
        conn.commit()
        messagebox.showinfo("Succès", "Module ajouté avec succès!")
        window.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout du module : {str(e)}")
    finally:
        if conn:
            conn.close()

def add_sequence_to_db(module_id, title, description, window):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sequences (module_id, title, description)
            VALUES (?, ?, ?)
        ''', (module_id, title, description))
        conn.commit()
        messagebox.showinfo("Succès", "Séquence ajoutée avec succès!")
        window.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout de la séquence : {str(e)}")
    finally:
        if conn:
            conn.close()

def add_seance_to_db(sequence_id, title, content, window):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO seances (sequence_id, title, content)
            VALUES (?, ?, ?)
        ''', (sequence_id, title, content))
        conn.commit()
        messagebox.showinfo("Succès", "Séance ajoutée avec succès!")
        window.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout de la séance : {str(e)}")
    finally:
        if conn:
            conn.close()

def create_modules_tab(frame):
    # Clear any existing widgets in the frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Main paned window with two parts
    main_frame = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Left frame for modules
    left_frame = ttk.Frame(main_frame)
    main_frame.add(left_frame, weight=1)
    
    # Right frame for sequences and séances
    right_frame = ttk.Frame(main_frame)
    main_frame.add(right_frame, weight=2)
    
    # Treeview for modules
    modules_tree = ttk.Treeview(left_frame, columns=('ID', 'Name'), show='headings')
    modules_tree.heading('ID', text='ID')
    modules_tree.heading('Name', text='Nom du Module')
    modules_tree.column('ID', width=50)
    modules_tree.column('Name', width=150)
    modules_tree.pack(fill=tk.BOTH, expand=True)
    
    # Treeview for sequences and séances
    sequences_tree = ttk.Treeview(right_frame, columns=('ID', 'Title'), show='tree headings')
    sequences_tree.heading('ID', text='ID')
    sequences_tree.heading('Title', text='Titre')
    sequences_tree.column('ID', width=50)
    sequences_tree.column('Title', width=250)
    sequences_tree.pack(fill=tk.BOTH, expand=True)
    
    def on_module_select(event):
        selected = modules_tree.selection()
        if selected:
            module_id = modules_tree.item(selected[0])['values'][0]
            refresh_sequences(sequences_tree, module_id)
    
    def refresh_sequences(tree, module_id):
        # Remove existing items
        for item in tree.get_children():
            tree.delete(item)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Load sequences for the selected module
        cursor.execute("SELECT id, title FROM sequences WHERE module_id = ?", (module_id,))
        sequences = cursor.fetchall()
        
        for seq in sequences:
            seq_item = tree.insert('', 'end', text=seq[1], values=(seq[0], seq[1]))
            
            # Load séances for each sequence
            cursor.execute("SELECT id, title FROM seances WHERE sequence_id = ?", (seq[0],))
            seances = cursor.fetchall()
            for seance in seances:
                tree.insert(seq_item, 'end', text=seance[1], values=(seance[0], seance[1]))
        
        conn.close()
    
    def refresh_modules():
        modules_tree.delete(*modules_tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM modules")
        modules = cursor.fetchall()
        for module in modules:
            modules_tree.insert('', 'end', values=module)
        conn.close()
    
    # Frame for module buttons
    module_buttons_frame = ttk.Frame(left_frame)
    module_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    add_module_btn = ttk.Button(module_buttons_frame, text='Ajouter Module', 
                                command=create_module_window)
    add_module_btn.pack(side=tk.LEFT, padx=5)
    
    refresh_btn = ttk.Button(module_buttons_frame, text='Actualiser', 
                             command=refresh_modules)
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    # Frame for sequence/séance buttons
    seq_buttons_frame = ttk.Frame(right_frame)
    seq_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def add_sequence():
        selected = modules_tree.selection()
        if selected:
            module_id = modules_tree.item(selected[0])['values'][0]
            create_sequence_window(module_id)
    
    def add_seance():
        selected = sequences_tree.selection()
        if selected:
            item = sequences_tree.item(selected[0])
            if 'values' in item and item['values']:
                sequence_id = item['values'][0]
                create_seance_window(sequence_id)
    
    add_seq_btn = ttk.Button(seq_buttons_frame, text='Ajouter Séquence', 
                             command=add_sequence)
    add_seq_btn.pack(side=tk.LEFT, padx=5)
    
    add_seance_btn = ttk.Button(seq_buttons_frame, text='Ajouter Séance', 
                                command=add_seance)
    add_seance_btn.pack(side=tk.LEFT, padx=5)
    
    modules_tree.bind('<<TreeviewSelect>>', on_module_select)
    
    # Load initial data
    refresh_modules()
