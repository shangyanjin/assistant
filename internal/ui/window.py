"""
Main window and application setup
"""
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import webbrowser
from pkg.api.ollama import OllamaClient
from pkg.utils.system import check_system_compatibility
from internal.model.config import AppConfig
from internal.file.service import FileService
from internal.file.ui import FileManagerUI
from internal.file.handler import FileHandler
from internal.chat.window import ChatWindow
from internal.ui.toolbar import Toolbar
from threading import Thread


class App:
    """Main application class"""
    
    def __init__(self):
        """Initialize application"""
        self.config = AppConfig()
        self.root: Optional[tk.Tk] = None
        self.api_client: Optional[OllamaClient] = None
        self.file_service: Optional[FileService] = None
        self.file_ui: Optional[FileManagerUI] = None
        self.file_handler: Optional[FileHandler] = None
        self.chat_window: Optional[ChatWindow] = None
        self.menubar: Optional[tk.Menu] = None
        self.toolbar: Optional[Toolbar] = None

    def _check_tkinter(self):
        """Check if tkinter is available"""
        try:
            import tkinter as tk
            from tkinter import ttk
        except (ModuleNotFoundError, ImportError):
            print(
                "Your Python installation does not include the Tk library.\n"
                "Please refer to https://github.com/chyok/ollama-gui?tab=readme-ov-file#-qa"
            )
            sys.exit(0)

    def _create_window(self):
        """Create main window - File Manager"""
        self.root = tk.Tk()
        self.root.title("Assistant - File Manager")
        
        # Set window size and position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"900x600+{(screen_width - 900) // 2}+{(screen_height - 600) // 2}")
        
        # Configure grid
        # Row 0: Menu bar (handled by tkinter)
        # Row 1: Toolbar
        # Row 2: File Manager header
        # Row 3: File Manager list
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)  # File manager list expands

    def _setup_components(self):
        """Setup application components"""
        # API client (for chat)
        self.api_client = OllamaClient(self.config.api_url)
        
        # File service
        self.file_service = FileService()
        
        # File manager UI (in main window)
        self.file_ui = FileManagerUI(self.root, self.file_service)
        
        # File handler
        self.file_handler = FileHandler(self.file_service, self.file_ui)
        
        # Toolbar (after menu bar)
        self.toolbar = Toolbar(self.root)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Setup toolbar commands
        self._setup_toolbar()

    
    def _setup_toolbar(self):
        """Setup toolbar button commands"""
        if not self.toolbar:
            return
        
        # New Chat button - opens chat window
        self.toolbar.set_command('new', self._show_chat)
        
        # File Manager button - refresh current file manager
        self.toolbar.set_command('file', self._refresh_file_manager)
        
        # Settings button - show model management
        self.toolbar.set_command('settings', self._show_model_management)
        
        # Models button - show model management
        self.toolbar.set_command('models', self._show_model_management)
        
        # Refresh button - refresh file manager
        self.toolbar.set_command('refresh', self._refresh_file_manager)
    
    def _show_chat(self):
        """Show chat window"""
        if not self.api_client:
            self.api_client = OllamaClient(self.config.api_url)
        
        # Create or show chat window
        self.chat_window = ChatWindow(self.root, self.api_client)
    
    def _refresh_file_manager(self):
        """Refresh file manager"""
        if self.file_ui:
            self.file_ui.refresh()

    def _create_menu_bar(self):
        """Create menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Chat", command=self._show_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Model Management", command=self._show_model_management)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self._refresh_file_manager)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_help)

    def _show_model_management(self):
        """Show model management window"""
        if not self.api_client:
            self.api_client = OllamaClient(self.config.api_url)
        
        from internal.chat.model_manager import ModelManager
        model_manager = ModelManager(self.root, self.api_client)
        model_manager.show_window()

    def _show_help(self):
        """Show help dialog with GitHub link"""
        # Create a custom dialog window
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Center the window
        screen_width = about_window.winfo_screenwidth()
        screen_height = about_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        about_window.geometry(f"400x300+{x}+{y}")
        
        # Content frame
        content_frame = ttk.Frame(about_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            content_frame,
            text="Assistant",
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = ttk.Label(
            content_frame,
            text="Version: 0.1.0"
        )
        version_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(
            content_frame,
            text="Multi-functional assistant application\nwith file management and chat capabilities",
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20))
        
        # GitHub link
        github_frame = ttk.Frame(content_frame)
        github_frame.pack(pady=(0, 20))
        
        ttk.Label(github_frame, text="GitHub: ").pack(side=tk.LEFT)
        
        github_link = tk.Label(
            github_frame,
            text="https://github.com/shangyanjin/assistant",
            fg="blue",
            cursor="hand2",
            font=("TkDefaultFont", 9)
        )
        github_link.pack(side=tk.LEFT)
        github_link.bind(
            "<Button-1>",
            lambda e: webbrowser.open("https://github.com/shangyanjin/assistant")
        )
        
        # Shortcuts
        shortcuts_label = ttk.Label(
            content_frame,
            text="Shortcuts:\n<Enter>: Send message\n<Shift+Enter>: New line",
            justify=tk.LEFT
        )
        shortcuts_label.pack(pady=(0, 20))
        
        # Close button
        close_button = ttk.Button(
            content_frame,
            text="Close",
            command=about_window.destroy
        )
        close_button.pack()

    def _check_system(self):
        """Check system compatibility"""
        if self.root:
            message = check_system_compatibility(self.root)
            if message:
                messagebox.showwarning("Warning", message, parent=self.root)

    def run(self):
        """Run application"""
        self._check_tkinter()
        self._create_window()
        self._setup_components()
        
        # Check system compatibility after a short delay
        if self.root:
            self.root.after(200, self._check_system)
        
        # Start main loop
        if self.root:
            self.root.mainloop()


def create_app() -> App:
    """Create and return application instance"""
    return App()

