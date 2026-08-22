import os
import re

def get_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower()

def read_file_range(file_path, start_line=1, end_line=None):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start = max(0, start_line - 1)
    end = end_line if end_line else len(lines)
    
    return "".join(lines[start:end])

def targeted_edit(file_path, search_pattern, new_content):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace using regex pattern
    new_content_full = re.sub(search_pattern, new_content, content, count=1)
    
    if new_content_full == content:
        return "No changes made (pattern not found or content identical)."
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content_full)
        
    return "File updated successfully."
