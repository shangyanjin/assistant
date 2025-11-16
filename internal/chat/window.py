"""
Chat window - independent window
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from threading import Thread
from pkg.api.ollama import OllamaClient
from pkg.utils.system import check_system_compatibility
from internal.model.config import AppConfig
from internal.chat.service import ChatService
from internal.chat.handler import ChatHandler
from internal.chat.ui import ChatUI
from internal.chat.model_manager import ModelManager
from internal.ui.components import HeaderFrame, InputFrame, ProgressFrame


class ChatWindow:
    """Independent chat window"""
    
    _instances = {}  # Track open windows by parent
    
    def __init__(self, parent: tk.Tk, api_client: OllamaClient):
        """
        Initialize chat window
        
        Args:
            parent: Parent window
            api_client: Ollama API client
        """
        # Check if window already exists for this parent
        if parent in ChatWindow._instances:
            existing = ChatWindow._instances[parent]
            if existing.window.winfo_exists():
                existing.window.lift()
                return
        
        self.window = tk.Toplevel(parent)
        self.api_client = api_client
        self.chat_service: Optional[ChatService] = None
        self.chat_ui: Optional[ChatUI] = None
        self.chat_handler: Optional[ChatHandler] = None
        self.header: Optional[HeaderFrame] = None
        self.input_frame: Optional[InputFrame] = None
        self.progress_frame: Optional[ProgressFrame] = None
        self.model_manager: Optional[ModelManager] = None
        
        # Store instance
        ChatWindow._instances[parent] = self
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._create_window()
        self._setup_components()
    
    def _on_close(self):
        """Handle window close"""
        if self.window.winfo_exists():
            # Remove from instances
            for key, instance in list(ChatWindow._instances.items()):
                if instance == self:
                    del ChatWindow._instances[key]
                    break
            self.window.destroy()
    
    def _create_window(self):
        """Create chat window"""
        self.window.title("Chat")
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"800x600+{(screen_width - 800) // 2}+{(screen_height - 600) // 2}")
        
        # Configure grid
        # Row 0: Header frame
        # Row 1: Chat UI
        # Row 2: Progress frame
        # Row 3: Input frame
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)  # Chat UI expands
        self.window.grid_rowconfigure(2, weight=0)  # Progress frame
        self.window.grid_rowconfigure(3, weight=0)  # Input frame
    
    def _setup_components(self):
        """Setup chat components"""
        # Model manager
        self.model_manager = ModelManager(self.window, self.api_client)
        
        # Header frame
        self.header = HeaderFrame(self.window, settings_callback=self._show_model_management)
        
        # Progress frame
        self.progress_frame = ProgressFrame(self.window)
        
        # Input frame
        self.input_frame = InputFrame(self.window)
        
        # Chat service
        self.chat_service = ChatService(self.api_client)
        
        # Chat UI
        self.chat_ui = ChatUI(self.window)
        
        # Connect UI components
        self._connect_ui_components()
        
        # Chat handler
        self.chat_handler = ChatHandler(self.chat_service, self.chat_ui)
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Refresh models
        self._refresh_models()
        
        # Check system compatibility
        self.window.after(200, self._check_system)
    
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
    
    def _setup_event_handlers(self):
        """Setup event handlers"""
        # User input key binding
        if self.input_frame and self.input_frame.user_input and self.chat_handler:
            self.input_frame.user_input.bind("<Key>", self.chat_handler.handle_key_press)
        
        # Send button
        if self.input_frame and self.input_frame.send_button and self.chat_handler:
            self.input_frame.send_button.config(command=self.chat_handler.on_send)
        
        # Stop button
        if self.progress_frame and self.progress_frame.stop_button and self.chat_handler:
            self.progress_frame.stop_button.config(command=self.chat_handler.on_stop)
        
        # Refresh button (header)
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
                    self.window.after(0, lambda: self.header.set_models(models))
                    if self.input_frame:
                        self.window.after(0, lambda: self.input_frame.send_button.state(["!disabled"]))
                else:
                    self.window.after(0, lambda: self.header.model_select.set("No models available"))
            except Exception:
                self.window.after(0, lambda: self.header.model_select.set("Error! Check host."))
        
        Thread(target=update_models, daemon=True).start()
    
    def _show_model_management(self):
        """Show model management window"""
        if self.model_manager:
            # Update API client host before showing
            if self.header:
                self.model_manager.api_client.api_url = self.header.get_host()
            self.model_manager.show_window()
    
    def _check_system(self):
        """Check system compatibility"""
        from pkg.utils.system import check_system_compatibility
        if self.window:
            message = check_system_compatibility(self.window)
            if message:
                messagebox.showwarning("Warning", message, parent=self.window)

