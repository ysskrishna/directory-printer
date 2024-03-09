import os
import tkinter as tk
from tkinter import filedialog, scrolledtext


def print_structure(path, prefix="", output_list=None):
    """Recursively get folder and file structure."""
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        output_list.append(f"{prefix}[Permission Denied]")
        return
    except FileNotFoundError:
        output_list.append(f"Error: Directory '{path}' not found!")
        return


    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        symbol = "└── " if is_last else "├── "
        full_path = os.path.join(path, entry)
        output_list.append(f"{prefix}{symbol}{entry}")
        if os.path.isdir(full_path):
            next_prefix = "    " if is_last else "│   "
            print_structure(full_path, prefix + next_prefix, output_list)


def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Folder structure for: {folder_selected}\n")
        output_list = []
        print_structure(folder_selected, output_list=output_list)
        output_text.insert(tk.END, "\n".join(output_list))


# Create GUI
root = tk.Tk()
root.title("Folder Structure Viewer")


frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)


browse_button = tk.Button(frame, text="Select Folder", command=browse_folder)
browse_button.pack(pady=5)


output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=25)
output_text.pack(pady=5, fill=tk.BOTH, expand=True)


root.mainloop()
