from tkinter import ttk
import sqlite3
import tkinter as tk
from tkinter import Toplevel, messagebox
from tkcalendar import Calendar
from config import DB_PATH  # Import the shared database path

def open_date_entry_window():
    top = Toplevel()
    top.title("Jours Fériés")
    
    # Add a calendar to select a holiday date
    label_cal = tk.Label(top, text="Sélectionner un jour férié!", font=("Arial", 10))
    label_cal.pack(padx=0, pady=0)
    
    calendar = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    calendar.pack(padx=10, pady=10)
    
    # Entry for the holiday's name/description
    label_holiday = tk.Label(top, text="Nom du jour férié!", font=("Arial", 10))
    label_holiday.pack(padx=0, pady=0)
    
    label_holiday_entry = tk.Text(top, height=10, width=40)
    label_holiday_entry.pack(padx=10, pady=10)
    
    # Variable to store the selected date and a label to show it
    selected_date = None
    date_label = tk.Label(top, text="Aucune date sélectionnée")
    date_label.pack(padx=10, pady=10)
    
    def on_date_click(event):
        nonlocal selected_date
        selected_date = calendar.get_date()
        date_label.config(text=f"Jour férié sélectionné: {selected_date}")
    
    def on_add_holiday():
        # Retrieve the holiday description
        content = label_holiday_entry.get("1.0", tk.END).strip()
        if not content:
            messagebox.showerror("Erreur", "Veuillez saisir un nom pour le jour férié")
            return
        if selected_date is None:
            messagebox.showerror("Erreur", "Veuillez sélectionner une date")
            return
        # Call the function to add the holiday to the database
        add_holiday_to_db(selected_date, content, top)

    calendar.bind("<<CalendarSelected>>", on_date_click)
    
    add_holiday_btn = ttk.Button(top, text='Ajouter Jour Férié', width=20, command=on_add_holiday)
    add_holiday_btn.pack(padx=10, pady=10)
    
def add_holiday_to_db(date, label_text, window):
    try:
        # Connect to the shared database using DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO jours_feries (date, label)
            VALUES (?, ?)
        ''', (date, label_text))
        
        conn.commit()
        messagebox.showinfo("Succès", "Le jour férié a été ajouté avec succès!")
        window.destroy()
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout du jour férié : {str(e)}")
    finally:
        if conn:
            conn.close()

def fetch_holidays_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jours_feries")
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération des données : {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def create_holidays_tab(frame):
    # Clear all widgets in the frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Create a frame for the buttons at the bottom
    button_frame = ttk.Frame(frame)
    button_frame.pack(side='bottom', fill='x', padx=5, pady=5)
    
    # Create a frame for the list with a scrollbar
    list_frame = ttk.Frame(frame)
    list_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)
    
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side='right', fill='y')
    
    # Create a Treeview widget to display holiday data
    tree = ttk.Treeview(list_frame, columns=('ID', 'Date', 'Label'), 
                        show='headings', yscrollcommand=scrollbar.set)
    
    tree.heading('ID', text='ID')
    tree.heading('Date', text='Date')
    tree.heading('Label', text='Description')
    
    tree.column('ID', width=50)
    tree.column('Date', width=100)
    tree.column('Label', width=200)
    
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=tree.yview)
    
    # Fetch and display the holiday data
    holidays_data = fetch_holidays_data()
    for row in holidays_data:
        tree.insert('', 'end', values=(row[0], row[1], row[2]))
    
    def delete_selected_holiday():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner un jour férié à supprimer")
            return
        
        holiday_id = tree.item(selected_item[0])['values'][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce jour férié ?"):
            delete_holiday(holiday_id)
            create_holidays_tab(frame)  # Refresh the display
    
    def refresh_data():
        create_holidays_tab(frame)
    
    # Create buttons for adding, deleting, and refreshing
    add_holiday_btn = ttk.Button(button_frame, text='Ajouter Jour Férié', width=20, 
                                 command=open_date_entry_window)
    add_holiday_btn.pack(side='left', padx=5, pady=5)
    
    del_holiday_btn = ttk.Button(button_frame, text='Supprimer Jour Férié', width=20, 
                                 command=delete_selected_holiday)
    del_holiday_btn.pack(side='left', padx=5, pady=5)
    
    refresh_btn = ttk.Button(button_frame, text='Actualiser', width=20, 
                             command=refresh_data)
    refresh_btn.pack(side='left', padx=5, pady=5)

def delete_holiday(holiday_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM jours_feries WHERE id = ?", (holiday_id,))
        conn.commit()
        messagebox.showinfo("Succès", "Jour férié supprimé avec succès!")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")
    finally:
        if conn:
            conn.close()
