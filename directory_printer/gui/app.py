import tkinter as tk
from tkinter import filedialog, scrolledtext

from directory_printer.core.printer import print_structure


class DirectoryPrinterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Directory Structure Viewer")
        
        self.setup_ui()
        
    def setup_ui(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        browse_button = tk.Button(frame, text="Select Folder", command=self.browse_folder)
        browse_button.pack(pady=5)
        
        self.output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=25)
        self.output_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
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