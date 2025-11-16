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
from internal.chat.service import ChatService
from internal.chat.handler import ChatHandler
from internal.chat.ui import ChatUI
from internal.chat.model_manager import ModelManager
from internal.ui.components import HeaderFrame, InputFrame, ProgressFrame
from threading import Thread


class App:
    """Main application class"""
    
    def __init__(self):
        """Initialize application"""
        self.config = AppConfig()
        self.root: Optional[tk.Tk] = None
        self.api_client: Optional[OllamaClient] = None
        self.chat_service: Optional[ChatService] = None
        self.chat_ui: Optional[ChatUI] = None
        self.chat_handler: Optional[ChatHandler] = None
        self.header: Optional[HeaderFrame] = None
        self.input_frame: Optional[InputFrame] = None
        self.progress_frame: Optional[ProgressFrame] = None
        self.model_manager: Optional[ModelManager] = None
        self.menubar: Optional[tk.Menu] = None

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
        """Create main window"""
        self.root = tk.Tk()
        self.root.title("Assistant")
        
        # Set window size and position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"800x600+{(screen_width - 800) // 2}+{(screen_height - 600) // 2}")
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)

    def _setup_components(self):
        """Setup application components"""
        # API client
        self.api_client = OllamaClient(self.config.api_url)
        
        # Model manager
        self.model_manager = ModelManager(self.root, self.api_client)
        
        # Header frame
        self.header = HeaderFrame(self.root, settings_callback=self._show_model_management)
        
        # Progress frame
        self.progress_frame = ProgressFrame(self.root)
        
        # Input frame
        self.input_frame = InputFrame(self.root)
        
        # Chat service
        self.chat_service = ChatService(self.api_client)
        
        # Chat UI
        self.chat_ui = ChatUI(self.root)
        
        # Connect UI components
        self._connect_ui_components()
        
        # Chat handler
        self.chat_handler = ChatHandler(self.chat_service, self.chat_ui)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Refresh models
        self._refresh_models()

    def _connect_ui_components(self):
        """Connect UI components"""
        # Connect input frame to chat UI
        if self.input_frame and self.chat_ui:
            self.chat_ui.user_input = self.input_frame.user_input
            self.chat_ui.send_button = self.input_frame.send_button
        
        # Connect progress frame to chat UI
        if self.progress_frame and self.chat_ui:
            self.chat_ui.set_progress_frame(self.progress_frame)
        
        # Connect header to chat UI
        if self.header and self.chat_ui:
            self.chat_ui.model_select = self.header.model_select

    def _connect_events(self):
        """Connect UI events to handlers"""
        # Note: handler needs to be created first, so this is called after handler creation
        pass
    
    def _setup_event_handlers(self):
        """Setup event handlers after handler is created"""
        # User input key binding
        if self.input_frame and self.input_frame.user_input and self.chat_handler:
            self.input_frame.user_input.bind("<Key>", self.chat_handler.handle_key_press)
        
        # Send button
        if self.input_frame and self.input_frame.send_button and self.chat_handler:
            self.input_frame.send_button.config(command=self.chat_handler.on_send)
        
        # Stop button
        if self.progress_frame and self.progress_frame.stop_button and self.chat_handler:
            self.progress_frame.stop_button.config(command=self.chat_handler.on_stop)
        
        # Refresh button
        if self.header and self.header.refresh_button:
            self.header.refresh_button.config(command=self._refresh_models)
        
        # Host input change
        if self.header and self.header.host_input:
            self.header.host_input.bind("<Return>", lambda e: self._update_host())

    def _update_host(self):
        """Update API client host"""
        if self.header and self.api_client:
            new_host = self.header.get_host()
            self.api_client.api_url = new_host
            if self.model_manager:
                self.model_manager.api_client.api_url = new_host
            self._refresh_models()

    def _refresh_models(self):
        """Refresh model list"""
        if not self.header or not self.api_client:
            return
        
        def update_models():
            try:
                models = self.api_client.fetch_models()
                if models:
                    self.root.after(0, lambda: self.header.set_models(models))
                    if self.input_frame:
                        self.root.after(0, lambda: self.input_frame.send_button.state(["!disabled"]))
                else:
                    self.root.after(0, lambda: self.header.model_select.set("No models available"))
            except Exception:
                self.root.after(0, lambda: self.header.model_select.set("Error! Check host."))
        
        Thread(target=update_models, daemon=True).start()

    def _create_menu_bar(self):
        """Create menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Model Management", command=self._show_model_management)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy All", command=self._copy_all)
        edit_menu.add_command(label="Clear Chat", command=self._clear_chat)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_help)

    def _show_model_management(self):
        """Show model management window"""
        if self.model_manager:
            # Update API client host before showing
            if self.header:
                self.model_manager.api_client.api_url = self.header.get_host()
            self.model_manager.show_window()

    def _copy_all(self):
        """Copy all chat history"""
        if self.chat_service:
            import pprint
            history = self.chat_service.get_history()
            if history:
                text = pprint.pformat([msg.to_dict() for msg in history])
                self.root.clipboard_clear()
                self.root.clipboard_append(text)

    def _clear_chat(self):
        """Clear chat"""
        if self.chat_handler:
            self.chat_handler.on_clear()

    def _show_help(self):
        """Show help dialog"""
        info = (
            "Project: Assistant\n"
            "Version: 0.1.0\n"
            "Multi-functional assistant application\n\n"
            "Shortcuts:\n"
            "<Enter>: Send message\n"
            "<Shift+Enter>: New line\n"
        )
        messagebox.showinfo("About", info, parent=self.root)

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

