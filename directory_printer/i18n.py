import os
import gettext
from typing import Optional, Union
from .i18n_messages import Messages

# Available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'zh': '中文'
}

DEFAULT_LANGUAGE = 'en'

def setup_i18n(language: Optional[str] = None) -> gettext.GNUTranslations:
    """
    Set up internationalization for the application
    
    Args:
        language: Language code (e.g., 'en', 'es', 'zh'). If None, uses system default or falls back to English
    
    Returns:
        gettext.GNUTranslations object
    """
    if not language:
        language = DEFAULT_LANGUAGE
    
    # Normalize language code
    language = language.lower()
    if language not in LANGUAGES:
        language = DEFAULT_LANGUAGE
    
    # Get the directory containing this file
    localedir = os.path.join(os.path.dirname(__file__), 'locales')
    
    # Set up translation
    try:
        translation = gettext.translation(
            'directory_printer',
            localedir=localedir,
            languages=[language]
        )
        translation.install()
        return translation
    except FileNotFoundError:
        # Fallback to default gettext behavior (English)
        gettext.install('directory_printer')
        return gettext.NullTranslations()

# Initialize translation with default language
current_translation = setup_i18n()

def change_language(language: str) -> None:
    """
    Change the application's language
    
    Args:
        language: Language code (e.g., 'en', 'es', 'zh')
    """
    global current_translation
    current_translation = setup_i18n(language)

def _(message: Union[str, Messages], *args, **kwargs) -> str:
    """
    Translate a message
    
    Args:
        message: Message to translate (can be string or Messages enum)
        *args: Format arguments for the message
        **kwargs: Format keyword arguments for the message
    
    Returns:
        Translated message with any formatting applied
    """
    if isinstance(message, Messages):
        message = message.value
    
    translated = current_translation.gettext(message) if current_translation else message
    
    if args or kwargs:
        return translated.format(*args, **kwargs)
    return translated 