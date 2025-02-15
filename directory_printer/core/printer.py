import os
from typing import List, Optional, Callable
from directory_printer.core.ignore_pattern import IgnorePattern


def parse_gitignore(gitignore_path: str) -> List[IgnorePattern]:
    """Parse gitignore file and return list of patterns with metadata"""
    if not os.path.exists(gitignore_path):
        return []
    
    with open(gitignore_path, 'r') as f:
        patterns = []
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check for negation
            is_negation = line.startswith('!')
            # Check for directory-only pattern
            is_dir_only = line.rstrip().endswith('/')
            
            # Remove trailing spaces
            pattern = line.rstrip('/ ')
            if is_dir_only:
                pattern = pattern + '/'
                
            patterns.append(IgnorePattern(pattern, is_negation, is_dir_only))
        return patterns


def should_ignore(path: str, base_path: str, ignore_patterns: List[IgnorePattern]) -> bool:
    """Check if path should be ignored based on gitignore patterns with proper precedence"""
    if not ignore_patterns:
        return False
    
    # Get relative path from base directory
    rel_path = os.path.relpath(path, base_path)
    # Convert Windows path separators to Unix style
    rel_path = rel_path.replace('\\', '/')
    
    # Track if path is matched by any pattern
    is_ignored = False
    matched_by_negation = False
    
    # Check each pattern in order
    for pattern in ignore_patterns:
        if pattern.matches(rel_path):
            if pattern.is_negation:
                matched_by_negation = True
                is_ignored = False
            elif not matched_by_negation:  # Only set to ignored if not matched by negation
                is_ignored = True
            
        # Also check parent directories
        parts = rel_path.split('/')
        for i in range(len(parts)):
            partial_path = '/'.join(parts[:i+1])
            if pattern.matches(partial_path):
                if pattern.is_negation:
                    matched_by_negation = True
                    is_ignored = False
                elif not matched_by_negation:  # Only set to ignored if not matched by negation
                    is_ignored = True
                
    return is_ignored


def count_entries(path: str, ignore_patterns: List[IgnorePattern] = None) -> int:
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

        # Filter out ignored entries before processing
        filtered_entries = []
        for entry in entries:
            full_path = os.path.join(current_path, entry)
            if not ignore_patterns or not should_ignore(full_path, path, ignore_patterns):
                filtered_entries.append(entry)

        for i, entry in enumerate(filtered_entries):
            full_path = os.path.join(current_path, entry)
            is_last = i == len(filtered_entries) - 1
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
