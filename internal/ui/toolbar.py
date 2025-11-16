"""
Toolbar component with common action buttons
"""
import tkinter as tk
from tkinter import ttk


class ToolbarFrame:
    """Toolbar with common action buttons"""
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize toolbar frame
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.buttons = {}
        
        self._create_toolbar()

    def _create_toolbar(self):
        """Create toolbar buttons"""
        self.frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # New Chat button
        self.buttons['new'] = ttk.Button(
            self.frame, text="New Chat", width=12
        )
        self.buttons['new'].grid(row=0, column=0, padx=(0, 5))
        
        # Separator
        ttk.Separator(self.frame, orient="vertical").grid(
            row=0, column=1, sticky="ns", padx=5, pady=5
        )
        
        # Copy button
        self.buttons['copy'] = ttk.Button(
            self.frame, text="Copy", width=10
        )
        self.buttons['copy'].grid(row=0, column=2, padx=(5, 5))
        
        # Paste button
        self.buttons['paste'] = ttk.Button(
            self.frame, text="Paste", width=10
        )
        self.buttons['paste'].grid(row=0, column=3, padx=(0, 5))
        
        # Separator
        ttk.Separator(self.frame, orient="vertical").grid(
            row=0, column=4, sticky="ns", padx=5, pady=5
        )
        
        # Clear button
        self.buttons['clear'] = ttk.Button(
            self.frame, text="Clear", width=10
        )
        self.buttons['clear'].grid(row=0, column=5, padx=(5, 5))
        
        # Separator
        ttk.Separator(self.frame, orient="vertical").grid(
            row=0, column=6, sticky="ns", padx=5, pady=5
        )
        
        # Settings button
        self.buttons['settings'] = ttk.Button(
            self.frame, text="⚙️ Settings", width=12
        )
        self.buttons['settings'].grid(row=0, column=7, padx=(5, 5))
        
        # Help button
        self.buttons['help'] = ttk.Button(
            self.frame, text="Help", width=10
        )
        self.buttons['help'].grid(row=0, column=8, padx=(0, 0))
        
        # Spacer to push buttons to left
        self.frame.grid_columnconfigure(9, weight=1)

    def set_command(self, button_name: str, command):
        """
        Set command for a button
        
        Args:
            button_name: Name of the button ('new', 'copy', 'paste', 'clear', 'settings', 'help')
            command: Callback function
        """
        if button_name in self.buttons:
            self.buttons[button_name].config(command=command)

    def set_all_commands(self, commands: dict):
        """
        Set commands for multiple buttons at once
        
        Args:
            commands: Dictionary mapping button names to command functions
        """
        for button_name, command in commands.items():
            self.set_command(button_name, command)

