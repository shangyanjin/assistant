"""
Chat UI components
"""
import platform
import tkinter as tk
from tkinter import ttk, font
from typing import List


class ChatUI:
    """Chat UI components"""
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize chat UI
        
        Args:
            parent: Parent window
        """
        self.root = parent
        self.default_font = font.nametofont("TkTextFont").actual()["family"]
        self.label_widgets: List[tk.Label] = []
        
        # UI components
        self.chat_box: tk.Text = None
        self.user_input: tk.Text = None
        self.send_button: ttk.Button = None
        self.progress: ttk.Progressbar = None
        self.stop_button: ttk.Button = None
        self.model_select: ttk.Combobox = None
        
        self._create_ui()

    def _create_ui(self):
        """Create chat UI components"""
        # Chat container
        chat_frame = ttk.Frame(self.root)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)

        # Chat box
        self.chat_box = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=(self.default_font, 12),
            spacing1=5,
            highlightthickness=0,
        )
        self.chat_box.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_box.configure(yscrollcommand=scrollbar.set)

        # Configure text tags
        self.chat_box.tag_configure("Bold", foreground="#ff007b", font=(self.default_font, 10, "bold"))
        self.chat_box.tag_configure("Error", foreground="red")
        self.chat_box.tag_configure("Right", justify="right")

        # Bind resize event
        self.chat_box.bind("<Configure>", self._resize_labels)

    def _resize_labels(self, event: tk.Event):
        """Resize label widgets when chat box is resized"""
        for label in self.label_widgets:
            current_width = event.widget.winfo_width()
            max_width = int(current_width) * 0.7
            label.config(wraplength=max_width)

    def display_user_message(self, message: str):
        """Display user message"""
        self._create_message_label(message, on_right_side=True)
        self._append_text(f"\n\n")

    def display_model_name(self, model: str):
        """Display model name"""
        self._append_text(f"{model}\n", ("Bold",))

    def append_response_chunk(self, chunk: str):
        """Append response chunk"""
        if self.label_widgets:
            current_label = self.label_widgets[-1]
            current_label.config(text=current_label.cget("text") + chunk)
        else:
            self._create_message_label("")
            self.label_widgets[-1].config(text=chunk)

    def _create_message_label(self, text: str, on_right_side: bool = False):
        """Create a message label"""
        background = "#48a4f2" if on_right_side else "#eaeaea"
        foreground = "white" if on_right_side else "black"
        max_width = int(self.chat_box.winfo_reqwidth()) * 0.7 if self.chat_box.winfo_reqwidth() > 0 else 500
        
        label = tk.Label(
            self.chat_box,
            justify=tk.LEFT,
            wraplength=max_width,
            background=background,
            highlightthickness=0,
            highlightbackground=background,
            foreground=foreground,
            padx=8,
            pady=8,
            font=(self.default_font, 12),
            borderwidth=0,
        )
        label.config(text=text)
        self.label_widgets.append(label)
        
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.window_create(tk.END, window=label)
        self.chat_box.config(state=tk.DISABLED)
        
        if on_right_side:
            idx = self.chat_box.index("end-1c").split(".")[0]
            self.chat_box.tag_add("Right", f"{idx}.0", f"{idx}.end")

    def _append_text(self, text: str, tags=()):
        """Append text to chat box"""
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, text, tags)
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def append_newline(self):
        """Append newline"""
        self._append_text("\n\n")

    def display_error(self, error: str):
        """Display error message"""
        self._append_text(f"\n{error}\n\n", ("Error",))

    def clear_chat(self):
        """Clear chat display"""
        for label in self.label_widgets:
            label.destroy()
        self.label_widgets.clear()
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.delete(1.0, tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def get_user_input(self) -> str:
        """Get user input text"""
        if self.user_input:
            return self.user_input.get("1.0", "end-1c").strip()
        return ""

    def clear_user_input(self):
        """Clear user input"""
        if self.user_input:
            self.user_input.delete("1.0", "end")

    def insert_newline(self):
        """Insert newline in user input"""
        if self.user_input:
            self.user_input.insert("end", "\n")

    def get_selected_model(self) -> str:
        """Get selected model name"""
        if self.model_select:
            return self.model_select.get()
        return ""

    def set_generating(self, generating: bool):
        """Set generating state"""
        if generating:
            if self.progress:
                self.progress.grid(row=0, column=0, sticky="nsew")
                self.progress.start(5)
            if self.stop_button:
                self.stop_button.grid(row=0, column=1, padx=20)
            if self.send_button:
                self.send_button.state(["disabled"])
        else:
            if self.progress:
                self.progress.stop()
                self.progress.grid_remove()
            if self.stop_button:
                self.stop_button.grid_remove()
            if self.send_button:
                self.send_button.state(["!disabled"])
    
    def set_progress_frame(self, progress_frame):
        """Set progress frame reference"""
        if progress_frame:
            self.progress = progress_frame.progress
            self.stop_button = progress_frame.stop_button

