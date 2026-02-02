"""
Print Schedules Frame
View and print saved schedules for any week
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from src.utils.theme import ThemeManager
from src.utils.config import DB_PATH


class PrintSchedulesFrame(ttk.Frame):
    """Frame for viewing and printing schedules"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.database
        
        self.current_week = 1
        self.max_weeks = 36
        
        self.build_ui()
        self.load_schedule()
    
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
            text='🖨️ Imprimer l\'État',
            style='Heading.TLabel'
        )
        title.pack(side='left', padx=20)
        
        # Week selector
        week_frame = ttk.Frame(top_bar)
        week_frame.pack(side='right')
        
        ttk.Label(week_frame, text='Semaine:').pack(side='left', padx=5)
        
        prev_btn = ThemeManager.create_button(
            week_frame,
            text='←',
            command=self.previous_week
        )
        prev_btn.pack(side='left')
        
        self.week_label = ttk.Label(
            week_frame,
            text=f'{self.current_week}/{self.max_weeks}',
            font=('Arial', 12, 'bold')
        )
        self.week_label.pack(side='left', padx=10)
        
        next_btn = ThemeManager.create_button(
            week_frame,
            text='→',
            command=self.next_week
        )
        next_btn.pack(side='left')
        
        # Action buttons
        action_bar = ttk.Frame(main_container)
        action_bar.pack(fill='x', pady=(0, 10))
        
        print_btn = ThemeManager.create_button(
            action_bar,
            text='🖨️ Imprimer',
            command=self.print_schedule
        )
        print_btn.pack(side='left', padx=5)
        
        export_btn = ThemeManager.create_button(
            action_bar,
            text='💾 Exporter HTML',
            command=self.export_html
        )
        export_btn.pack(side='left', padx=5)
        
        refresh_btn = ThemeManager.create_button(
            action_bar,
            text='🔄 Actualiser',
            command=self.load_schedule
        )
        refresh_btn.pack(side='left', padx=5)
        
        # Schedule display area with scrollbar
        display_frame = ttk.Frame(main_container)
        display_frame.pack(fill='both', expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(display_frame, bg='white')
        scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=canvas.yview)
        
        self.schedule_display = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        
        canvas_frame = canvas.create_window((0, 0), window=self.schedule_display, anchor='nw')
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        self.schedule_display.bind('<Configure>', configure_scroll)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=e.width))
    
    def load_schedule(self):
        """Load and display schedule for current week"""
        # Clear existing display
        for widget in self.schedule_display.winfo_children():
            widget.destroy()
        
        try:
            # Get days and time slots
            days = self.db.execute_query("SELECT * FROM days ORDER BY display_order")
            slots = self.db.execute_query("SELECT * FROM time_slots ORDER BY display_order")
            
            # Get schedule data for current week
            query = """
                SELECT day_id, slot_id, content
                FROM schedule_data
                WHERE week_number = ?
            """
            schedule_data = self.db.execute_query(query, (self.current_week,))
            
            # Convert to dictionary for easy lookup
            schedule_dict = {(row['day_id'], row['slot_id']): row['content'] 
                           for row in schedule_data}
            
            # Build display table
            # Header row
            header_frame = ttk.Frame(self.schedule_display)
            header_frame.grid(row=0, column=0, columnspan=len(days)+1, sticky='ew', padx=1, pady=1)
            
            tk.Label(
                header_frame,
                text=f'Semaine {self.current_week}',
                font=('Arial', 14, 'bold'),
                bg='#2c3e50',
                fg='white',
                pady=10
            ).pack(fill='x')
            
            # Column headers
            tk.Label(
                self.schedule_display,
                text='Horaires',
                font=('Arial', 10, 'bold'),
                bg='#34495e',
                fg='white',
                width=15,
                pady=5
            ).grid(row=1, column=0, sticky='nsew', padx=1, pady=1)
            
            for col_idx, day in enumerate(days, start=1):
                tk.Label(
                    self.schedule_display,
                    text=day['name'],
                    font=('Arial', 10, 'bold'),
                    bg='#3498db',
                    fg='white',
                    width=20,
                    pady=5
                ).grid(row=1, column=col_idx, sticky='nsew', padx=1, pady=1)
            
            # Data rows
            for row_idx, slot in enumerate(slots, start=2):
                # Time slot label
                slot_text = f"{slot['start_time']}\n{slot['end_time']}"
                bg_color = '#e74c3c' if slot['is_lunch'] else '#34495e'
                
                tk.Label(
                    self.schedule_display,
                    text=slot_text,
                    font=('Arial', 9),
                    bg=bg_color,
                    fg='white',
                    pady=10
                ).grid(row=row_idx, column=0, sticky='nsew', padx=1, pady=1)
                
                # Schedule cells
                for col_idx, day in enumerate(days, start=1):
                    cell_key = (day['id'], slot['id'])
                    content = schedule_dict.get(cell_key, '')
                    
                    cell_bg = '#ecf0f1' if slot['is_lunch'] else 'white'
                    
                    tk.Label(
                        self.schedule_display,
                        text=content,
                        font=('Arial', 9),
                        bg=cell_bg,
                        relief='solid',
                        borderwidth=1,
                        wraplength=150,
                        justify='left',
                        anchor='nw',
                        padx=5,
                        pady=5
                    ).grid(row=row_idx, column=col_idx, sticky='nsew', padx=1, pady=1)
            
            # Configure grid weights
            for col in range(len(days) + 1):
                self.schedule_display.grid_columnconfigure(col, weight=1, minsize=120)
            
            for row in range(len(slots) + 2):
                self.schedule_display.grid_rowconfigure(row, weight=1)
            
            logging.info(f"Loaded schedule for week {self.current_week}")
            
        except Exception as e:
            logging.error(f"Error loading schedule: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger l'emploi du temps:\n{str(e)}")
    
    def print_schedule(self):
        """Print the current schedule"""
        try:
            # Generate HTML for printing
            html = self.generate_html()
            
            # Save to temporary file
            import tempfile
            import webbrowser
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html)
                temp_path = f.name
            
            # Open in browser for printing
            webbrowser.open(f'file://{temp_path}')
            
            messagebox.showinfo(
                "Impression",
                "L'emploi du temps a été ouvert dans votre navigateur.\n"
                "Utilisez Ctrl+P ou Cmd+P pour imprimer."
            )
            
            logging.info(f"Opened schedule for printing: week {self.current_week}")
            
        except Exception as e:
            logging.error(f"Error printing schedule: {e}")
            messagebox.showerror("Erreur", f"Impossible d'imprimer:\n{str(e)}")
    
    def export_html(self):
        """Export schedule to HTML file"""
        try:
            from tkinter import filedialog
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension='.html',
                filetypes=[('HTML files', '*.html'), ('All files', '*.*')],
                initialfile=f'emploi_du_temps_semaine_{self.current_week}.html'
            )
            
            if not filename:
                return
            
            # Generate and save HTML
            html = self.generate_html()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            messagebox.showinfo("Succès", f"Emploi du temps exporté vers:\n{filename}")
            logging.info(f"Exported schedule to: {filename}")
            
        except Exception as e:
            logging.error(f"Error exporting schedule: {e}")
            messagebox.showerror("Erreur", f"Impossible d'exporter:\n{str(e)}")
    
    def generate_html(self):
        """Generate HTML representation of schedule"""
        try:
            # Get data
            days = self.db.execute_query("SELECT * FROM days ORDER BY display_order")
            slots = self.db.execute_query("SELECT * FROM time_slots ORDER BY display_order")
            
            query = """
                SELECT day_id, slot_id, content
                FROM schedule_data
                WHERE week_number = ?
            """
            schedule_data = self.db.execute_query(query, (self.current_week,))
            schedule_dict = {(row['day_id'], row['slot_id']): row['content'] 
                           for row in schedule_data}
            
            # Build HTML
            html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emploi du Temps - Semaine {self.current_week}</title>
    <style>
        @media print {{
            @page {{ margin: 1cm; }}
            body {{ margin: 0; }}
        }}
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        th.time {{
            background-color: #34495e;
        }}
        th.lunch {{
            background-color: #e74c3c;
        }}
        td.time {{
            background-color: #34495e;
            color: white;
            font-weight: bold;
            white-space: pre-line;
        }}
        td.lunch {{
            background-color: #ecf0f1;
        }}
        td.content {{
            text-align: left;
            vertical-align: top;
            min-height: 60px;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            text-align: center;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Emploi du Temps - Semaine {self.current_week}</h1>
    </div>
    <table>
        <thead>
            <tr>
                <th class="time">Horaires</th>
"""
            
            # Add day headers
            for day in days:
                html += f"                <th>{day['name']}</th>\n"
            
            html += """            </tr>
        </thead>
        <tbody>
"""
            
            # Add schedule rows
            for slot in slots:
                lunch_class = ' class="lunch"' if slot['is_lunch'] else ''
                slot_text = f"{slot['start_time']}&#10;{slot['end_time']}"
                
                html += f"            <tr>\n"
                html += f"                <td class=\"time{' lunch' if slot['is_lunch'] else ''}\">{slot_text}</td>\n"
                
                for day in days:
                    cell_key = (day['id'], slot['id'])
                    content = schedule_dict.get(cell_key, '&nbsp;')
                    content = content.replace('\n', '<br>')
                    
                    html += f"                <td class=\"content{' lunch' if slot['is_lunch'] else ''}\">{content}</td>\n"
                
                html += "            </tr>\n"
            
            html += """        </tbody>
    </table>
</body>
</html>
"""
            
            return html
            
        except Exception as e:
            logging.error(f"Error generating HTML: {e}")
            raise
    
    def previous_week(self):
        """Navigate to previous week"""
        if self.current_week > 1:
            self.current_week -= 1
            self.week_label.config(text=f'{self.current_week}/{self.max_weeks}')
            self.load_schedule()
    
    def next_week(self):
        """Navigate to next week"""
        if self.current_week < self.max_weeks:
            self.current_week += 1
            self.week_label.config(text=f'{self.current_week}/{self.max_weeks}')
            self.load_schedule()
    
    def go_back(self):
        """Return to dashboard"""
        self.controller.show_frame('DashboardFrame')
