import tkinter as tk
from tkinter import ttk
from theme_manager import ThemeManager

class LoadingWindow:
    def __init__(self, title="Chargement...", message="Veuillez patienter..."):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create loading window
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title(title)
        self.loading_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Remove window decorations and make it float
        self.loading_window.overrideredirect(True)
        self.loading_window.attributes('-topmost', True)
        
        # Calculate center position
        window_width = 300
        window_height = 150
        screen_width = self.loading_window.winfo_screenwidth()
        screen_height = self.loading_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.loading_window.geometry(f'{window_width}x{window_height }+{x}+{y}')
        
        # Main frame
        self.main_frame = ttk.Frame(self.loading_window, style='TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create styles for loading elements
        style = ttk.Style()
        style.configure('Loading.TLabel',
            font=ThemeManager.FONTS['body'],
            foreground=ThemeManager.COLORS['text_primary'],
            background=ThemeManager.COLORS['background'],
            padding=5
        )
        
        # Loading icon (circle animation)
        self.canvas = tk.Canvas(
            self.main_frame,
            width=40, height=40,
            bg=ThemeManager.COLORS['background'],
            highlightthickness=0
        )
        self.canvas.pack(pady=(0, 10))
        
        self.spinner = self.canvas.create_arc(
            10, 10, 30, 30,
            start=0, extent=300,
            fill=ThemeManager.COLORS['primary']
        )
        
        # Message label
        self.message_label = ttk.Label(
            self.main_frame,
            text=message,
            style='Loading.TLabel'
        )
        self.message_label.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="Initialisation...",
            style='Loading.TLabel',
            font=ThemeManager.FONTS['small']
        )
        self.status_label.pack(pady=5)
        
        # Start animations
        self.progress.start(10)
        self.animate_spinner()
        
        # Make window visible
        self.loading_window.deiconify()
        self.loading_window.update()
    
    def animate_spinner(self):
        """Animate the spinning circle"""
        angle = 0
        def update_spinner():
            nonlocal angle
            angle = (angle + 10) % 360
            self.canvas.delete(self.spinner)
            self.spinner = self.canvas.create_arc(
                10, 10, 30, 30,
                start=angle,
                extent=300,
                fill=ThemeManager.COLORS['primary']
            )
            self.loading_window.after(50, update_spinner)
        update_spinner()
    
    def update_status(self, text):
        """Update the status text"""
        self.status_label.config(text=text)
        self.loading_window.update()
    
    def update_message(self, text):
        """Update the main message text"""
        self.message_label.config(text=text)
        self.loading_window.update()
    
    def close(self):
        """Close the loading window"""
        self.progress.stop()
        self.loading_window.destroy()
        self.root.destroy()

class LoadingContext:
    def __init__(self, title="Chargement...", message="Veuillez patienter..."):
        self.title = title
        self.message = message
        self.loading_window = None
    
    def __enter__(self):
        self.loading_window = LoadingWindow(self.title, self.message)
        return self.loading_window
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.loading_window:
            self.loading_window.close()