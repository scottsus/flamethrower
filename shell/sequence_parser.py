
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
        b' ',
        b'[0m',
        b'[1m',
        b'[4m',
        b'[24m',
        b'[31m',
        b'[32m',
        b'[33m',
        b'[39m',
        b'[90m',
        b'[K',
        b'[11D',
        b'[13D',
        b'[18D',
        b'[?2',  # Note: This seems to be an incomplete sequence.
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

    # TODO: there is still some noise that is difficult to remove
    noise = (
        b'\r\n\x1b[1m\x1b[3m%\x1b[23m\x1b[1m\x1b[0m'
        b'                                                                               ' # 80 spaces
        b'\r \r\n'
    )
    # if data.endswith(noise):
    #     return True

    return False