"""
Chat handler - event handling
"""
import tkinter as tk
from typing import Optional
from threading import Thread
from internal.chat.service import ChatService
from internal.chat.ui import ChatUI


class ChatHandler:
    """Chat event handler"""
    
    def __init__(self, service: ChatService, ui: ChatUI):
        """
        Initialize chat handler
        
        Args:
            service: Chat service instance
            ui: Chat UI instance
        """
        self.service = service
        self.ui = ui
        self.is_generating = False

    def on_send(self, event=None):
        """Handle send button click or Enter key"""
        if self.is_generating:
            return

        message = self.ui.get_user_input()
        if not message:
            return

        model = self.ui.get_selected_model()
        if not model or model == "Waiting..." or "Error" in model:
            return

        # Clear input
        self.ui.clear_user_input()

        # Display user message
        self.ui.display_user_message(message)

        # Start generating response in background thread
        self.is_generating = True
        self.ui.set_generating(True)
        Thread(target=self._generate_response, args=(message, model), daemon=True).start()

    def _generate_response(self, message: str, model: str):
        """Generate AI response in background thread"""
        try:
            # Create response label first
            self.ui._create_message_label("")
            self.ui.display_model_name(model)
            response_content = ""
            
            for chunk in self.service.send_message(message, model):
                if not self.is_generating:
                    break
                response_content += chunk
                self.ui.append_response_chunk(chunk)
            
            # Add complete response to history
            if response_content:
                self.service.add_assistant_message(response_content)
            
            self.ui.append_newline()
        except Exception as e:
            self.ui.display_error(f"AI error: {e}")
        finally:
            self.is_generating = False
            self.ui.set_generating(False)

    def on_stop(self):
        """Handle stop button click"""
        self.is_generating = False
        self.ui.set_generating(False)

    def on_clear(self):
        """Handle clear chat"""
        self.service.clear_history()
        self.ui.clear_chat()

    def handle_key_press(self, event: tk.Event):
        """Handle keyboard events"""
        if event.keysym == "Return":
            if event.state & 0x1 == 0x1:  # Shift key pressed
                self.ui.insert_newline()
            else:
                self.on_send()
            return "break"

