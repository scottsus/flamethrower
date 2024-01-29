"""
A bunch of helper functions for the shell.
"""

def is_capitalized(text: str) -> bool:
    if not text:
        return False
    return text[0].isupper()

def is_single_key(data: bytes) -> bool:
    return len(data) == 1

def is_prompt_newline(data: bytes) -> bool:
    return data.startswith(b'\r\x1b')

def is_ansi_escape_sequence(data: bytes) -> bool:
    ansi_escape_sequences = [
        b' ',       # Space character, not an ANSI sequence.
        b'[0m',     # Reset / Normal: All attributes off.
        b'[1m',     # Bold or increased intensity.
        b'[4m',     # Underline: Single.
        b'[24m',    # Not underlined: Underline off.
        b'[31m',    # Foreground color: Red.
        b'[32m',    # Foreground color: Green.
        b'[33m',    # Foreground color: Yellow.
        b'[39m',    # Default foreground color.
        b'[90m',    # Foreground color: Bright black (gray).
        b'[K',      # Erase line: Clears part of the line.
        b'[11D',    # Cursor movement: Move cursor left by 11 spaces.
        b'[13D',    # Cursor movement: Move cursor left by 13 spaces.
        b'[18D',    # Cursor movement: Move cursor left by 18 spaces.
        b'[?2',     # Incomplete sequence, possibly related to mode setting.
    ]

    # Sequence starting with escape dataacter (zsh-syntax-highlighting)
    if data.startswith(b'\x1b'):
        return any(data.startswith(b'\x1b' + seq) for seq in ansi_escape_sequences)

    # Sequence starting with backspaces (zsh-autocomplete)
    backspace = b'\x08'
    index = 0
    while index < len(data) and data[index:index + 1] == backspace:
        index += 1
    if any(data.startswith(backspace * index + b'\x1b' + seq) for seq in ansi_escape_sequences):
        return True

    return False

def get_cleaned_data(data: bytes) -> bytes:
    if is_ansi_escape_sequence(data):
        return b''
    
    if is_single_key(data):
        return b''
    
    return data