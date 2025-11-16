"""
Model management window
"""
import tkinter as tk
from tkinter import ttk
import webbrowser
from threading import Thread
from typing import Optional
from pkg.api.ollama import OllamaClient


class ModelManager:
    """Model management window"""
    
    def __init__(self, parent: tk.Tk, api_client: OllamaClient):
        """
        Initialize model manager
        
        Args:
            parent: Parent window
            api_client: Ollama API client
        """
        self.parent = parent
        self.api_client = api_client
        self.management_window: Optional[tk.Toplevel] = None
        self.models_list: Optional[tk.Listbox] = None
        self.log_textbox: Optional[tk.Text] = None
        self.download_button: Optional[ttk.Button] = None
        self.delete_button: Optional[ttk.Button] = None

    def show_window(self):
        """Show model management window"""
        if self.management_window and self.management_window.winfo_exists():
            self.management_window.lift()
            return

        # Update API client host if needed
        # (This would be called from the app when host changes)

        # Create window
        self.management_window = tk.Toplevel(self.parent)
        self.management_window.title("Model Management")
        
        screen_width = self.management_window.winfo_screenwidth()
        screen_height = self.management_window.winfo_screenheight()
        x = int((screen_width / 2) - (400 / 2))
        y = int((screen_height / 2) - (500 / 2))
        self.management_window.geometry(f"{400}x{500}+{x}+{y}")

        self.management_window.grid_columnconfigure(0, weight=1)
        self.management_window.grid_rowconfigure(3, weight=1)

        self._create_download_section()
        self._create_model_list()
        self._create_log_section()

        # Update model list
        Thread(target=self._update_model_list, daemon=True).start()

    def _create_download_section(self):
        """Create download section"""
        frame = ttk.Frame(self.management_window)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)

        model_name_input = ttk.Entry(frame)
        model_name_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        def _download():
            arg = model_name_input.get().strip()
            if arg.startswith("ollama run "):
                arg = arg[11:]
            if arg:
                Thread(target=self._download_model, daemon=True, args=(arg,)).start()

        self.download_button = ttk.Button(frame, text="Download", command=_download)
        self.download_button.grid(row=0, column=1, sticky="ew")

        tips = tk.Label(
            frame,
            text="find models: https://ollama.com/library",
            fg="blue",
            cursor="hand2",
        )
        tips.bind("<Button-1>", lambda e: webbrowser.open("https://ollama.com/library"))
        tips.grid(row=1, column=0, sticky="W", padx=(0, 5), pady=5)

    def _create_model_list(self):
        """Create model list section"""
        list_action_frame = ttk.Frame(self.management_window)
        list_action_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_action_frame.grid_columnconfigure(0, weight=1)
        list_action_frame.grid_rowconfigure(0, weight=1)

        self.models_list = tk.Listbox(list_action_frame)
        self.models_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            list_action_frame, orient="vertical", command=self.models_list.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.models_list.config(yscrollcommand=scrollbar.set)

        def _delete():
            selection = self.models_list.curselection()
            if selection:
                model_name = self.models_list.get(selection[0]).strip()
                Thread(target=self._delete_model, daemon=True, args=(model_name,)).start()

        self.delete_button = ttk.Button(list_action_frame, text="Delete", command=_delete)
        self.delete_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))

    def _create_log_section(self):
        """Create log section"""
        self.log_textbox = tk.Text(self.management_window)
        self.log_textbox.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_textbox.config(state="disabled")

    def _append_log(self, message: str, clear: bool = False):
        """Append log message"""
        if self.log_textbox and self.log_textbox.winfo_exists():
            self.log_textbox.config(state=tk.NORMAL)
            if clear:
                self.log_textbox.delete(1.0, tk.END)
            if message:
                self.log_textbox.insert(tk.END, message + "\n")
            self.log_textbox.config(state=tk.DISABLED)
            self.log_textbox.see(tk.END)

    def _update_model_list(self):
        """Update model list in background thread"""
        try:
            models = self.api_client.fetch_models()
            if self.models_list and self.models_list.winfo_exists():
                self.management_window.after(0, lambda: self._refresh_model_list(models))
        except Exception:
            if self.management_window:
                self.management_window.after(0, lambda: self._append_log("Error! Please check the Ollama host."))

    def _refresh_model_list(self, models: list):
        """Refresh model list UI"""
        if self.models_list:
            self.models_list.delete(0, tk.END)
            for model in models:
                self.models_list.insert(tk.END, model)

    def _download_model(self, model_name: str):
        """Download model in background thread"""
        if not model_name:
            return

        if self.download_button:
            self.management_window.after(0, lambda: self.download_button.state(["disabled"]))
        
        self.management_window.after(0, lambda: self._append_log("", clear=True))

        try:
            for log_msg in self.api_client.download_model(model_name):
                self.management_window.after(0, lambda msg=log_msg: self._append_log(msg))
        except Exception as e:
            self.management_window.after(0, lambda: self._append_log(f"Failed to download model: {e}"))
        finally:
            self._update_model_list()
            if self.download_button:
                self.management_window.after(0, lambda: self.download_button.state(["!disabled"]))

    def _delete_model(self, model_name: str):
        """Delete model in background thread"""
        if not model_name:
            return

        self.management_window.after(0, lambda: self._append_log("", clear=True))

        try:
            success = self.api_client.delete_model(model_name)
            if success:
                self.management_window.after(0, lambda: self._append_log("Model deleted successfully."))
            else:
                self.management_window.after(0, lambda: self._append_log("Model not found."))
        except Exception as e:
            self.management_window.after(0, lambda: self._append_log(f"Failed to delete model: {e}"))
        finally:
            self._update_model_list()

