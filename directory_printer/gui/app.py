import os
import tkinter as tk
import webbrowser
from importlib.metadata import version
from tkinter import filedialog, scrolledtext

import tomli
from PIL import Image, ImageTk

from directory_printer.core.printer import print_structure


def load_config():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pyproject.toml"
    )
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
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
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

        github_link = self.create_link_label(
            author_frame, "Github", self.config.get("repository_url")
        )
        github_link.pack(side=tk.LEFT)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Folder structure for: {folder_selected}\n")
            output_list = print_structure(folder_selected)
            self.output_text.insert(tk.END, "\n".join(output_list))

    def run(self):
        self.root.mainloop()


def main():
    app = DirectoryPrinterApp()
    app.run()


if __name__ == "__main__":
    main()
