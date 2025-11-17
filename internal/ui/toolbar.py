"""
Toolbar component - Windows file manager style toolbar
"""
import tkinter as tk
from tkinter import ttk


def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = tk.Label(
            tooltip,
            text=text,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("TkDefaultFont", 9)
        )
        label.pack()
        widget.tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
    
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


class Toolbar:
    """Toolbar with common action buttons"""
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize toolbar
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.frame = ttk.Frame(parent, relief=tk.FLAT, borderwidth=1)
        self.buttons = {}
        
        self._create_toolbar()

    def _create_toolbar(self):
        """Create toolbar with icon buttons - clean and simple style"""
        self.frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.frame.grid_columnconfigure(0, weight=0)
        
        # Icon button style - clean and minimal
        icon_style = {
            'width': 3,
            'padding': (4, 2)
        }
        
        # File Manager button (📁) - First button
        self.buttons['file'] = ttk.Button(
            self.frame,
            text="📁",
            **icon_style
        )
        self.buttons['file'].grid(row=0, column=0, padx=1, pady=2, sticky="w")
        create_tooltip(self.buttons['file'], "File Manager")
        
        # New Chat button (📝 or ✨) - Second button
        self.buttons['new'] = ttk.Button(
            self.frame,
            text="✨",
            **icon_style
        )
        self.buttons['new'].grid(row=0, column=1, padx=1, pady=2, sticky="w")
        create_tooltip(self.buttons['new'], "New Chat")
        
        # Separator
        separator1 = ttk.Separator(self.frame, orient=tk.VERTICAL)
        separator1.grid(row=0, column=2, padx=3, pady=2, sticky="ns")
        
        # Settings button (⚙️)
        self.buttons['settings'] = ttk.Button(
            self.frame,
            text="⚙️",
            **icon_style
        )
        self.buttons['settings'].grid(row=0, column=3, padx=1, pady=2, sticky="w")
        create_tooltip(self.buttons['settings'], "Settings")
        
        # Model Management button (📦 or 🤖)
        self.buttons['models'] = ttk.Button(
            self.frame,
            text="📦",
            **icon_style
        )
        self.buttons['models'].grid(row=0, column=4, padx=1, pady=2, sticky="w")
        create_tooltip(self.buttons['models'], "Model Management")
        
        # Separator
        separator2 = ttk.Separator(self.frame, orient=tk.VERTICAL)
        separator2.grid(row=0, column=5, padx=3, pady=2, sticky="ns")
        
        # Audio Processor button (🎵)
        self.buttons['audio'] = ttk.Button(
            self.frame,
            text="🎵",
            **icon_style
        )
        self.buttons['audio'].grid(row=0, column=6, padx=1, pady=2, sticky="w")
        create_tooltip(self.buttons['audio'], "Audio Processor")
        
        # Refresh button (🔄)
        self.buttons['refresh'] = ttk.Button(
            self.frame,
            text="🔄",
            **icon_style
        )
        self.buttons['refresh'].grid(row=0, column=7, padx=1, pady=2, sticky="w")
        create_tooltip(self.buttons['refresh'], "Refresh Models")
        
        # Spacer to push buttons to left
        spacer = ttk.Frame(self.frame)
        spacer.grid(row=0, column=8, sticky="ew")
        self.frame.grid_columnconfigure(8, weight=1)

    def set_command(self, button_name: str, command):
        """
        Set command for a button
        
        Args:
            button_name: Name of the button ('new', 'clear', 'settings', etc.)
            command: Callback function
        """
        if button_name in self.buttons:
            self.buttons[button_name].config(command=command)

    def get_button(self, button_name: str) -> ttk.Button:
        """
        Get button widget
        
        Args:
            button_name: Name of the button
            
        Returns:
            Button widget or None
        """
        return self.buttons.get(button_name)

