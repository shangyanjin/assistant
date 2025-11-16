"""
Common UI components
"""
import tkinter as tk
from tkinter import ttk


class HeaderFrame:
    """Header frame with model selection and controls"""
    
    def __init__(self, parent: tk.Tk, settings_callback=None):
        """
        Initialize header frame
        
        Args:
            parent: Parent window
            settings_callback: Callback function for settings button
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.model_select: ttk.Combobox = None
        self.refresh_button: ttk.Button = None
        self.settings_button: ttk.Button = None
        self.host_input: ttk.Entry = None
        self.settings_callback = settings_callback
        
        self._create_header()

    def _create_header(self):
        """Create header components"""
        # Header frame at row 2 (after menu and toolbar)
        self.frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.frame.grid_columnconfigure(4, weight=1)

        # Model selection
        self.model_select = ttk.Combobox(self.frame, state="readonly", width=30)
        self.model_select.grid(row=0, column=0)

        # Settings button
        self.settings_button = ttk.Button(
            self.frame, text="⚙️", width=3, command=self.settings_callback
        )
        self.settings_button.grid(row=0, column=1, padx=(5, 0))

        # Refresh button
        self.refresh_button = ttk.Button(self.frame, text="Refresh")
        self.refresh_button.grid(row=0, column=2, padx=(5, 0))

        # Host label and input
        ttk.Label(self.frame, text="Host:").grid(row=0, column=3, padx=(10, 0))
        self.host_input = ttk.Entry(self.frame, width=24)
        self.host_input.grid(row=0, column=4, padx=(5, 15))
        self.host_input.insert(0, "http://127.0.0.1:11434")

    def get_selected_model(self) -> str:
        """Get selected model"""
        return self.model_select.get() if self.model_select else ""

    def set_models(self, models: list):
        """Set available models"""
        if self.model_select:
            self.model_select["values"] = models
            if models:
                self.model_select.set(models[0])

    def get_host(self) -> str:
        """Get host URL"""
        return self.host_input.get() if self.host_input else "http://127.0.0.1:11434"
    
    def set_settings_callback(self, callback):
        """Set settings button callback"""
        self.settings_callback = callback
        if self.settings_button:
            self.settings_button.config(command=callback)


class InputFrame:
    """Input frame with text input and send button"""
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize input frame
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.user_input: tk.Text = None
        self.send_button: ttk.Button = None
        
        self._create_input()

    def _create_input(self):
        """Create input components"""
        # Input frame at row 5 (after menu, toolbar, header, chat, progress)
        self.frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.frame.grid_columnconfigure(0, weight=1)

        # User input
        import tkinter.font as font
        default_font = font.nametofont("TkTextFont").actual()["family"]
        self.user_input = tk.Text(
            self.frame, font=(default_font, 12), height=4, wrap=tk.WORD
        )
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Send button
        self.send_button = ttk.Button(self.frame, text="Send")
        self.send_button.grid(row=0, column=1)
        self.send_button.state(["disabled"])

    def get_text(self) -> str:
        """Get input text"""
        return self.user_input.get("1.0", "end-1c").strip() if self.user_input else ""

    def clear(self):
        """Clear input"""
        if self.user_input:
            self.user_input.delete("1.0", "end")

    def insert_newline(self):
        """Insert newline"""
        if self.user_input:
            self.user_input.insert("end", "\n")


class ProgressFrame:
    """Progress bar frame"""
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize progress frame
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.frame = ttk.Frame(parent, height=28)
        self.progress: ttk.Progressbar = None
        self.stop_button: ttk.Button = None
        
        self._create_progress()

    def _create_progress(self):
        """Create progress components"""
        # Progress frame at row 4 (after menu, toolbar, header, chat)
        self.frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(
            self.frame,
            mode="indeterminate",
        )

        # Stop button
        self.stop_button = ttk.Button(
            self.frame,
            width=5,
            text="Stop",
        )

    def show(self):
        """Show progress bar"""
        self.progress.grid(row=0, column=0, sticky="nsew")
        self.stop_button.grid(row=0, column=1, padx=20)
        self.progress.start(5)

    def hide(self):
        """Hide progress bar"""
        self.progress.stop()
        self.stop_button.grid_remove()
        self.progress.grid_remove()

