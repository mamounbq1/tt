import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
import os
import logging
from config import DB_PATH  # Use the shared database path

class ExcelImporterFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configure logging
        self.setup_logging()

        try:
            self.create_ui()
            self.init_db()
            self.load_entries()
        except Exception as e:
            self.log_error("Initialization error", e)
            messagebox.showerror("Erreur Critique", f"Erreur d'initialisation : {e}")

    def setup_logging(self):
        """Configure logging for the application."""
        try:
            # Ensure logs directory exists
            os.makedirs("logs", exist_ok=True)
            logging.basicConfig(
                filename='logs/application.log', 
                level=logging.ERROR,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        except Exception as e:
            messagebox.showwarning("Avertissement", f"Impossible de configurer la journalisation : {e}")

    def log_error(self, context, error):
        """Log errors with context."""
        logging.error(f"{context}: {str(error)}")

    def create_ui(self):
        try:
            # Top Navigation (Retour Button)
            top_frame = ttk.Frame(self)
            top_frame.pack(fill="x", padx=10, pady=5)
            ttk.Button(top_frame, text="Retour au tableau de bord", command=self.safe_return).pack(side=tk.LEFT)

            # Search Bar
            self.search_var = tk.StringVar()
            search_frame = ttk.Frame(self)
            search_frame.pack(pady=5)
            ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT, padx=5)
            texte_recherche = ttk.Entry(search_frame, textvariable=self.search_var)
            texte_recherche.pack(side=tk.LEFT, padx=5)
            texte_recherche.bind("<KeyRelease>", self.safe_load_entries)

            # Scrollable Table
            table_frame = ttk.Frame(self)
            table_frame.pack(fill="both", expand=True, padx=10, pady=5)

            # Scrollbar for the Treeview
            tree_scroll = ttk.Scrollbar(table_frame, orient="vertical")
            self.tree = ttk.Treeview(
                table_frame,
                columns=("ID", "Valeur"),
                show="headings",
                selectmode="browse",
                yscrollcommand=tree_scroll.set
            )
            tree_scroll.config(command=self.tree.yview)

            # Treeview Columns configuration
            self.tree.heading("ID", text="ID")
            self.tree.heading("Valeur", text="Valeur")
            self.tree.column("ID", width=50, stretch=False, anchor="center")
            self.tree.column("Valeur", stretch=True, anchor="w")

            # Multi-select bindings
            def on_click(event):
                try:
                    for item in self.tree.selection():
                        self.tree.selection_remove(item)
                    
                    clicked_item = self.tree.identify_row(event.y)
                    if clicked_item:
                        self.tree.selection_add(clicked_item)
                        self.tree.focus(clicked_item)
                        self.tree.selection_mark(clicked_item)
                except Exception as e:
                    self.log_error("Erreur de sélection", e)

            def on_drag(event):
                try:
                    clicked_item = self.tree.identify_row(event.y)
                    if clicked_item:
                        first_selected = self.tree.selection()[0] if self.tree.selection() else None
                        if first_selected:
                            for item in self.tree.selection():
                                self.tree.selection_remove(item)
                            
                            first_index = self.tree.get_children().index(first_selected)
                            current_index = self.tree.get_children().index(clicked_item)
                            
                            start = min(first_index, current_index)
                            end = max(first_index, current_index)
                            
                            for item in self.tree.get_children()[start:end+1]:
                                self.tree.selection_add(item)
                except Exception as e:
                    self.log_error("Erreur de glissement", e)

            self.tree.bind('<Button-1>', on_click)
            self.tree.bind('<B1-Motion>', on_drag)

            # Layout
            self.tree.pack(side="left", fill="both", expand=True)
            tree_scroll.pack(side="right", fill="y")

            # Buttons at the bottom
            btn_frame = ttk.Frame(self)
            btn_frame.pack(pady=5)

            ttk.Button(btn_frame, text="Ajouter", command=self.safe_add_texte).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Modifier", command=self.safe_update_texte).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Supprimer", command=self.safe_delete_entries).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Importer Excel", command=self.safe_import_entries_from_excel).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            self.log_error("Erreur de création de l'interface", e)
            messagebox.showerror("Erreur Critique", f"Impossible de créer l'interface : {e}")

    def safe_return(self):
        """Safely return to home frame."""
        try:
            self.controller.show_frame("HomeFrame")
        except Exception as e:
            self.log_error("Erreur de retour", e)
            messagebox.showerror("Erreur", f"Impossible de retourner à l'écran d'accueil : {e}")

    def init_db(self):
        """Initialize database with robust error handling."""
        try:
            # Ensure the directory for the database exists
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ma_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    valeur TEXT UNIQUE
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            self.log_error("Erreur d'initialisation de la base de données", e)
            messagebox.showerror("Erreur de Base de Données", f"Impossible d'initialiser la base de données : {e}")
        except Exception as e:
            self.log_error("Erreur inattendue lors de l'initialisation de la base de données", e)
            messagebox.showerror("Erreur Critique", f"Erreur inattendue : {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def safe_load_entries(self, event=None):
        """Safely load entries with error handling."""
        try:
            self.load_entries()
        except Exception as e:
            self.log_error("Erreur de chargement des entrées", e)
            messagebox.showerror("Erreur", f"Impossible de charger les entrées : {e}")

    def load_entries(self):
        """Load and display entries from the database with search filter."""
        try:
            self.tree.delete(*self.tree.get_children())
            filter_text = self.search_var.get()
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            query = "SELECT * FROM ma_table"
            if filter_text:
                query += " WHERE valeur LIKE ?"
                cursor.execute(query, ('%' + filter_text + '%',))
            else:
                cursor.execute(query)
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            self.log_error("Erreur de requête SQL", e)
            messagebox.showerror("Erreur de Base de Données", f"Impossible de charger les entrées : {e}")
        except Exception as e:
            self.log_error("Erreur inattendue lors du chargement", e)
            messagebox.showerror("Erreur Critique", f"Erreur inattendue : {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def safe_add_texte(self):
        """Safely add a new text entry."""
        try:
            self.add_texte()
        except Exception as e:
            self.log_error("Erreur lors de l'ajout", e)
            messagebox.showerror("Erreur", f"Impossible d'ajouter l'entrée : {e}")

    def add_texte(self):
        """Add new texte entry with comprehensive error handling."""
        valeur = self.simple_texte_dialog("Nouvelle Valeur", "Valeur:")
        if not valeur:
            return

        try:
            # Validate input
            if not valeur.strip():
                messagebox.showwarning("Avertissement", "La valeur ne peut pas être vide.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check for duplicate before inserting
            cursor.execute("SELECT 1 FROM ma_table WHERE valeur = ?", (valeur,))
            if cursor.fetchone():
                messagebox.showwarning("Avertissement", "Cette valeur existe déjà.")
                return

            cursor.execute("INSERT INTO ma_table (valeur) VALUES (?)", (valeur,))
            conn.commit()
            self.load_entries()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Avertissement", "Impossible d'ajouter : contrainte d'intégrité.")
        except sqlite3.Error as e:
            self.log_error("Erreur SQL lors de l'ajout", e)
            messagebox.showerror("Erreur de Base de Données", f"Erreur lors de l'ajout : {e}")
        except Exception as e:
            self.log_error("Erreur inattendue lors de l'ajout", e)
            messagebox.showerror("Erreur Critique", f"Erreur inattendue : {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def safe_update_texte(self):
        """Safely update a text entry."""
        try:
            self.update_texte()
        except Exception as e:
            self.log_error("Erreur lors de la modification", e)
            messagebox.showerror("Erreur", f"Impossible de modifier l'entrée : {e}")

    def update_texte(self):
        """Update selected texte entry with comprehensive error handling."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Sélectionnez une valeur à modifier.")
            return
        if len(selected) > 1:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner UNE seule ligne à modifier.")
            return

        try:
            entry_id, valeur = self.tree.item(selected[0])["values"]
            new_valeur = self.simple_texte_dialog("Modifier Valeur", "Nouvelle valeur:", valeur)
            
            if not new_valeur:
                return

            # Validate input
            if not new_valeur.strip():
                messagebox.showwarning("Avertissement", "La valeur ne peut pas être vide.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check for duplicate before updating
            cursor.execute("SELECT 1 FROM ma_table WHERE valeur = ? AND id != ?", (new_valeur, entry_id))
            if cursor.fetchone():
                messagebox.showwarning("Avertissement", "Cette valeur existe déjà.")
                return

            cursor.execute("UPDATE ma_table SET valeur=? WHERE id=?", (new_valeur, entry_id))
            conn.commit()
            self.load_entries()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Avertissement", "Impossible de modifier : contrainte d'intégrité.")
        except sqlite3.Error as e:
            self.log_error("Erreur SQL lors de la modification", e)
            messagebox.showerror("Erreur de Base de Données", f"Erreur lors de la modification : {e}")
        except Exception as e:
            self.log_error("Erreur inattendue lors de la modification", e)
            messagebox.showerror("Erreur Critique", f"Erreur inattendue : {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def safe_delete_entries(self):
        """Safely delete entries."""
        try:
            self.delete_entries()
        except Exception as e:
            self.log_error("Erreur lors de la suppression", e)
            messagebox.showerror("Erreur", f"Impossible de supprimer les entrées : {e}")

    def delete_entries(self):
        """Delete selected entries with comprehensive error handling."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Sélectionnez des valeurs à supprimer.")
            return
        
        try:
            if not messagebox.askyesno("Confirmer", f"Voulez-vous vraiment supprimer {len(selected)} entrée(s) ?"):
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Use parameterized query for safety
            delete_query = "DELETE FROM ma_table WHERE id=?"
            
            for item in selected:
                entry_id = self.tree.item(item)["values"][0]
                cursor.execute(delete_query, (entry_id,))
            
            conn.commit()
            self.load_entries()
        except sqlite3.Error as e:
            self.log_error("Erreur SQL lors de la suppression", e)
            messagebox.showerror("Erreur de Base de Données", f"Erreur lors de la suppression : {e}")
        except Exception as e:
            self.log_error("Erreur inattendue lors de la suppression", e)
            messagebox.showerror("Erreur Critique", f"Erreur inattendue : {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def safe_import_entries_from_excel(self):
        """Safely import entries from Excel."""
        try:
            self.import_entries_from_excel()
        except Exception as e:
            self.log_error("Erreur lors de l'importation Excel", e)
            messagebox.showerror("Erreur", f"Impossible d'importer le fichier Excel : {e}")

    def simple_texte_dialog(self, title, prompt, default=""):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x300")
        dialog.resizable(True, True)

        tk.Label(dialog, text=prompt, wraplength=480).pack(pady=(10, 5))

        text_frame = tk.Frame(dialog)
        text_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        texte = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            yscrollcommand=scrollbar.set,
            height=10,
            width=60
        )
        texte.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=texte.yview)

        # Insert default text if provided
        if default:
            texte.insert(tk.END, str(default))
        
        texte.focus_set()

        result = [None]

        def validate_and_submit():
            value = texte.get("1.0", tk.END).strip()
            if not value:
                messagebox.showwarning("Avertissement", "Le texte ne peut pas être vide.")
                return
            result[0] = value
            dialog.destroy()

        def cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="OK", command=validate_and_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=cancel).pack(side=tk.LEFT, padx=5)

        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

        return result[0]

    def import_entries_from_excel(self):
        """Import values from an Excel file with error handling and logging."""
        fichier_selectionne = filedialog.askopenfilename(
            title="Sélectionnez un fichier Excel",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")]
        )

        if not fichier_selectionne:
            messagebox.showwarning("Avertissement", "Aucun fichier sélectionné.")
            return

        try:
            df = pd.read_excel(fichier_selectionne)
            if df.empty:
                messagebox.showwarning("Avertissement", "Le fichier sélectionné est vide.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            valeurs_inserees = 0
            valeurs_existantes = 0

            for valeur in df.iloc[:, 0]:  # Use only the first column
                cursor.execute("SELECT 1 FROM ma_table WHERE valeur = ?", (valeur,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO ma_table (valeur) VALUES (?)", (valeur,))
                    valeurs_inserees += 1
                else:
                    valeurs_existantes += 1

            conn.commit()
            conn.close()

            messagebox.showinfo("Importation réussie", f"{valeurs_inserees} insérées, {valeurs_existantes} existantes")
            self.load_entries()
        except Exception as e:
            self.log_error("Erreur lors de l'importation Excel", e)
            messagebox.showerror("Erreur", f"Une erreur s'est produite lors de l'importation : {e}")
