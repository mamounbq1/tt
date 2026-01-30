from tkinter import ttk
import sqlite3
import tkinter as tk
from tkinter import Toplevel, messagebox
from tkcalendar import Calendar
from config import DB_PATH  # Use the shared database path

def open_date_entry_window():
    top = Toplevel()
    top.title("Absences")
    
    # Label and Calendar to select a date
    label_cal = tk.Label(top, text="Sélectionner un jour d'absence!", font=("Arial", 10))
    label_cal.pack(padx=0, pady=0)
    
    calendar = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    calendar.pack(padx=10, pady=10)
    
    # Label and Text widget for the absence reason
    label_absence = tk.Label(top, text="Motif de l'absence!", font=("Arial", 10))
    label_absence.pack(padx=0, pady=0)
    
    label_absence_entry = tk.Text(top, height=10, width=40)
    label_absence_entry.pack(padx=10, pady=10)
    
    # Variable and label to display the selected date
    selected_date = None
    date_label = tk.Label(top, text="Aucune date sélectionnée")
    date_label.pack(padx=10, pady=10)
    
    def on_date_click(event):
        nonlocal selected_date
        selected_date = calendar.get_date()
        date_label.config(text=f"Date d'absence sélectionnée: {selected_date}")
    
    def on_add_absence():
        # Get the reason for absence
        content = label_absence_entry.get("1.0", tk.END).strip()
        if not content:
            messagebox.showerror("Erreur", "Veuillez saisir un motif pour l'absence")
            return
        if selected_date is None:
            messagebox.showerror("Erreur", "Veuillez sélectionner une date")
            return
        # Add the absence record to the database
        add_absence_to_db(selected_date, content, top)
    
    calendar.bind("<<CalendarSelected>>", on_date_click)
    
    add_absence_btn = ttk.Button(top, text='Ajouter Absence', width=20, command=on_add_absence)
    add_absence_btn.pack(padx=10, pady=10)

def add_absence_to_db(date, motif, window):
    try:
        # Connect to the same database file defined in config.py
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO absences (date, motif)
            VALUES (?, ?)
        ''', (date, motif))
        
        conn.commit()
        messagebox.showinfo("Succès", "L'absence a été ajoutée avec succès!")
        window.destroy()
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout de l'absence : {str(e)}")
    finally:
        if conn:
            conn.close()

def fetch_absences_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM absences")
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération des données : {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def create_absences_tab(frame):
    # Clear any existing widgets in the frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Create a frame for the action buttons (at the bottom)
    button_frame = ttk.Frame(frame)
    button_frame.pack(side='bottom', fill='x', padx=5, pady=5)
    
    # Create a frame for the list (with a scrollbar)
    list_frame = ttk.Frame(frame)
    list_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)
    
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side='right', fill='y')
    
    # Create a Treeview to display absence records
    tree = ttk.Treeview(list_frame, columns=('ID', 'Date', 'Motif'), 
                        show='headings', yscrollcommand=scrollbar.set)
    
    tree.heading('ID', text='ID')
    tree.heading('Date', text='Date')
    tree.heading('Motif', text='Motif')
    
    tree.column('ID', width=50)
    tree.column('Date', width=100)
    tree.column('Motif', width=200)
    
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=tree.yview)
    
    # Fetch absence records and insert them into the Treeview
    absences_data = fetch_absences_data()
    for row in absences_data:
        tree.insert('', 'end', values=(row[0], row[1], row[2]))
    
    def delete_selected_absence():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une absence à supprimer")
            return
        absence_id = tree.item(selected_item[0])['values'][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette absence ?"):
            delete_absence(absence_id)
            create_absences_tab(frame)  # Refresh the display
    
    def refresh_data():
        create_absences_tab(frame)
    
    # Create action buttons in the button frame
    add_absence_btn = ttk.Button(button_frame, text='Ajouter Absence', width=20, 
                                 command=open_date_entry_window)
    add_absence_btn.pack(side='left', padx=5, pady=5)
    
    del_absence_btn = ttk.Button(button_frame, text='Supprimer Absence', width=20, 
                                 command=delete_selected_absence)
    del_absence_btn.pack(side='left', padx=5, pady=5)
    
    refresh_btn = ttk.Button(button_frame, text='Actualiser', width=20, 
                             command=refresh_data)
    refresh_btn.pack(side='left', padx=5, pady=5)

def delete_absence(absence_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM absences WHERE id = ?", (absence_id,))
        conn.commit()
        messagebox.showinfo("Succès", "Absence supprimée avec succès!")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")
    finally:
        if conn:
            conn.close()
