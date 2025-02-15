from enum import Enum

class Messages(str, Enum):
    """
    Enumeration of all translatable messages in the application.
    Using an enum ensures consistency and allows for better IDE support and type checking.
    """
    # Button texts
    SELECT_DIRECTORY = "Select Directory"
    SELECT_IGNORE_FILE = "Select ignore file (Optional)"
    BROWSE = "Browse"
    CLEAR = "Clear"
    GENERATE = "Generate Directory Structure"
    RESET_ALL = "Reset All"
    COPY_TO_CLIPBOARD = "Copy to Clipboard"
    DOWNLOAD = "Download"
    STOP = "Stop"
    
    # Dialog titles
    WARNING = "Warning"
    ERROR = "Error"
    SUCCESS = "Success"
    
    # Dialog messages
    STOP_GENERATION_TITLE = "Stop Generation?"
    STOP_GENERATION_MESSAGE = "Do you want to stop?\n\n• Yes: Stop and clear output\n• No: Continue processing"
    SELECT_DIRECTORY_WARNING = "Please select a directory first!"
    PROCESS_DIRECTORY_ERROR = "Failed to process directory: {}"
    PROCESSING_STATUS = "Processing: {}/{} entries ({}%)"
    CONTENT_COPIED = "Content copied to clipboard!"
    NO_CONTENT_TO_COPY = "No content to copy!"
    NO_CONTENT_TO_DOWNLOAD = "No content to download!"
    SAVE_DIALOG_TITLE = "Save Directory Structure"
    FILE_SAVED = "File saved successfully!"
    SAVE_FILE_ERROR = "Failed to save file: {}"
    QUIT_TITLE = "Quit Application?"
    QUIT_MESSAGE = "Processing is in progress.\nDo you want to quit?\n\n• Yes: Stop processing and quit\n• No: Continue processing"

    def __str__(self) -> str:
        """Return the message value when the enum is converted to string"""
        return self.value 