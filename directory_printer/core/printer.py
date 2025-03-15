import os
from typing import List, Optional, Callable
import pathspec


def parse_gitignore(gitignore_path: str) -> Optional[pathspec.PathSpec]:
    """Parse gitignore file and return a PathSpec object"""
    if not os.path.exists(gitignore_path):
        return None
    
    with open(gitignore_path, 'r') as f:
        # Read and filter out empty lines and comments
        patterns = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith('#')
        ]
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)


def should_ignore(path: str, base_path: str, spec: Optional[pathspec.PathSpec]) -> bool:
    """Check if path should be ignored based on gitignore patterns"""
    if not spec:
        return False
    
    # Get relative path from base directory
    rel_path = os.path.relpath(path, base_path)
    # Convert Windows path separators to Unix style and normalize path
    rel_path = rel_path.replace('\\', '/')
    
    # Check if the path itself matches
    if spec.match_file(rel_path):
        return True
        
    # Check if any parent directory matches
    path_parts = rel_path.split('/')
    for i in range(len(path_parts)):
        partial_path = '/'.join(path_parts[:i+1])
        if spec.match_file(partial_path) or spec.match_file(partial_path + '/'):
            return True
            
    return False


def count_entries(path: str, spec: Optional[pathspec.PathSpec] = None) -> int:
    """Count total number of entries for progress tracking"""
    total = 0
    for root, dirs, files in os.walk(path):
        if spec and should_ignore(root, path, spec):
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
    spec = parse_gitignore(gitignore_path) if gitignore_path else None
    
    # Count total entries for progress tracking
    total_entries = count_entries(path, spec)
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
            if not spec or not should_ignore(full_path, path, spec):
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
