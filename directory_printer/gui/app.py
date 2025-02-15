import os
import tkinter as tk
import webbrowser
from importlib.metadata import version
from tkinter import filedialog, scrolledtext, messagebox, ttk
import sys

import tomli
from PIL import Image, ImageTk

from directory_printer.core.printer import print_structure


def get_resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    return os.path.join(base_path, relative_path)


def load_config():
    config_path = get_resource_path("pyproject.toml")
    with open(config_path, "rb") as f:
        config = tomli.load(f)
    return config.get("tool", {}).get("directory_printer", {}).get("ui", {})


class DirectoryPrinterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Directory Printer v{version('directory-printer')}")
        self.root.minsize(700, 400)
        self.logo_image = None
        self.config = load_config()
        self.selected_folder = None
        self.gitignore_path = None
        self.stop_processing = False

        # Add window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Set window icon
        logo_path = get_resource_path(os.path.join("directory_printer", "assets", "logo.png"))
        if os.path.exists(logo_path):
            try:
                icon = Image.open(logo_path)
                icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(True, icon_photo)
            except Exception as e:
                print(f"Could not set window icon: {e}")

        self.setup_ui()

    def open_link(self, url):
        webbrowser.open(url)

    def create_link_label(self, parent, text, url):
        link = tk.Label(parent, text=text, fg="blue", cursor="hand2", font=("Helvetica", 9))
        link.bind("<Button-1>", lambda e: self.open_link(url))
        link.bind("<Enter>", lambda e: link.configure(font=("Helvetica", 9, "underline")))
        link.bind("<Leave>", lambda e: link.configure(font=("Helvetica", 9)))
        return link

    def setup_ui(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Directory selection row
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        dir_frame.grid_columnconfigure(1, weight=1)  # Make the entry expand
        
        dir_label = ttk.Label(dir_frame, text="Select Directory", width=25)
        dir_label.grid(row=0, column=0, padx=5)
        
        self.directory_var = tk.StringVar()
        self.directory_entry = ttk.Entry(dir_frame, textvariable=self.directory_var)
        self.directory_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=2)
        
        clear_btn = ttk.Button(dir_frame, text="Clear", command=self.clear_directory)
        clear_btn.grid(row=0, column=3, padx=2)

        # Gitignore selection row
        gitignore_frame = ttk.Frame(main_frame)
        gitignore_frame.pack(fill=tk.X, pady=(0, 10))
        gitignore_frame.grid_columnconfigure(1, weight=1)  # Make the entry expand
        
        gitignore_label = ttk.Label(gitignore_frame, text="Select ignore file (Optional)", width=25)
        gitignore_label.grid(row=0, column=0, padx=5)
        
        self.gitignore_var = tk.StringVar()
        self.gitignore_entry = ttk.Entry(gitignore_frame, textvariable=self.gitignore_var)
        self.gitignore_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        browse_gitignore_btn = ttk.Button(gitignore_frame, text="Browse", command=self.select_gitignore)
        browse_gitignore_btn.grid(row=0, column=2, padx=2)
        
        clear_gitignore_btn = ttk.Button(gitignore_frame, text="Clear", command=self.clear_gitignore)
        clear_gitignore_btn.grid(row=0, column=3, padx=2)

        # Action buttons and progress frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Button container
        button_container = ttk.Frame(action_frame)
        button_container.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_container, text="Generate Directory Structure", command=self.process_directory).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_container, text="Reset All", command=self.reset_all).pack(side=tk.LEFT, padx=2)

        # Progress bar (hidden initially)
        self.progress_frame = ttk.Frame(action_frame)
        self.progress_frame.pack(fill=tk.X)
        
        # Progress bar and controls frame using grid
        progress_controls = ttk.Frame(self.progress_frame)
        progress_controls.pack(fill=tk.X)
        progress_controls.grid_columnconfigure(0, weight=1)  # Make progress bar expand
        
        # Create a single row container for progress bar and stop button
        progress_row = ttk.Frame(progress_controls)
        progress_row.pack(fill=tk.X)
        progress_row.grid_columnconfigure(0, weight=1)  # Make progress bar expand
        
        # Progress bar and stop button in same row
        self.progress_bar = ttk.Progressbar(progress_row, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        self.stop_button = ttk.Button(progress_row, text="Stop", command=self.confirm_stop)
        self.stop_button.grid(row=0, column=1)
        
        # Progress label below the progress bar
        self.progress_label = ttk.Label(progress_controls, text="")
        self.progress_label.pack(anchor='w')
        
        # Initially hide all progress elements
        self.progress_frame.pack_forget()

        # Output area
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=25)
        self.output_text.pack(pady=(0, 5), fill=tk.BOTH, expand=True)

        # Buttons frame for copy and download
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        buttons_frame.grid_columnconfigure(1, weight=1)  # Add weight to create space between buttons and links

        # Left side - action buttons
        left_buttons = ttk.Frame(buttons_frame)
        left_buttons.grid(row=0, column=0, sticky='w')
        ttk.Button(left_buttons, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_buttons, text="Download", command=self.download_as_txt).pack(side=tk.LEFT, padx=2)

        # Right side - links
        links_frame = ttk.Frame(buttons_frame)
        links_frame.grid(row=0, column=2, sticky='e')

        author_link = self.create_link_label(
            links_frame, self.config.get("author_name"), self.config.get("author_linkedin")
        )
        author_link.pack(side=tk.LEFT)

        separator1 = ttk.Label(links_frame, text=" | ")
        separator1.pack(side=tk.LEFT)

        product_hunt_link = self.create_link_label(
            links_frame, "producthunt", self.config.get("product_hunt_url")
        )
        product_hunt_link.pack(side=tk.LEFT)

        separator2 = ttk.Label(links_frame, text=" | ")
        separator2.pack(side=tk.LEFT)

        github_link = self.create_link_label(
            links_frame, "github", self.config.get("github_repo_url")
        )
        github_link.pack(side=tk.LEFT)

    def select_gitignore(self):
        file_path = filedialog.askopenfilename(
            title="Select .gitignore file",
            filetypes=[(".gitignore", ".gitignore"), ("All files", "*.*")]
        )
        if file_path:
            self.gitignore_path = file_path
            self.gitignore_var.set(file_path)
        else:
            self.gitignore_path = None
            self.gitignore_var.set("")

    def clear_directory(self):
        self.selected_folder = None
        self.directory_var.set("")

    def clear_gitignore(self):
        self.gitignore_path = None
        self.gitignore_var.set("")

    def reset_all(self):
        self.clear_directory()
        self.clear_gitignore()
        self.output_text.delete("1.0", tk.END)
        self.progress_bar["value"] = 0
        self.progress_label.config(text="")
        self.progress_frame.pack_forget()  # Hide entire progress frame

    def confirm_stop(self):
        if not self.stop_processing:  # Only show dialog if not already stopping
            self.root.bell()  # Ring the system bell
            if messagebox.askyesno(
                "Stop Generation?",
                "Do you want to stop?\n\n"
                "• Yes: Stop and clear output\n"
                "• No: Continue processing"
            ):
                self.stop_processing = True
                self.output_text.delete("1.0", tk.END)
                self.progress_frame.pack_forget()  # Hide entire progress frame

    def process_directory(self):
        if not self.selected_folder:
            messagebox.showwarning("Warning", "Please select a directory first!")
            return

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"{self.selected_folder}\n")
        
        # Reset progress bar and stop flag
        self.progress_bar["value"] = 0
        self.progress_label.config(text="")
        self.stop_processing = False
        
        try:
            output_list = print_structure(
                self.selected_folder,
                gitignore_path=self.gitignore_path,
                progress_callback=self.update_progress
            )
            if not self.stop_processing:  # Only update output if not stopped
                self.output_text.insert(tk.END, "\n".join(output_list))
            else:
                # Clear output if stopped
                self.output_text.delete("1.0", tk.END)
        except Exception as e:
            if not self.stop_processing:  # Only show error if not stopped
                messagebox.showerror("Error", f"Failed to process directory: {str(e)}")
        finally:
            # Hide progress frame when done or stopped
            self.progress_frame.pack_forget()
            # Reset stop flag
            self.stop_processing = False

    def update_progress(self, current: int, total: int):
        if self.stop_processing:
            return False  # Signal to stop processing
            
        # Show progress frame if not already visible
        if not self.progress_frame.winfo_ismapped():
            self.progress_frame.pack(fill=tk.X, pady=5)
        
        progress = (current / total) * 100
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"Processing: {current}/{total} entries ({progress:.1f}%)")
        self.root.update()  # Use update to process events and keep UI responsive
        return True  # Continue processing

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_folder = folder_selected
            self.directory_var.set(folder_selected)

    def copy_to_clipboard(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Content copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No content to copy!")

    def download_as_txt(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "No content to download!")
            return

        default_name = "directory_structure.txt"
        if self.selected_folder:
            default_name = os.path.basename(self.selected_folder) + ".txt"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Directory Structure",
            initialfile=default_name
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def on_closing(self):
        """Handle window close event"""
        if self.stop_processing or not self.progress_frame.winfo_ismapped():
            # If not processing or already stopped, close directly
            self.root.destroy()
        else:
            # If processing, ask for confirmation
            self.root.bell()
            if messagebox.askyesno(
                "Quit Application?",
                "Processing is in progress.\nDo you want to quit?\n\n"
                "• Yes: Stop processing and quit\n"
                "• No: Continue processing"
            ):
                self.stop_processing = True
                self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = DirectoryPrinterApp()
    app.run()


if __name__ == "__main__":
    main()
