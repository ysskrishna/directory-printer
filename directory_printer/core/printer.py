import os
from typing import List, Optional


def print_structure(
    path: str, prefix: str = "", output_list: Optional[List[str]] = None
) -> List[str]:
    if output_list is None:
        output_list = []

    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        output_list.append(f"{prefix}[Permission Denied]")
        return output_list
    except FileNotFoundError:
        output_list.append(f"Error: Directory '{path}' not found!")
        return output_list

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        symbol = "└── " if is_last else "├── "
        full_path = os.path.join(path, entry)
        output_list.append(f"{prefix}{symbol}{entry}")
        if os.path.isdir(full_path):
            next_prefix = "    " if is_last else "│   "
            print_structure(full_path, prefix + next_prefix, output_list)

    return output_list
