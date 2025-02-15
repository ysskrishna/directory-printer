import os
import tkinter as tk
import webbrowser
import json
import urllib.request
from importlib.metadata import version
from tkinter import filedialog, scrolledtext, messagebox, ttk

import tomli
from PIL import Image, ImageTk

from directory_printer.core.printer import print_structure
from directory_printer.core.i18n_config import init_i18n, t, set_language, get_language
from directory_printer.core.utilities import get_resource_path
from directory_printer.core.configuration import Configuration


def load_project_metadata():
    """Load project metadata from pyproject.toml"""
    toml_path = get_resource_path("pyproject.toml")
    with open(toml_path, "rb") as f:
        toml_data = tomli.load(f)
    return toml_data.get("tool", {}).get("directory_printer", {}).get("ui", {})


class DirectoryPrinterApp:
    def __init__(self):
        # Initialize configuration
        self.config = Configuration()
        
        # Initialize i18n with saved language
        init_i18n()
        set_language(self.config.get_language())
        
        self.root = tk.Tk()
        self.root.title(t('TITLE', version=version('directory-printer')))
        self.root.minsize(700, 400)
        self.logo_image = None
        self.project_metadata = load_project_metadata()
        self.selected_folder = None
        self.gitignore_path = None
        self.stop_processing = False
        self.current_version = version('directory-printer')

        # Language options
        self.languages = {
            'en': t('MENU.FILE.LANGUAGES.ENGLISH'),
            'es': t('MENU.FILE.LANGUAGES.SPANISH'),
            'zh': t('MENU.FILE.LANGUAGES.CHINESE')
        }

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

        # Create menu bar
        self.create_menu_bar()
        
        self.setup_ui()

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('MENU.FILE.TITLE'), menu=file_menu)
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label=t('MENU.FILE.OPEN_RECENT'), menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label=t('MENU.FILE.CLEAR_RECENT'), command=self.clear_recent_files)
        file_menu.add_separator()
        
        # Language submenu
        language_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label=t('MENU.FILE.LANGUAGE'), menu=language_menu)
        
        # Add language options
        current_language = get_language()
        for lang_code, lang_name in self.languages.items():
            language_menu.add_command(
                label=f"{'✓ ' if lang_code == current_language else '  '}{lang_name}",
                command=lambda code=lang_code: self.change_language_from_menu(code)
            )
            
        file_menu.add_separator()
        file_menu.add_command(label=t('MENU.FILE.EXIT'), command=self.on_closing)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('MENU.HELP.TITLE'), menu=help_menu)
        
        # Add help menu items
        help_menu.add_command(label=t('MENU.HELP.FAQ'), command=self.open_faq)
        help_menu.add_command(label=t('MENU.HELP.CHECK_UPDATES'), command=self.check_updates)
        help_menu.add_separator()
        help_menu.add_command(
            label=t('MENU.HELP.CURRENT_VERSION', version=self.current_version),
            state=tk.DISABLED
        )

        # About menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('MENU.ABOUT.TITLE'), menu=about_menu)
        
        # Add about menu items
        about_menu.add_command(
            label=t('MENU.ABOUT.AUTHOR'),
            command=lambda: self.open_link(self.project_metadata.get("author_linkedin"))
        )
        about_menu.add_command(
            label=t('MENU.ABOUT.PRODUCTHUNT'),
            command=lambda: self.open_link(self.project_metadata.get("product_hunt_url"))
        )
        about_menu.add_command(
            label=t('MENU.ABOUT.GITHUB'),
            command=lambda: self.open_link(self.project_metadata.get("github_repo_url"))
        )

    def update_recent_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, tk.END)
        recent_files = self.config.get_recent_files()
        
        if not recent_files:
            self.recent_menu.add_command(label="(Empty)", state=tk.DISABLED)
        else:
            for entry in recent_files:
                directory_path = entry.get('directory_path', '')
                self.recent_menu.add_command(
                    label=os.path.basename(directory_path),
                    command=lambda e=entry: self.open_recent_file(e)
                )

    def open_recent_file(self, entry):
        """Open a recently used file with its configuration"""
        directory_path = entry.get('directory_path', '')
        config = entry.get('config', {})
        
        if os.path.exists(directory_path):
            # Clear output if opening a different directory
            if self.selected_folder != directory_path:
                self.output_text.delete("1.0", tk.END)
                
            self.selected_folder = directory_path
            self.directory_var.set(directory_path)
            
            # Restore ignore file if it exists
            ignore_file = config.get('ignore_file')
            if ignore_file and os.path.exists(ignore_file):
                self.gitignore_path = ignore_file
                self.gitignore_var.set(ignore_file)
            else:
                self.gitignore_path = None
                self.gitignore_var.set("")
        else:
            messagebox.showwarning(
                t('DIALOGS.WARNING'),
                t('MESSAGES.DIRECTORY_NOT_FOUND', path=directory_path)
            )
            # Remove from recent files if it doesn't exist
            recent_files = self.config.get_recent_files()
            recent_files = [f for f in recent_files if f.get('directory_path') != directory_path]
            self.config.set_recent_files(recent_files)
            self.update_recent_menu()

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.config.clear_recent_files()
        self.update_recent_menu()

    def change_language_from_menu(self, lang_code):
        """Change language from menu selection"""
        if lang_code != get_language():
            set_language(lang_code)
            self.config.set_language(lang_code)
            
            # Save current state
            current_directory = self.directory_var.get()
            current_gitignore = self.gitignore_var.get()
            current_output = self.output_text.get("1.0", tk.END)
            
            # Destroy all widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Update window title
            self.root.title(t('TITLE', version=version('directory-printer')))
            
            # Recreate menu
            self.create_menu_bar()
            
            # Rebuild UI
            self.setup_ui()
            
            # Restore state
            self.directory_var.set(current_directory)
            self.gitignore_var.set(current_gitignore)
            self.output_text.insert("1.0", current_output)

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
        
        self.dir_label = ttk.Label(dir_frame, text=t('DIRECTORY.LABEL'), width=25)
        self.dir_label.grid(row=0, column=0, padx=5)
        
        self.directory_var = tk.StringVar()
        self.directory_entry = ttk.Entry(dir_frame, textvariable=self.directory_var)
        self.directory_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.browse_btn = ttk.Button(dir_frame, text=t('DIRECTORY.BROWSE'), command=self.browse_folder)
        self.browse_btn.grid(row=0, column=2, padx=2)
        
        self.clear_dir_btn = ttk.Button(dir_frame, text=t('DIRECTORY.CLEAR'), command=self.clear_directory)
        self.clear_dir_btn.grid(row=0, column=3, padx=2)

        # Gitignore selection row
        gitignore_frame = ttk.Frame(main_frame)
        gitignore_frame.pack(fill=tk.X, pady=(0, 10))
        gitignore_frame.grid_columnconfigure(1, weight=1)  # Make the entry expand
        
        self.gitignore_label = ttk.Label(gitignore_frame, text=t('IGNORE_FILE.LABEL'), width=25)
        self.gitignore_label.grid(row=0, column=0, padx=5)
        
        self.gitignore_var = tk.StringVar()
        self.gitignore_entry = ttk.Entry(gitignore_frame, textvariable=self.gitignore_var)
        self.gitignore_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.browse_gitignore_btn = ttk.Button(gitignore_frame, text=t('IGNORE_FILE.BROWSE'), command=self.select_gitignore)
        self.browse_gitignore_btn.grid(row=0, column=2, padx=2)
        
        self.clear_gitignore_btn = ttk.Button(gitignore_frame, text=t('IGNORE_FILE.CLEAR'), command=self.clear_gitignore)
        self.clear_gitignore_btn.grid(row=0, column=3, padx=2)

        # Action buttons and progress frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Button container
        button_container = ttk.Frame(action_frame)
        button_container.pack(fill=tk.X, pady=(0, 5))
        self.generate_btn = ttk.Button(button_container, text=t('ACTIONS.GENERATE'), command=self.process_directory)
        self.generate_btn.pack(side=tk.LEFT, padx=2)
        self.reset_btn = ttk.Button(button_container, text=t('ACTIONS.RESET'), command=self.reset_all)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

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
        
        self.stop_button = ttk.Button(progress_row, text=t('ACTIONS.STOP'), command=self.confirm_stop)
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
        self.copy_btn = ttk.Button(left_buttons, text=t('ACTIONS.COPY'), command=self.copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=2)
        self.download_btn = ttk.Button(left_buttons, text=t('ACTIONS.DOWNLOAD'), command=self.download_as_txt)
        self.download_btn.pack(side=tk.LEFT, padx=2)

        # Right side - links
        links_frame = ttk.Frame(buttons_frame)
        links_frame.grid(row=0, column=2, sticky='e')

        author_link = self.create_link_label(
            links_frame, self.project_metadata.get("author_name"), self.project_metadata.get("author_linkedin")
        )
        author_link.pack(side=tk.LEFT)

        separator1 = ttk.Label(links_frame, text=" | ")
        separator1.pack(side=tk.LEFT)

        product_hunt_link = self.create_link_label(
            links_frame, "producthunt", self.project_metadata.get("product_hunt_url")
        )
        product_hunt_link.pack(side=tk.LEFT)

        separator2 = ttk.Label(links_frame, text=" | ")
        separator2.pack(side=tk.LEFT)

        github_link = self.create_link_label(
            links_frame, "github", self.project_metadata.get("github_repo_url")
        )
        github_link.pack(side=tk.LEFT)

    def select_gitignore(self):
        file_path = filedialog.askopenfilename(
            title=t('IGNORE_FILE.LABEL'),
            filetypes=[(".gitignore", ".gitignore"), (t('SAVE_DIALOG.FILETYPES.ALL'), "*.*")]
        )
        if file_path:
            self.gitignore_path = file_path
            self.gitignore_var.set(file_path)
            
            # Update recent files entry if a directory is selected
            if self.selected_folder:
                config = {'ignore_file': file_path}
                self.config.add_recent_file(self.selected_folder, config)
                self.update_recent_menu()
        else:
            self.gitignore_path = None
            self.gitignore_var.set("")
            
            # Clear ignore_file from recent files entry if a directory is selected
            if self.selected_folder:
                config = {}
                self.config.add_recent_file(self.selected_folder, config)
                self.update_recent_menu()

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
                t('DIALOGS.STOP_TITLE'),
                t('DIALOGS.STOP_MESSAGE')
            ):
                self.stop_processing = True
                self.output_text.delete("1.0", tk.END)
                self.progress_frame.pack_forget()  # Hide entire progress frame

    def process_directory(self):
        if not self.selected_folder:
            messagebox.showwarning(t('DIALOGS.WARNING'), t('MESSAGES.SELECT_DIRECTORY'))
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
                messagebox.showerror(t('DIALOGS.ERROR'), t('MESSAGES.PROCESS_ERROR', error=str(e)))
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
        self.progress_label.config(text=t('PROGRESS.PROCESSING', current=current, total=total, percent=f"{progress:.1f}"))
        self.root.update()  # Use update to process events and keep UI responsive
        return True  # Continue processing

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_folder = folder_selected
            self.directory_var.set(folder_selected)
            # Add to recent files with current configuration
            config = {}
            if self.gitignore_path:
                config['ignore_file'] = self.gitignore_path
            self.config.add_recent_file(folder_selected, config)
            self.update_recent_menu()

    def copy_to_clipboard(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo(t('DIALOGS.SUCCESS'), t('MESSAGES.COPY_SUCCESS'))
        else:
            messagebox.showwarning(t('DIALOGS.WARNING'), t('MESSAGES.NO_CONTENT'))

    def download_as_txt(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning(t('DIALOGS.WARNING'), t('MESSAGES.NO_CONTENT_DOWNLOAD'))
            return

        default_name = "directory_structure.txt"
        if self.selected_folder:
            default_name = os.path.basename(self.selected_folder) + ".txt"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[(t('SAVE_DIALOG.FILETYPES.TEXT'), "*.txt"), (t('SAVE_DIALOG.FILETYPES.ALL'), "*.*")],
            title=t('SAVE_DIALOG.TITLE'),
            initialfile=default_name
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo(t('DIALOGS.SUCCESS'), t('MESSAGES.SAVE_SUCCESS'))
            except Exception as e:
                messagebox.showerror(t('DIALOGS.ERROR'), t('MESSAGES.SAVE_ERROR', error=str(e)))

    def on_closing(self):
        """Handle window close event"""
        if self.stop_processing or not self.progress_frame.winfo_ismapped():
            # If not processing or already stopped, close directly
            self.root.destroy()
        else:
            # If processing, ask for confirmation
            self.root.bell()
            if messagebox.askyesno(
                t('DIALOGS.QUIT_TITLE'),
                t('DIALOGS.QUIT_MESSAGE')
            ):
                self.stop_processing = True
                self.root.destroy()

    def run(self):
        self.root.mainloop()

    def open_faq(self):
        """Open FAQ section in GitHub"""
        webbrowser.open(f"{self.project_metadata.get('faqs_url')}")

    def check_updates(self):
        """Check for updates by comparing current version with latest release"""
        try:
            # Get latest release info from GitHub API
            api_url = self.project_metadata.get('release_api_url')
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read())
                latest_version = data['tag_name'].lstrip('v')
                
                # Compare versions
                if latest_version > self.current_version:
                    if messagebox.askyesno(
                        t('DIALOGS.SUCCESS'),
                        t('MESSAGES.UPDATE_AVAILABLE', version=latest_version),
                        icon='info'
                    ):
                        webbrowser.open(data['html_url'])
                else:
                    messagebox.showinfo(
                        t('DIALOGS.SUCCESS'),
                        t('MESSAGES.UPDATE_LATEST'),
                        icon='info'
                    )
        except Exception as e:
            messagebox.showerror(
                t('DIALOGS.ERROR'),
                t('MESSAGES.UPDATE_ERROR', error=str(e))
            )


def main():
    app = DirectoryPrinterApp()
    app.run()


if __name__ == "__main__":
    main()
