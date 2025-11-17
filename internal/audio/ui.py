"""
Audio processor UI window
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from typing import Optional
from internal.audio.processor import AudioProcessor
from internal.audio.display import ProgressDisplay


class AudioProcessorWindow:
    """Audio processing window"""
    
    def __init__(self, parent: tk.Tk, initial_path: str = ""):
        """
        Initialize audio processor window
        
        Args:
            parent: Parent window
            initial_path: Initial directory path
        """
        self.parent = parent
        self.initial_path = initial_path
        self.processor: Optional[AudioProcessor] = None
        self.is_processing = False
        
        self._create_window()
        self._create_ui()
    
    def _create_window(self):
        """Create window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Audio File Batch Processor")
        self.window.geometry("800x600")
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        """Create UI components"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directory", padding=10)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_var = tk.StringVar(value=self.initial_path)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=60)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self._browse_directory)
        browse_btn.pack(side=tk.LEFT)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Fix encoding
        self.fix_encoding_var = tk.BooleanVar(value=True)
        fix_encoding_cb = ttk.Checkbutton(
            options_frame,
            text="Fix encoding issues (GBK/GB2312 -> UTF-8)",
            variable=self.fix_encoding_var
        )
        fix_encoding_cb.pack(anchor=tk.W, pady=2)
        
        # Auto album
        self.auto_album_var = tk.BooleanVar(value=True)
        auto_album_cb = ttk.Checkbutton(
            options_frame,
            text="Auto-detect album from directory name",
            variable=self.auto_album_var
        )
        auto_album_cb.pack(anchor=tk.W, pady=2)
        
        # Auto title
        self.auto_title_var = tk.BooleanVar(value=True)
        auto_title_cb = ttk.Checkbutton(
            options_frame,
            text="Auto-generate title with zero-padding (01, 02, ...)",
            variable=self.auto_title_var
        )
        auto_title_cb.pack(anchor=tk.W, pady=2)
        
        # Overwrite options
        overwrite_frame = ttk.Frame(options_frame)
        overwrite_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.overwrite_album_var = tk.BooleanVar(value=False)
        overwrite_album_cb = ttk.Checkbutton(
            overwrite_frame,
            text="Overwrite existing album",
            variable=self.overwrite_album_var
        )
        overwrite_album_cb.pack(side=tk.LEFT, padx=(20, 10))
        
        self.overwrite_title_var = tk.BooleanVar(value=False)
        overwrite_title_cb = ttk.Checkbutton(
            overwrite_frame,
            text="Overwrite existing title",
            variable=self.overwrite_title_var
        )
        overwrite_title_cb.pack(side=tk.LEFT)
        
        # Update tags
        self.update_tags_var = tk.BooleanVar(value=True)
        update_tags_cb = ttk.Checkbutton(
            options_frame,
            text="Update tags (write changes to files)",
            variable=self.update_tags_var
        )
        update_tags_cb.pack(anchor=tk.W, pady=2)
        
        # Format filename
        self.format_filename_var = tk.BooleanVar(value=False)
        format_filename_cb = ttk.Checkbutton(
            options_frame,
            text="Format filename (Number + Album Style, remove ads and decorations)",
            variable=self.format_filename_var
        )
        format_filename_cb.pack(anchor=tk.W, pady=2)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="Start Processing", command=self._start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self._stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Log output (scrolled text)
        log_label = ttk.Label(progress_frame, text="Processing Log:")
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            progress_frame,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)
    
    def _start_processing(self):
        """Start processing"""
        directory = self.dir_var.get().strip()
        
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("Error", "Please select a valid directory", parent=self.window)
            return
        
        # Disable start button, enable stop button
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_processing = True
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Get options
        options = {
            'fix_encoding': self.fix_encoding_var.get(),
            'auto_album': self.auto_album_var.get(),
            'auto_title': self.auto_title_var.get(),
            'overwrite_album': self.overwrite_album_var.get(),
            'overwrite_title': self.overwrite_title_var.get(),
            'update_tags': self.update_tags_var.get(),
            'format_filename': self.format_filename_var.get()
        }
        
        # Start processing in thread
        thread = threading.Thread(target=self._process_thread, args=(directory, options), daemon=True)
        thread.start()
    
    def _process_thread(self, directory: str, options: dict):
        """Process files in background thread"""
        try:
            # Create processor
            self.processor = AudioProcessor(num_workers=4)
            self.processor.set_progress_callback(self._on_progress)
            
            # Update status
            self._update_status("Scanning directory...")
            self._log("Starting scan of: " + directory + "\n")
            
            # Process
            results = self.processor.process_directory(directory, options)
            
            # Update UI
            self.window.after(0, self._on_complete, results)
            
        except Exception as e:
            self.window.after(0, self._on_error, str(e))
    
    def _on_progress(self, file_path: str, current: int, total: int, result: dict):
        """Progress callback"""
        def update():
            # Update progress bar
            if total > 0:
                progress = (current / total) * 100
                self.progress_var.set(progress)
            
            # Update status
            status = f"Processing: {current}/{total} files"
            if result:
                if 'error' in result:
                    status += f" - ERROR: {result['error']}"
                elif result.get('fixed'):
                    status += " - Encoding fixed"
                elif result.get('updated'):
                    status += " - Tags updated"
                elif result.get('renamed'):
                    status += " - File renamed"
            self._update_status(status)
            
            # Log
            filename = os.path.basename(file_path)
            log_line = f"[{current}/{total}] {filename}"
            if result:
                if 'error' in result:
                    log_line += f" - ERROR: {result['error']}"
                elif result.get('fixed'):
                    log_line += " - Encoding fixed"
                elif result.get('updated'):
                    log_line += " - Tags updated"
                elif result.get('renamed'):
                    log_line += " - File renamed"
            log_line += "\n"
            self._log(log_line)
        
        self.window.after(0, update)
    
    def _on_complete(self, results: dict):
        """Processing complete"""
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Update progress bar
        self.progress_var.set(100)
        
        # Summary
        summary = f"""
Processing complete!
  Total files:    {results.get('total', 0)}
  Processed:      {results.get('processed', 0)}
  Fixed encoding: {results.get('fixed', 0)}
  Updated tags:   {results.get('updated', 0)}
  Renamed files: {results.get('renamed', 0)}
  Errors:         {results.get('errors', 0)}
"""
        self._update_status("Processing complete")
        self._log(summary)
        
        messagebox.showinfo("Complete", summary, parent=self.window)
    
    def _on_error(self, error: str):
        """Processing error"""
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self._update_status(f"Error: {error}")
        self._log(f"ERROR: {error}\n")
        messagebox.showerror("Error", f"Processing error:\n{error}", parent=self.window)
    
    def _stop_processing(self):
        """Stop processing"""
        if self.processor:
            self.processor.stop()
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self._update_status("Stopped")
        self._log("Processing stopped by user\n")
    
    def _update_status(self, text: str):
        """Update status label"""
        self.status_label.config(text=text)
    
    def _log(self, text: str):
        """Add text to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _on_close(self):
        """Handle window close"""
        if self.is_processing:
            if messagebox.askyesno("Confirm", "Processing is in progress. Stop and close?", parent=self.window):
                self._stop_processing()
                self.window.destroy()
        else:
            self.window.destroy()

