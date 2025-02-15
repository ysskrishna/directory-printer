import os
import i18n
from directory_printer.core.utilities import get_resource_path

def init_i18n():
    """Initialize i18n configuration"""
    translations_path = get_resource_path(os.path.join('directory_printer', 'translations'))
    i18n.load_path.append(translations_path)

    i18n.set('filename_format', '{locale}.{format}')
    i18n.set('file_format', 'json')  
    i18n.set('skip_locale_root_data', True)
    i18n.set('locale', 'en')
    i18n.set('fallback', 'en')

def set_language(locale: str):
    """Set the current language"""
    i18n.set('locale', locale)

def get_language() -> str:
    """Get the current language"""
    return i18n.get('locale')

def t(key: str, **kwargs) -> str:
    """Translate a key with optional parameters"""    
    value = i18n.t(key, **kwargs)
    return value
