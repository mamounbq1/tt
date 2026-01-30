from tkinter import ttk
import sqlite3
import tkinter as tk
from tkinter import Toplevel, messagebox
from tkcalendar import Calendar
from config import DB_PATH  # Import the shared database path

def open_date_entry_window():
    top = Toplevel()
    top.title("Vacances")
    
    # Add a calendar to select a single day or an interval.
    label_cal = tk.Label(top, text="Sélectionner un jour ou intervalle!", font=("Arial", 10))
    label_cal.pack(padx=0, pady=0)
    
    calendar = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    calendar.pack(padx=10, pady=10)
    
    # Label and Text widget for the vacation description.
    label_vac = tk.Label(top, text="Intitulé de la vacance!", font=("Arial", 10))
    label_vac.pack(padx=0, pady=0)
    
    label_vac_entry = tk.Text(top, height=10, width=40)
    label_vac_entry.pack(padx=10, pady=10)
    
    # Variables to store selected dates.
    first_selected_date = None
    second_selected_date = None
    
    status_label = tk.Label(top, text="Aucune date sélectionnée")
    status_label.pack(padx=10, pady=10)
    
    def on_date_click(event):
        nonlocal first_selected_date, second_selected_date
        selected_date = calendar.get_date()
        
        if first_selected_date is None:
            first_selected_date = selected_date
            status_label.config(text=f"Premier jour sélectionné: {first_selected_date}")
        elif second_selected_date is None:
            second_selected_date = selected_date
            # Ensure the interval is ordered correctly.
            if first_selected_date <= second_selected_date:
                status_label.config(text=f"Intervalle sélectionné: {first_selected_date} à {second_selected_date}")
            else:
                first_selected_date, second_selected_date = second_selected_date, first_selected_date
                status_label.config(text=f"Intervalle sélectionné: {first_selected_date} à {second_selected_date}")
        else:
            # Reset if both dates were already selected.
            first_selected_date = selected_date
            second_selected_date = None
            status_label.config(text=f"Premier jour sélectionné: {first_selected_date}")
    
    def on_add_vacation():
        content = label_vac_entry.get("1.0", tk.END).strip()
        if not content:
            messagebox.showerror("Erreur", "Veuillez saisir un intitulé pour les vacances")
            return
        if first_selected_date is None:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins une date")
            return
        # Add vacation to the database.
        add_vacation_to_db(first_selected_date, second_selected_date, content, top)
    
    calendar.bind("<<CalendarSelected>>", on_date_click)
    
    add_vac_btn = ttk.Button(top, text='Add Vacation', width=20, command=on_add_vacation)
    add_vac_btn.pack(padx=10, pady=10)

def add_vacation_to_db(first, second, label_text, window):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO vacances (start_date, end_date, label)
            VALUES (?, ?, ?)
        ''', (first, second, label_text))
        
        conn.commit()
        messagebox.showinfo("Succès", "Les vacances ont été ajoutées avec succès!")
        window.destroy()
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout des vacances : {str(e)}")
    finally:
        if conn:
            conn.close()

def fetch_vacances_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacances")
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération des données : {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def create_vacances_tab(frame):
    # Clear existing widgets from the frame.
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Create a frame for the buttons at the bottom.
    button_frame = ttk.Frame(frame)
    button_frame.pack(side='bottom', fill='x', padx=5, pady=5)
    
    # Create a frame for the list with a scrollbar.
    list_frame = ttk.Frame(frame)
    list_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)
    
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side='right', fill='y')
    
    # Create a Treeview to display vacation data.
    tree = ttk.Treeview(list_frame, columns=('ID', 'Début', 'Fin', 'Label'), 
                        show='headings', yscrollcommand=scrollbar.set)
    
    tree.heading('ID', text='ID')
    tree.heading('Début', text='Date de début')
    tree.heading('Fin', text='Date de fin')
    tree.heading('Label', text='Description')
    
    tree.column('ID', width=50)
    tree.column('Début', width=100)
    tree.column('Fin', width=100)
    tree.column('Label', width=200)
    
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=tree.yview)
    
    # Fetch and display the vacation data.
    vacances_data = fetch_vacances_data()
    for row in vacances_data:
        tree.insert('', 'end', values=(row[0], row[1], row[2], row[3]))
    
    def delete_selected_vacation():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une vacation à supprimer")
            return
        
        vacation_id = tree.item(selected_item[0])['values'][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette vacation ?"):
            delete_vacation(vacation_id)
            create_vacances_tab(frame)  # Refresh the display
    
    def refresh_data():
        create_vacances_tab(frame)
    
    # Create buttons for adding, deleting, and refreshing.
    add_vac_btn = ttk.Button(button_frame, text='Add Vacation', width=20, command=open_date_entry_window)
    add_vac_btn.pack(side='left', padx=5, pady=5)
    
    dell_vac_btn = ttk.Button(button_frame, text='Delete Vacation', width=20, command=delete_selected_vacation)
    dell_vac_btn.pack(side='left', padx=5, pady=5)
    
    act_vac_btn = ttk.Button(button_frame, text='Actualiser', width=20, command=refresh_data)
    act_vac_btn.pack(side='left', padx=5, pady=5)

def delete_vacation(vacation_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vacances WHERE id = ?", (vacation_id,))
        conn.commit()
        messagebox.showinfo("Succès", "Vacation supprimée avec succès!")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")
    finally:
        if conn:
            conn.close()
