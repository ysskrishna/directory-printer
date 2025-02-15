#!/usr/bin/env python3
import os
import polib
from typing import Dict, Optional
from directory_printer.i18n import LANGUAGES
from directory_printer.i18n_messages import Messages

def create_pot_template() -> polib.POFile:
    """Create a new POT template file from Messages enum"""
    pot = polib.POFile()
    pot.metadata = {
        'Project-Id-Version': 'directory-printer',
        'Report-Msgid-Bugs-To': '',
        'POT-Creation-Date': 'YEAR-MO-DA HO:MI+ZONE',
        'PO-Revision-Date': 'YEAR-MO-DA HO:MI+ZONE',
        'Last-Translator': 'FULL NAME <EMAIL@ADDRESS>',
        'Language-Team': 'LANGUAGE <LL@li.org>',
        'Language': '',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding': '8bit',
    }

    # Add entries from Messages enum
    for msg in Messages:
        entry = polib.POEntry(
            msgid=msg.value,
            msgstr='',
            comment=f"Message ID: {msg.name}"  # Add enum key as a comment for reference
        )
        pot.append(entry)

    return pot

def update_po_file(language: str, pot: polib.POFile, existing_po: Optional[polib.POFile] = None) -> polib.POFile:
    """Update or create a .po file for the specified language"""
    po = polib.POFile()
    po.metadata = pot.metadata.copy()
    po.metadata.update({
        'Language': language,
        'Language-Team': LANGUAGES[language],
        'Plural-Forms': 'nplurals=2; plural=(n != 1);',  # Default plural form, adjust per language if needed
    })

    # Create a map of existing translations
    existing_translations: Dict[str, str] = {}
    if existing_po:
        existing_translations = {entry.msgid: entry.msgstr for entry in existing_po}

    # Add entries from template, preserving existing translations
    for template_entry in pot:
        entry = polib.POEntry(
            msgid=template_entry.msgid,
            msgstr=existing_translations.get(template_entry.msgid, ''),
            comment=template_entry.comment
        )
        po.append(entry)

    return po

def main():
    """Main function to update all translation files"""
    # Get the base directory (where locales folder should be)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    locales_dir = os.path.join(base_dir, 'locales')
    
    # Create POT template
    pot = create_pot_template()
    
    # Ensure locales directory exists
    os.makedirs(locales_dir, exist_ok=True)
    
    # Save POT template
    pot_path = os.path.join(locales_dir, 'directory_printer.pot')
    pot.save(pot_path)
    print(f"Created template: {pot_path}")
    
    # Update .po files for each language
    for lang in LANGUAGES:
        lang_dir = os.path.join(locales_dir, lang, 'LC_MESSAGES')
        os.makedirs(lang_dir, exist_ok=True)
        
        po_path = os.path.join(lang_dir, 'directory_printer.po')
        existing_po = None
        
        # Load existing translations if they exist
        if os.path.exists(po_path):
            try:
                existing_po = polib.pofile(po_path)
            except Exception as e:
                print(f"Warning: Could not load existing translations for {lang}: {e}")
        
        # Update/create PO file
        po = update_po_file(lang, pot, existing_po)
        po.save(po_path)
        print(f"Updated translations for {lang}: {po_path}")

if __name__ == '__main__':
    main() 