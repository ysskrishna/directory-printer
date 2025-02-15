import os
import subprocess
from pathlib import Path

def compile_translations():
    """Compile all .po files to .mo files"""
    locales_dir = Path("directory_printer/locales")
    
    for lang_dir in locales_dir.glob("*/LC_MESSAGES"):
        po_file = lang_dir / "directory_printer.po"
        mo_file = lang_dir / "directory_printer.mo"
        
        if po_file.exists():
            print(f"Compiling {po_file} to {mo_file}")
            try:
                subprocess.run(["msgfmt", str(po_file), "-o", str(mo_file)], check=True)
                print(f"Successfully compiled {lang_dir.parent.name} translations")
            except subprocess.CalledProcessError as e:
                print(f"Error compiling {lang_dir.parent.name} translations: {e}")
            except FileNotFoundError:
                print("Error: msgfmt not found. Please install gettext tools.")
                return

if __name__ == "__main__":
    compile_translations() 