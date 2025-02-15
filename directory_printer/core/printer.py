import os
from typing import List, Optional, Callable
import re


def parse_gitignore(gitignore_path: str) -> List[str]:
    """Parse gitignore file and return list of patterns"""
    if not os.path.exists(gitignore_path):
        return []
    
    with open(gitignore_path, 'r') as f:
        patterns = []
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Remove trailing spaces and slashes
            pattern = line.rstrip('/ ')
            
            # Convert .gitignore pattern to regex pattern
            if pattern.startswith('/'):
                # Pattern starting with / matches from project root
                pattern = pattern[1:]  # Remove leading /
                pattern = f'^{pattern}'  # Anchor to start
            else:
                # Pattern without leading / can match anywhere in path
                pattern = f'.*?{pattern}'
            
            # Handle special characters
            pattern = (
                pattern
                .replace('.', r'\.')  # Escape dots
                .replace('**', '.*')  # ** matches anything including /
                .replace('*', '[^/]*')  # * matches anything except /
                .replace('?', '[^/]')  # ? matches any single character except /
            )
            
            # Make sure pattern matches full path component
            pattern = f'{pattern}(?:$|/.*)'
            
            patterns.append(pattern)
        return patterns


def should_ignore(path: str, base_path: str, ignore_patterns: List[str]) -> bool:
    """Check if path should be ignored based on gitignore patterns"""
    if not ignore_patterns:
        return False
    
    # Get relative path from base directory
    rel_path = os.path.relpath(path, base_path)
    # Convert Windows path separators to Unix style
    rel_path = rel_path.replace('\\', '/')
    
    # Check each pattern
    for pattern in ignore_patterns:
        if re.match(pattern, rel_path):
            return True
            
        # Also check parent directories
        parts = rel_path.split('/')
        for i in range(len(parts)):
            partial_path = '/'.join(parts[:i+1])
            if re.match(pattern, partial_path):
                return True
                
    return False


def count_entries(path: str, ignore_patterns: List[str] = None) -> int:
    """Count total number of entries for progress tracking"""
    total = 0
    for root, dirs, files in os.walk(path):
        if ignore_patterns and should_ignore(root, path, ignore_patterns):
            continue
        total += len(files) + len(dirs)
    return total


def print_structure(
    path: str,
    prefix: str = "",
    output_list: Optional[List[str]] = None,
    gitignore_path: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], bool]] = None
) -> List[str]:
    """
    Print directory structure with gitignore support and progress tracking
    
    Args:
        path: Directory path to print
        prefix: Prefix for current line (used for tree structure)
        output_list: List to store output lines
        gitignore_path: Path to .gitignore file
        progress_callback: Callback function(current, total) -> bool for progress updates
                         Returns False to stop processing, True to continue
    """
    if output_list is None:
        output_list = []
        
    # Parse gitignore patterns if provided
    ignore_patterns = parse_gitignore(gitignore_path) if gitignore_path else []
    
    # Count total entries for progress tracking
    total_entries = count_entries(path, ignore_patterns)
    current_entry = 0

    def _print_structure_recursive(current_path: str, current_prefix: str = "") -> bool:
        nonlocal current_entry
        
        try:
            entries = sorted(os.listdir(current_path))
        except PermissionError:
            output_list.append(f"{current_prefix}[Permission Denied]")
            return True
        except FileNotFoundError:
            output_list.append(f"Error: Directory '{current_path}' not found!")
            return True

        for i, entry in enumerate(entries):
            full_path = os.path.join(current_path, entry)
            
            # Skip if path matches gitignore patterns
            if ignore_patterns and should_ignore(full_path, path, ignore_patterns):
                continue
                
            is_last = i == len(entries) - 1
            symbol = "└── " if is_last else "├── "
            output_list.append(f"{current_prefix}{symbol}{entry}")
            
            current_entry += 1
            if progress_callback:
                if not progress_callback(current_entry, total_entries):
                    return False  # Stop processing
            
            if os.path.isdir(full_path):
                next_prefix = "    " if is_last else "│   "
                if not _print_structure_recursive(full_path, current_prefix + next_prefix):
                    return False  # Stop processing
        
        return True  # Continue processing

    if not _print_structure_recursive(path, prefix):
        return []  # Return empty list if stopped
    return output_list
