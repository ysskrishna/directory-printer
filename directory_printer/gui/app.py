import os
import tkinter as tk
import webbrowser
from importlib.metadata import version
from tkinter import filedialog, scrolledtext, messagebox
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
        self.root.minsize(600, 400)
        self.logo_image = None
        self.config = load_config()

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

        browse_button = tk.Button(main_frame, text="Select Folder", command=self.browse_folder)
        browse_button.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=25)
        self.output_text.pack(pady=5, fill=tk.BOTH, expand=True)

        # Buttons frame for copy and download
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 5))

        copy_button = tk.Button(buttons_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, padx=2)

        download_button = tk.Button(buttons_frame, text="Download as TXT", command=self.download_as_txt)
        download_button.pack(side=tk.LEFT, padx=2)

        # Footer section
        footer_frame = tk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(5, 0))

        author_frame = tk.Frame(footer_frame)
        author_frame.pack(side=tk.LEFT)

        author_link = self.create_link_label(
            author_frame, self.config.get("author_name"), self.config.get("author_linkedin")
        )
        author_link.pack(side=tk.LEFT)

        separator = tk.Label(author_frame, text=" | ", font=("Helvetica", 8))
        separator.pack(side=tk.LEFT)

        product_hunt_link = self.create_link_label(
            author_frame, "producthunt", self.config.get("product_hunt_url")
        )
        product_hunt_link.pack(side=tk.LEFT)

        separator = tk.Label(author_frame, text=" | ", font=("Helvetica", 8))
        separator.pack(side=tk.LEFT)

        github_link = self.create_link_label(
            author_frame, "github", self.config.get("github_repo_url")
        )
        github_link.pack(side=tk.LEFT)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"{folder_selected}\n")
            output_list = print_structure(folder_selected)
            self.output_text.insert(tk.END, "\n".join(output_list))

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

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Directory Structure"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def run(self):
        self.root.mainloop()


def main():
    app = DirectoryPrinterApp()
    app.run()


if __name__ == "__main__":
    main()
