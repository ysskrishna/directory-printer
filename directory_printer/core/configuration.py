import json
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

class Configuration:
    def __init__(self):
        self.config_dir = os.path.join(str(Path.home()), '.directory_printer')
        self.config_file = os.path.join(self.config_dir, 'configuration.json')
        self.config = self._load_configuration()

    def _create_backup(self):
        """Create a backup of the corrupted configuration file"""
        if os.path.exists(self.config_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.config_file}.{timestamp}.backup"
            try:
                shutil.copy2(self.config_file, backup_file)
                return True
            except Exception:
                return False
        return False

    def _load_configuration(self) -> dict:
        """Load configuration from file or create default configuration"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Validate and clean recent files
                if 'recent_files' in config:
                    config['recent_files'] = self._validate_recent_files(config['recent_files'])
                # Add timestamps if they don't exist
                if 'created_at' not in config:
                    config['created_at'] = datetime.now().isoformat()
                if 'updated_at' not in config:
                    config['updated_at'] = config['created_at']
                return config
            except Exception:
                # Create backup of corrupted file
                self._create_backup()
                # Return default configuration
                return self._get_default_configuration()
        return self._get_default_configuration()

    def _validate_recent_files(self, recent_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate recent files and remove entries with non-existent paths"""
        valid_entries = []
        for entry in recent_files:
            path = entry.get('path', '')
            if os.path.exists(path):
                valid_entries.append(entry)
        return valid_entries

    def _get_default_configuration(self) -> dict:
        """Get default configuration"""
        now = datetime.now().isoformat()
        return {
            'language': 'en',
            'recent_files': [],
            'created_at': now,
            'updated_at': now
        }

    def _save_configuration(self):
        """Save configuration to file"""
        # Update the updated_at timestamp
        self.config['updated_at'] = datetime.now().isoformat()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    def get_language(self) -> str:
        """Get current language"""
        return self.config.get('language', 'en')

    def set_language(self, language: str):
        """Set current language"""
        self.config['language'] = language
        self._save_configuration()

    def get_recent_files(self) -> List[Dict[str, Any]]:
        """Get list of recent files with their configurations"""
        return self.config.get('recent_files', [])

    def set_recent_files(self, recent_files: List[Dict[str, Any]]):
        """Set the list of recent files and save to disk"""
        self.config['recent_files'] = recent_files
        self._save_configuration()

    def add_recent_file(self, directory_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Add a directory with its configuration to recent files list
        
        Args:
            directory_path: Path to the directory
            config: Dictionary containing configuration (e.g., ignore_file path)
        """
        if config is None:
            config = {}
            
        recent_files = self.get_recent_files()
        entry = {
            'directory_path': directory_path,
            'config': config,
            'created_at': datetime.now().isoformat()
        }
        
        # Remove if path already exists
        recent_files = [f for f in recent_files if f.get('directory_path') != directory_path]
        
        # Add to front of list
        recent_files.insert(0, entry)
        
        # Keep only last 5
        self.config['recent_files'] = recent_files[:5]
        self._save_configuration()

    def clear_recent_files(self):
        """Clear recent files list"""
        self.config['recent_files'] = []
        self._save_configuration() 