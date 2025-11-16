"""
File management handler - event handling
"""
import tkinter as tk
from tkinter import messagebox
from internal.file.service import FileService
from internal.file.ui import FileManagerUI


class FileHandler:
    """File management event handler"""
    
    def __init__(self, service: FileService, ui: FileManagerUI):
        """
        Initialize file handler
        
        Args:
            service: File service instance
            ui: File manager UI instance
        """
        self.service = service
        self.ui = ui
        self.ui.set_handler(self)
        
        # Connect UI events
        if self.ui.back_btn:
            self.ui.back_btn.config(command=self.on_navigate_back)
        if self.ui.forward_btn:
            self.ui.forward_btn.config(command=self.on_navigate_forward)
        if self.ui.refresh_btn:
            self.ui.refresh_btn.config(command=self.on_refresh)

    def on_double_click(self, event=None):
        """Handle double click on file/directory"""
        selected = self.ui.get_selected_item()
        if selected:
            if self.service.open_item(selected):
                self.ui.refresh()

    def on_navigate_back(self):
        """Handle back button"""
        if self.service.navigate_back():
            self.ui.refresh()

    def on_navigate_forward(self):
        """Handle forward button"""
        if self.service.navigate_forward():
            self.ui.refresh()

    def on_refresh(self):
        """Handle refresh button"""
        self.ui.refresh()

    def on_search(self, query: str):
        """Handle search"""
        if query:
            matches = self.service.search_files(query)
            self.ui.refresh(matches)
        else:
            self.ui.refresh()
    
    def on_tree_navigate(self, dir_path: str):
        """Handle directory tree navigation"""
        if self.service.navigate_to(dir_path):
            self.ui.refresh()

    def on_create_file(self, name: str) -> bool:
        """Handle create file"""
        if not name:
            return False
        if self.service.create_file(name):
            self.ui.refresh()
            return True
        return False

    def on_create_directory(self, name: str) -> bool:
        """Handle create directory"""
        if not name:
            return False
        if self.service.create_directory(name):
            self.ui.refresh()
            return True
        return False

    def on_delete_item(self, name: str) -> bool:
        """Handle delete item"""
        if not name:
            return False
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?\nThis action cannot be undone.",
            parent=self.ui.window
        )
        
        if result:
            if self.service.delete_item(name):
                self.ui.refresh()
                return True
        return False

    def on_rename_item(self, old_name: str, new_name: str) -> bool:
        """Handle rename item"""
        if not old_name or not new_name:
            return False
        if self.service.rename_item(old_name, new_name):
            self.ui.refresh()
            return True
        return False

    def on_copy_item(self, name: str):
        """Handle copy item"""
        if name:
            self.service.copy_item(name)

    def on_paste_item(self):
        """Handle paste item"""
        if self.service.paste_item():
            self.ui.refresh()

    def on_select_item(self, event):
        """Handle item selection"""
        selected = self.ui.get_selected_item_from_event(event)
        if selected:
            self.service.selected_item = selected

