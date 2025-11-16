"""
Toolbar component - Windows file manager style toolbar
"""
import tkinter as tk
from tkinter import ttk


class Toolbar:
    """Toolbar with common action buttons"""
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize toolbar
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        self.buttons = {}
        
        self._create_toolbar()

    def _create_toolbar(self):
        """Create toolbar with buttons"""
        self.frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.frame.grid_columnconfigure(0, weight=0)
        
        # Button style - similar to Windows file manager
        button_style = {
            'width': 10,
            'padding': (5, 2)
        }
        
        # New Chat button
        self.buttons['new'] = ttk.Button(
            self.frame,
            text="New Chat",
            **button_style
        )
        self.buttons['new'].grid(row=0, column=0, padx=2, pady=2, sticky="w")
        
        # Clear button
        self.buttons['clear'] = ttk.Button(
            self.frame,
            text="Clear",
            **button_style
        )
        self.buttons['clear'].grid(row=0, column=1, padx=2, pady=2, sticky="w")
        
        # Separator
        separator1 = ttk.Separator(self.frame, orient=tk.VERTICAL)
        separator1.grid(row=0, column=2, padx=5, pady=2, sticky="ns")
        
        # Settings button
        self.buttons['settings'] = ttk.Button(
            self.frame,
            text="Settings",
            **button_style
        )
        self.buttons['settings'].grid(row=0, column=3, padx=2, pady=2, sticky="w")
        
        # Model Management button
        self.buttons['models'] = ttk.Button(
            self.frame,
            text="Models",
            **button_style
        )
        self.buttons['models'].grid(row=0, column=4, padx=2, pady=2, sticky="w")
        
        # Separator
        separator2 = ttk.Separator(self.frame, orient=tk.VERTICAL)
        separator2.grid(row=0, column=5, padx=5, pady=2, sticky="ns")
        
        # Refresh button
        self.buttons['refresh'] = ttk.Button(
            self.frame,
            text="Refresh",
            **button_style
        )
        self.buttons['refresh'].grid(row=0, column=6, padx=2, pady=2, sticky="w")
        
        # Spacer to push buttons to left
        spacer = ttk.Frame(self.frame)
        spacer.grid(row=0, column=7, sticky="ew")
        self.frame.grid_columnconfigure(7, weight=1)

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

