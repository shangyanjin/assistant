"""
File manager UI components
"""
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import List, Optional
from internal.file.service import FileService


class FileManagerUI:
    """File manager UI components"""
    
    def __init__(self, parent: tk.Tk, service: FileService):
        """
        Initialize file manager UI
        
        Args:
            parent: Parent window (Tk for main window, Toplevel for popup)
            service: File service instance
        """
        self.parent = parent
        self.service = service
        self.treeview: Optional[ttk.Treeview] = None
        self.path_label: Optional[ttk.Label] = None
        self.search_entry: Optional[ttk.Entry] = None
        self.handler = None
        self.window = None
        
        self._create_window()
        self._create_ui()
        self.refresh()

    def _create_window(self):
        """Create file manager window"""
        # If parent is Tk (main window), use it directly
        if isinstance(self.parent, tk.Tk):
            self.window = self.parent
            self.window.title("Assistant - File Manager")
        else:
            # If parent is Toplevel, create new window
            self.window = tk.Toplevel(self.parent)
            self.window.title("File Manager")
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f"900x600+{(screen_width - 900) // 2}+{(screen_height - 600) // 2}")
        
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(3, weight=1)  # File list expands

    def _create_ui(self):
        """Create UI components"""
        # Header frame with navigation (row 2 after menu and toolbar)
        header_frame = ttk.Frame(self.window)
        header_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(2, weight=1)

        # Back button
        back_btn = ttk.Button(header_frame, text="◀", width=3)
        back_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Forward button
        forward_btn = ttk.Button(header_frame, text="▶", width=3)
        forward_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Path label
        self.path_label = ttk.Label(header_frame, text="", font=("TkDefaultFont", 10, "bold"))
        self.path_label.grid(row=0, column=2, sticky="ew", padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(header_frame, text="🔄", width=3)
        refresh_btn.grid(row=0, column=3, padx=(5, 0))
        
        # Search entry
        self.search_entry = ttk.Entry(header_frame, width=25)
        self.search_entry.insert(0, "Search files...")
        self.search_entry.grid(row=0, column=4, padx=(5, 0))
        
        # Bind search
        self.search_entry.bind("<Button-1>", lambda e: self._clear_search_placeholder())
        self.search_entry.bind("<FocusOut>", lambda e: self._restore_search_placeholder())
        self.search_entry.bind("<Return>", lambda e: self._on_search())
        
        # Main content frame with paned window (row 3 after header)
        content_frame = ttk.Frame(self.window)
        content_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # PanedWindow for resizable left/right split
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky="nsew")
        
        # Left panel: Directory tree
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        
        # Directory tree scrollbar
        tree_scrollbar = ttk.Scrollbar(left_frame, orient="vertical")
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Directory tree
        self.dir_tree = ttk.Treeview(
            left_frame,
            show="tree",
            yscrollcommand=tree_scrollbar.set
        )
        self.dir_tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar.config(command=self.dir_tree.yview)
        
        # Bind tree events
        self.dir_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.dir_tree.bind("<<TreeviewOpen>>", self._on_tree_expand)
        
        # Right panel: File list
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        
        # File list scrollbar
        list_scrollbar = ttk.Scrollbar(right_frame, orient="vertical")
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # File list treeview
        self.treeview = ttk.Treeview(
            right_frame,
            columns=("Name", "Date Modified", "Type", "Size"),
            yscrollcommand=list_scrollbar.set,
            show="headings",
            height=20
        )
        self.treeview.grid(row=0, column=0, sticky="nsew")
        list_scrollbar.config(command=self.treeview.yview)

        # Configure columns (no #0 column for file list)
        self.treeview.column("Name", width=200, anchor="w")
        self.treeview.column("Date Modified", width=150, anchor="center")
        self.treeview.column("Type", width=120, anchor="center")
        self.treeview.column("Size", width=100, anchor="center")

        # Configure headings (no #0 heading for file list)
        self.treeview.heading("Name", text="Name")
        self.treeview.heading("Date Modified", text="Date Modified")
        self.treeview.heading("Type", text="Type")
        self.treeview.heading("Size", text="Size")

        # Footer frame (row 4 after content)
        footer_frame = ttk.Frame(self.window)
        footer_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.footer_label = ttk.Label(footer_frame, text="")
        self.footer_label.pack(side="left")

        # Store button references for handler
        self.back_btn = back_btn
        self.forward_btn = forward_btn
        self.refresh_btn = refresh_btn
        
        # Create context menu
        self._create_context_menu()
    
    def _clear_search_placeholder(self):
        """Clear search placeholder"""
        if self.search_entry and self.search_entry.get() == "Search files...":
            self.search_entry.delete(0, "end")
    
    def _restore_search_placeholder(self):
        """Restore search placeholder if empty"""
        if self.search_entry and not self.search_entry.get():
            self.search_entry.insert(0, "Search files...")
    
    def _on_search(self):
        """Handle search"""
        if not self.search_entry:
            return
        query = self.search_entry.get()
        if query and query != "Search files...":
            if self.handler:
                self.handler.on_search(query)
        else:
            if self.handler:
                self.handler.on_search("")

    def _build_directory_tree(self, parent="", path=""):
        """Build directory tree - add subdirectories to parent node"""
        if not path:
            path = self.service.get_current_path()
        
        try:
            # Check if path exists and is a directory
            if not os.path.isdir(path):
                return
            
            items = os.listdir(path)
            dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
            dirs.sort()
            
            for dir_name in dirs:
                dir_path = os.path.join(path, dir_name)
                try:
                    # Check if we can access this directory
                    if os.path.isdir(dir_path):
                        item_id = self.dir_tree.insert(
                            parent, "end", text=dir_name, values=(dir_path,), open=False
                        )
                        # Always add a dummy child to make it expandable (lazy loading)
                        # This allows the tree to show the expand icon
                        self.dir_tree.insert(item_id, "end", text="")
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError) as e:
            pass
    
    def _on_tree_select(self, event):
        """Handle directory tree selection"""
        selection = self.dir_tree.selection()
        if selection:
            item = self.dir_tree.item(selection[0])
            values = item.get("values", [])
            if values and values[0]:
                dir_path = values[0]
                if os.path.isdir(dir_path):
                    if self.handler:
                        self.handler.on_tree_navigate(dir_path)
    
    def _on_tree_expand(self, event):
        """Handle directory tree expand"""
        # Get the item that was expanded
        item_id = event.widget.focus()
        if not item_id:
            # Try to get from selection
            selection = event.widget.selection()
            if selection:
                item_id = selection[0]
        
        if item_id:
            # Check if this item already has real children (not just dummy)
            children = self.dir_tree.get_children(item_id)
            has_real_children = False
            for child in children:
                if self.dir_tree.item(child).get("values"):
                    has_real_children = True
                    break
            
            # Only build if we don't have real children yet
            if not has_real_children:
                # Remove dummy children
                for child in children:
                    if not self.dir_tree.item(child).get("values"):
                        self.dir_tree.delete(child)
                
                # Add real children
                item = self.dir_tree.item(item_id)
                values = item.get("values", [])
                if values and values[0]:
                    dir_path = values[0]
                    self._build_directory_tree(parent=item_id, path=dir_path)
    
    def _expand_to_path(self, target_path):
        """Expand tree to show target path"""
        if not self.dir_tree:
            return
        
        # Normalize paths
        if os.name == 'nt':  # Windows
            target_path = os.path.normpath(target_path)
            parts = target_path.split(os.sep)
            if parts[0].endswith(':'):
                parts[0] = parts[0] + '\\'
        else:  # Unix/Linux
            parts = target_path.split(os.sep)
            if parts[0] == '':
                parts[0] = '/'
        
        # Find and expand path
        current_items = self.dir_tree.get_children()
        current_path = ""
        
        for part in parts:
            if not part:
                continue
            
            found = False
            for item_id in current_items:
                item = self.dir_tree.item(item_id)
                if item.get("text") == part:
                    # Expand this item
                    self.dir_tree.item(item_id, open=True)
                    # Check if children need to be built
                    children = self.dir_tree.get_children(item_id)
                    has_real_children = any(self.dir_tree.item(child).get("values") for child in children)
                    
                    if not has_real_children:
                        # Remove dummy children
                        for child in children:
                            if not self.dir_tree.item(child).get("values"):
                                self.dir_tree.delete(child)
                        # Build real children
                        values = item.get("values", [])
                        if values and values[0]:
                            dir_path = values[0]
                            self._build_directory_tree(parent=item_id, path=dir_path)
                    
                    current_items = self.dir_tree.get_children(item_id)
                    found = True
                    break
            
            if not found:
                break
    
    def refresh(self, filtered_items: Optional[List[str]] = None):
        """Refresh directory tree and file list"""
        # Refresh directory tree
        if self.dir_tree:
            # Clear existing tree
            for item in self.dir_tree.get_children():
                self.dir_tree.delete(item)
            
            # Build tree from root
            current_path = self.service.get_current_path()
            
            if os.name == 'nt':  # Windows
                # Get all drives
                import string
                drives = []
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        drives.append(drive)
                
                # Add each drive as root node
                for drive in drives:
                    drive_id = self.dir_tree.insert("", "end", text=drive, values=(drive,), open=False)
                    # Build immediate subdirectories for this drive (first level only)
                    self._build_directory_tree(parent=drive_id, path=drive)
                
                # Expand to current path
                self._expand_to_path(current_path)
            else:  # Unix/Linux
                # Add root node
                root_id = self.dir_tree.insert("", "end", text="/", values=("/",), open=False)
                # Build immediate subdirectories (first level only)
                self._build_directory_tree(parent=root_id, path="/")
                # Expand to current path
                self._expand_to_path(current_path)
        
        # Refresh file list
        if not self.treeview:
            return

        # Clear existing items
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Update path label
        if self.path_label:
            path = self.service.get_current_path()
            display_path = path.replace('\\', ' > ')
            self.path_label.config(text=display_path)

        # Get directory items
        if filtered_items:
            items = []
            for name in filtered_items:
                item_path = os.path.join(self.service.get_current_path(), name)
                try:
                    date_modified = os.path.getmtime(item_path)
                    date_str = datetime.fromtimestamp(date_modified).strftime("%d-%m-%Y %I:%M")
                    
                    if os.path.isdir(item_path):
                        file_type = "Directory"
                        size = ""
                        icon = "📁"
                    else:
                        ext = os.path.splitext(name)[1]
                        file_type = ext.upper()[1:] + " file" if ext else "Unknown file"
                        size_kb = round(os.stat(item_path).st_size / 1024)
                        size = f"{size_kb} KB"
                        icon = "📄"
                    
                    items.append((name, date_str, file_type, size, icon))
                except Exception:
                    continue
        else:
            items_data = self.service.list_directory()
            items = []
            for name, date_str, file_type, size in items_data:
                icon = "📁" if file_type == "Directory" else "📄"
                items.append((name, date_str, file_type, size, icon))

        # Insert items
        total_size = 0
        for name, date_str, file_type, size, icon in items:
            self.treeview.insert("", "end", values=(name, date_str, file_type, size))
            if size:
                try:
                    total_size += int(size.split()[0])
                except:
                    pass

        # Update footer
        if self.footer_label:
            self.footer_label.config(text=f"{len(items)} items | {round(total_size / 1024, 1)} MB Total")
        
        # Bind double-click
        if self.treeview and self.handler:
            self.treeview.bind("<Double-1>", lambda e: self.handler.on_double_click(e))

    def get_selected_item(self) -> Optional[str]:
        """Get selected item name"""
        if not self.treeview:
            return None
        selection = self.treeview.selection()
        if selection:
            item = self.treeview.item(selection[0])
            values = item.get("values", [])
            if values:
                return values[0]  # Name is first value
        return None

    def get_selected_item_from_event(self, event) -> Optional[str]:
        """Get selected item from click event"""
        if not self.treeview:
            return None
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            self.treeview.selection_set(item_id)
            item = self.treeview.item(item_id)
            values = item.get("values", [])
            if values:
                return values[0]
        return None
    
    def _create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Open", command=self._on_open)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="New File", command=self._on_new_file)
        self.context_menu.add_command(label="New Directory", command=self._on_new_dir)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy", command=self._on_copy)
        self.context_menu.add_command(label="Paste", command=self._on_paste)
        self.context_menu.add_command(label="Delete", command=self._on_delete)
        self.context_menu.add_command(label="Rename", command=self._on_rename)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Refresh", command=self._on_refresh)
        
        # Bind right-click
        if self.treeview:
            self.treeview.bind("<Button-3>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        if not self.treeview:
            return
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def _on_open(self):
        """Handle open from context menu"""
        if self.handler:
            self.handler.on_double_click()
    
    def _on_new_file(self):
        """Handle new file from context menu"""
        if self.handler:
            from tkinter.simpledialog import askstring
            name = askstring("New File", "Enter file name:", parent=self.window)
            if name:
                self.handler.on_create_file(name)
    
    def _on_new_dir(self):
        """Handle new directory from context menu"""
        if self.handler:
            from tkinter.simpledialog import askstring
            name = askstring("New Directory", "Enter directory name:", parent=self.window)
            if name:
                self.handler.on_create_directory(name)
    
    def _on_copy(self):
        """Handle copy from context menu"""
        if self.handler:
            selected = self.get_selected_item()
            if selected:
                self.handler.on_copy_item(selected)
    
    def _on_paste(self):
        """Handle paste from context menu"""
        if self.handler:
            self.handler.on_paste_item()
    
    def _on_delete(self):
        """Handle delete from context menu"""
        if self.handler:
            selected = self.get_selected_item()
            if selected:
                self.handler.on_delete_item(selected)
    
    def _on_rename(self):
        """Handle rename from context menu"""
        if self.handler:
            selected = self.get_selected_item()
            if selected:
                from tkinter.simpledialog import askstring
                new_name = askstring("Rename", f"Enter new name for '{selected}':", parent=self.window)
                if new_name:
                    self.handler.on_rename_item(selected, new_name)
    
    def _on_refresh(self):
        """Handle refresh from context menu"""
        if self.handler:
            self.handler.on_refresh()
    
    def set_handler(self, handler):
        """Set handler for events"""
        self.handler = handler

