import re

def sanitize_to_plain_text(text: str) -> str:
    """Sanitizes text to plain text only, removing markdown, symbols, etc."""
    # Remove markdown/symbols (keep Thai, English, Digits, whitespace EXCEPT \n)
    sanitized = re.sub(r'[^a-zA-Z0-9\u0e00-\u0e7f\s\n]', ' ', text)
    # Deduplicate whitespace (excluding \n)
    sanitized = re.sub(r'[ \t\r\f\v]+', ' ', sanitized)
    # Deduplicate multiple newlines
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized).strip()
    return sanitized

def remove_duplicates(text: str) -> str:
    """Removes consecutive duplicate paragraphs."""
    paragraphs = text.split('\n\n')
    unique_paragraphs = []
    for p in paragraphs:
        if not unique_paragraphs or p.strip() != unique_paragraphs[-1].strip():
            unique_paragraphs.append(p)
    return '\n\n'.join(unique_paragraphs)

def clean_ai_response(text: str) -> str:
    """Combines sanitization and deduplication."""
    return remove_duplicates(sanitize_to_plain_text(text))
