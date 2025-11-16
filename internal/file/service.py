"""
File management service - business logic
"""
import os
import shutil
import subprocess
import platform
from datetime import datetime
from typing import List, Tuple, Optional


class FileService:
    """File management business logic service"""
    
    def __init__(self):
        """Initialize file service"""
        self.current_path = os.getcwd()
        self.last_directory = ""
        self.copied_path = ""  # Source path for copy/paste
        self.selected_item = ""

    def get_current_path(self) -> str:
        """Get current directory path"""
        return self.current_path

    def list_directory(self, path: Optional[str] = None) -> List[Tuple[str, str, str, str]]:
        """
        List directory contents
        
        Returns:
            List of tuples: (name, date_modified, file_type, size)
        """
        if path is None:
            path = self.current_path
        
        try:
            items = []
            for name in os.listdir(path):
                item_path = os.path.join(path, name)
                try:
                    # Date modified
                    date_modified = datetime.fromtimestamp(
                        os.path.getmtime(item_path)
                    ).strftime("%d-%m-%Y %I:%M")
                    
                    # File type
                    if os.path.isdir(item_path):
                        file_type = "Directory"
                        size = ""
                    else:
                        ext = os.path.splitext(name)[1]
                        if ext == "":
                            file_type = "Unknown file"
                        else:
                            file_type = ext.upper()[1:] + " file"
                        # Size in KB
                        size_kb = round(os.stat(item_path).st_size / 1024)
                        size = f"{size_kb} KB"
                    
                    items.append((name, date_modified, file_type, size))
                except Exception:
                    continue
            
            return items
        except Exception:
            return []

    def navigate_to(self, path: str) -> bool:
        """
        Navigate to directory
        
        Args:
            path: Directory path
            
        Returns:
            True if successful
        """
        try:
            if os.path.isdir(path):
                self.last_directory = self.current_path
                self.current_path = path
                os.chdir(path)
                return True
            return False
        except Exception:
            return False

    def navigate_to(self, path: str) -> bool:
        """Navigate to specified directory"""
        try:
            if os.path.isdir(path):
                self.last_directory = self.current_path
                self.current_path = path
                os.chdir(path)
                return True
            return False
        except Exception:
            return False
    
    def navigate_back(self) -> bool:
        """Navigate to parent directory"""
        try:
            parent = os.path.dirname(self.current_path)
            if parent != self.current_path:
                self.last_directory = self.current_path
                self.current_path = parent
                os.chdir(parent)
                return True
            return False
        except Exception:
            return False

    def navigate_forward(self) -> bool:
        """Navigate to last directory"""
        try:
            if self.last_directory and os.path.isdir(self.last_directory):
                self.current_path = self.last_directory
                os.chdir(self.last_directory)
                return True
            return False
        except Exception:
            return False

    def open_item(self, name: str) -> bool:
        """
        Open file or directory
        
        Args:
            name: Item name
            
        Returns:
            True if successful
        """
        try:
            item_path = os.path.join(self.current_path, name)
            if os.path.isdir(item_path):
                return self.navigate_to(item_path)
            else:
                # Open file with system default
                if platform.system() == "Windows":
                    os.startfile(item_path)
                elif platform.system() == "Linux":
                    subprocess.Popen(["xdg-open", item_path])
                return True
        except Exception:
            return False

    def create_file(self, name: str) -> bool:
        """Create new file"""
        try:
            file_path = os.path.join(self.current_path, name)
            with open(file_path, 'x'):
                pass
            return True
        except Exception:
            return False

    def create_directory(self, name: str) -> bool:
        """Create new directory"""
        try:
            dir_path = os.path.join(self.current_path, name)
            os.makedirs(dir_path, exist_ok=False)
            return True
        except Exception:
            return False

    def delete_item(self, name: str) -> bool:
        """Delete file or directory"""
        try:
            item_path = os.path.join(self.current_path, name)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
            return True
        except Exception:
            return False

    def rename_item(self, old_name: str, new_name: str) -> bool:
        """Rename file or directory"""
        try:
            old_path = os.path.join(self.current_path, old_name)
            new_path = os.path.join(self.current_path, new_name)
            os.rename(old_path, new_path)
            return True
        except Exception:
            return False

    def copy_item(self, name: str):
        """Copy item (store source path)"""
        self.copied_path = os.path.join(self.current_path, name)

    def paste_item(self) -> bool:
        """Paste copied item to current directory"""
        if not self.copied_path:
            return False
        
        try:
            dest = self.current_path
            if os.path.isfile(self.copied_path):
                shutil.copy2(self.copied_path, dest)
            elif os.path.isdir(self.copied_path):
                new_dest = os.path.join(dest, os.path.basename(self.copied_path))
                shutil.copytree(self.copied_path, new_dest, dirs_exist_ok=True)
            return True
        except Exception:
            return False

    def search_files(self, query: str) -> List[str]:
        """
        Search files in current directory
        
        Args:
            query: Search query
            
        Returns:
            List of matching file/directory names
        """
        try:
            items = os.listdir(self.current_path)
            query_lower = query.lower()
            matches = [name for name in items if query_lower in name.lower()]
            return matches
        except Exception:
            return []

    def get_available_drives(self) -> List[str]:
        """Get available drives (Windows)"""
        if platform.system() == "Windows":
            drives = [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]
            return drives
        else:
            return ["/"]

