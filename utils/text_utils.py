import re

def clean_ai_response(text: str) -> str:
    """Cleans AI response by removing Markdown formatting and whitespace."""
    if not text:
        return ""

    # Remove code fences
    text = re.sub(r'```[a-zA-Z]*\n', '', text)
    text = re.sub(r'```', '', text)

    # Remove bold and italic (careful not to break 2 * 5)
    # This pattern looks for markdown markers at the start/end of words or lines
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    # Remove headings
    text = re.sub(r'###\s+', '', text)
    text = re.sub(r'##\s+', '', text)
    text = re.sub(r'#\s+', '', text)

    # Remove horizontal rules
    text = re.sub(r'---', '', text)

    # Remove markdown link formatting [text](url) -> text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text
