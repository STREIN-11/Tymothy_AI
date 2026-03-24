try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("tkinter not available - splash screen disabled")

import threading
import time

if TKINTER_AVAILABLE:
    class SplashScreen:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Tymor AI Assistant")
            self.root.geometry("400x200")
            self.root.resizable(False, False)
            self.root.configure(bg='#2c3e50')
            
            # Center the window
            self.root.eval('tk::PlaceWindow . center')
            
            # Remove window decorations
            self.root.overrideredirect(True)
            
            # Create main frame
            main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            title_label = tk.Label(
                main_frame, 
                text="Tymor AI Assistant", 
                font=('Arial', 18, 'bold'),
                fg='white',
                bg='#2c3e50'
            )
            title_label.pack(pady=(10, 20))
            
            # Status label
            self.status_label = tk.Label(
                main_frame,
                text="Initializing...",
                font=('Arial', 10),
                fg='#ecf0f1',
                bg='#2c3e50'
            )
            self.status_label.pack(pady=(0, 10))
            
            # Progress bar
            self.progress = ttk.Progressbar(
                main_frame,
                length=300,
                mode='determinate',
                style='Custom.Horizontal.TProgressbar'
            )
            self.progress.pack(pady=(0, 10))
            
            # Percentage label
            self.percent_label = tk.Label(
                main_frame,
                text="0%",
                font=('Arial', 12, 'bold'),
                fg='#3498db',
                bg='#2c3e50'
            )
            self.percent_label.pack()
            
            # Configure progress bar style
            style = ttk.Style()
            style.theme_use('clam')
            style.configure(
                'Custom.Horizontal.TProgressbar',
                background='#3498db',
                troughcolor='#34495e',
                borderwidth=0,
                lightcolor='#3498db',
                darkcolor='#3498db'
            )
            
            self.progress['maximum'] = 100
            self.progress['value'] = 0
            
        def update_progress(self, value, status="Loading..."):
            """Update progress bar and status"""
            self.progress['value'] = value
            self.percent_label.config(text=f"{int(value)}%")
            self.status_label.config(text=status)
            self.root.update()
            
        def close(self):
            """Close splash screen"""
            self.root.destroy()
            
        def show(self):
            """Show splash screen"""
            self.root.update()
else:
    class SplashScreen:
        def __init__(self): pass
        def update_progress(self, value, status): print(f"[{int(value)}%] {status}")
        def close(self): pass
        def show(self): pass

# Global splash instance
splash = None

def show_splash():
    """Show splash screen"""
    
    global splash
    splash = SplashScreen()
    splash.show()

def update_splash(progress, status):
    """Update splash screen progress"""
    global splash
    if splash:
        splash.update_progress(progress, status)

def close_splash():
    """Close splash screen"""
    global splash
    if splash:
        splash.close()
        splash = None