import os
import tkinter as tk
import webbrowser
from importlib.metadata import version
from tkinter import filedialog, scrolledtext, messagebox, ttk
import sys

import tomli
from PIL import Image, ImageTk

from directory_printer.core.printer import print_structure
from directory_printer.i18n import _, setup_i18n, LANGUAGES, change_language


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
        self.root.title(_(f"Directory Printer v{version('directory-printer')}"))
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

    def on_language_change(self, *args):
        selected_lang = self.language_var.get()
        for lang_code, lang_name in LANGUAGES.items():
            if lang_name == selected_lang:
                change_language(lang_code)
                self.update_ui_texts()
                break

    def update_ui_texts(self):
        """Update all UI texts after language change"""
        # Update window title
        self.root.title(_(f"Directory Printer v{version('directory-printer')}"))
        
        # Update labels and buttons
        self.dir_label.config(text=_("Select Directory"))
        self.gitignore_label.config(text=_("Select ignore file (Optional)"))
        self.browse_btn.config(text=_("Browse"))
        self.browse_gitignore_btn.config(text=_("Browse"))
        self.clear_btn.config(text=_("Clear"))
        self.clear_gitignore_btn.config(text=_("Clear"))
        self.generate_btn.config(text=_("Generate Directory Structure"))
        self.reset_btn.config(text=_("Reset All"))
        self.copy_btn.config(text=_("Copy to Clipboard"))
        self.download_btn.config(text=_("Download"))
        
        if hasattr(self, 'stop_button'):
            self.stop_button.config(text=_("Stop"))

    def setup_ui(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Language selection
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT, padx=5)
        self.language_var = tk.StringVar(value=LANGUAGES['en'])  # Default to English
        language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                    values=list(LANGUAGES.values()), state='readonly')
        language_combo.pack(side=tk.LEFT)
        self.language_var.trace('w', self.on_language_change)

        # Directory selection row
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        dir_frame.grid_columnconfigure(1, weight=1)
        
        self.dir_label = ttk.Label(dir_frame, text=_("Select Directory"), width=25)
        self.dir_label.grid(row=0, column=0, padx=5)
        
        self.directory_var = tk.StringVar()
        self.directory_entry = ttk.Entry(dir_frame, textvariable=self.directory_var)
        self.directory_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.browse_btn = ttk.Button(dir_frame, text=_("Browse"), command=self.browse_folder)
        self.browse_btn.grid(row=0, column=2, padx=2)
        
        self.clear_btn = ttk.Button(dir_frame, text=_("Clear"), command=self.clear_directory)
        self.clear_btn.grid(row=0, column=3, padx=2)

        # Gitignore selection row
        gitignore_frame = ttk.Frame(main_frame)
        gitignore_frame.pack(fill=tk.X, pady=(0, 10))
        gitignore_frame.grid_columnconfigure(1, weight=1)
        
        self.gitignore_label = ttk.Label(gitignore_frame, text=_("Select ignore file (Optional)"), width=25)
        self.gitignore_label.grid(row=0, column=0, padx=5)
        
        self.gitignore_var = tk.StringVar()
        self.gitignore_entry = ttk.Entry(gitignore_frame, textvariable=self.gitignore_var)
        self.gitignore_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.browse_gitignore_btn = ttk.Button(gitignore_frame, text=_("Browse"), command=self.select_gitignore)
        self.browse_gitignore_btn.grid(row=0, column=2, padx=2)
        
        self.clear_gitignore_btn = ttk.Button(gitignore_frame, text=_("Clear"), command=self.clear_gitignore)
        self.clear_gitignore_btn.grid(row=0, column=3, padx=2)

        # Action buttons and progress frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Button container
        button_container = ttk.Frame(action_frame)
        button_container.pack(fill=tk.X, pady=(0, 5))
        self.generate_btn = ttk.Button(button_container, text=_("Generate Directory Structure"), 
                                     command=self.process_directory)
        self.generate_btn.pack(side=tk.LEFT, padx=2)
        
        self.reset_btn = ttk.Button(button_container, text=_("Reset All"), 
                                  command=self.reset_all)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        # Progress bar (hidden initially)
        self.progress_frame = ttk.Frame(action_frame)
        self.progress_frame.pack(fill=tk.X)
        
        # Progress bar and controls frame using grid
        progress_controls = ttk.Frame(self.progress_frame)
        progress_controls.pack(fill=tk.X)
        progress_controls.grid_columnconfigure(0, weight=1)
        
        # Create a single row container for progress bar and stop button
        progress_row = ttk.Frame(progress_controls)
        progress_row.pack(fill=tk.X)
        progress_row.grid_columnconfigure(0, weight=1)
        
        # Progress bar and stop button in same row
        self.progress_bar = ttk.Progressbar(progress_row, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        self.stop_button = ttk.Button(progress_row, text=_("Stop"), command=self.confirm_stop)
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
        buttons_frame.grid_columnconfigure(1, weight=1)

        # Left side - action buttons
        left_buttons = ttk.Frame(buttons_frame)
        left_buttons.grid(row=0, column=0, sticky='w')
        self.copy_btn = ttk.Button(left_buttons, text=_("Copy to Clipboard"), 
                                 command=self.copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=2)
        
        self.download_btn = ttk.Button(left_buttons, text=_("Download"), 
                                    command=self.download_as_txt)
        self.download_btn.pack(side=tk.LEFT, padx=2)

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
        self.progress_frame.pack_forget()

    def confirm_stop(self):
        if not self.stop_processing:
            self.root.bell()
            if messagebox.askyesno(
                _("Stop Generation?"),
                _("Do you want to stop?\n\n• Yes: Stop and clear output\n• No: Continue processing")
            ):
                self.stop_processing = True
                self.output_text.delete("1.0", tk.END)
                self.progress_frame.pack_forget()

    def process_directory(self):
        if not self.selected_folder:
            messagebox.showwarning(_("Warning"), _("Please select a directory first!"))
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
            if not self.stop_processing:
                self.output_text.insert(tk.END, "\n".join(output_list))
            else:
                self.output_text.delete("1.0", tk.END)
        except Exception as e:
            if not self.stop_processing:
                messagebox.showerror(_("Error"), _(f"Failed to process directory: {str(e)}"))
        finally:
            self.progress_frame.pack_forget()
            self.stop_processing = False

    def update_progress(self, current: int, total: int):
        if self.stop_processing:
            return False
            
        if not self.progress_frame.winfo_ismapped():
            self.progress_frame.pack(fill=tk.X, pady=5)
        
        progress = (current / total) * 100
        self.progress_bar["value"] = progress
        self.progress_label.config(text=_("Processing: {}/{} entries ({}%)").format(
            current, total, f"{progress:.1f}"
        ))
        self.root.update()
        return True

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
            messagebox.showinfo(_("Success"), _("Content copied to clipboard!"))
        else:
            messagebox.showwarning(_("Warning"), _("No content to copy!"))

    def download_as_txt(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning(_("Warning"), _("No content to download!"))
            return

        default_name = "directory_structure.txt"
        if self.selected_folder:
            default_name = os.path.basename(self.selected_folder) + ".txt"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title=_("Save Directory Structure"),
            initialfile=default_name
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo(_("Success"), _("File saved successfully!"))
            except Exception as e:
                messagebox.showerror(_("Error"), _(f"Failed to save file: {str(e)}"))

    def on_closing(self):
        if self.stop_processing or not self.progress_frame.winfo_ismapped():
            self.root.destroy()
        else:
            self.root.bell()
            if messagebox.askyesno(
                _("Quit Application?"),
                _("Processing is in progress.\nDo you want to quit?\n\n• Yes: Stop processing and quit\n• No: Continue processing")
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
