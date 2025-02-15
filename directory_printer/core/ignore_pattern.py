import re

class IgnorePattern:
    def __init__(self, pattern: str, is_negation: bool = False, is_dir_only: bool = False):
        self.original_pattern = pattern
        self.is_negation = is_negation
        self.is_dir_only = is_dir_only
        # Remove leading ! for negation (already handled in is_negation)
        pattern = pattern[1:] if is_negation else pattern
        self.regex_pattern = self._convert_to_regex(pattern)

    def _convert_to_regex(self, pattern: str) -> str:
        """Convert gitignore pattern to regex pattern with proper escaping"""
        # Handle directory-only pattern
        if pattern.endswith('/'):
            pattern = pattern[:-1]  # Remove trailing slash
        
        # Handle leading slash
        anchored = pattern.startswith('/')
        if anchored:
            pattern = pattern[1:]  # Remove leading /
        
        # Escape special regex characters except * and ?
        pattern = re.escape(pattern)
        # Unescape * and ? since we want to handle them specially
        pattern = pattern.replace(r'\*', '*').replace(r'\?', '?')
        
        # Handle special characters
        pattern = (
            pattern
            .replace('**', '.*')  # ** matches anything including /
            .replace('*', '[^/]*')  # * matches anything except /
            .replace('?', '[^/]')  # ? matches any single character except /
        )
        
        # Make sure pattern matches full path component
        if anchored:
            pattern = f'^{pattern}'  # Anchor to start
        else:
            pattern = f'(?:^|/){pattern}'  # Can match at start or after /
            
        if self.is_dir_only:
            pattern = f'{pattern}(?:/.*)?$'  # Match directory and optionally its contents
        else:
            pattern = f'{pattern}(?:$|/)'  # Match file or directory
            
        return pattern

    def matches(self, path: str) -> bool:
        """Check if path matches this pattern"""
        return bool(re.match(self.regex_pattern, path)) 