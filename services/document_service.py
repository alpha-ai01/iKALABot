import os
import csv
from pypdf import PdfReader
from docx import Document
import openpyxl
import mimetypes

# Define supported extensions and their primary purpose
SUPPORTED_EXTENSIONS = {
    '.txt': 'text/plain',
    '.html': 'text/html',
    '.htm': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.xml': 'application/xml',
    '.csv': 'text/csv',
    '.md': 'text/markdown',
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

MAX_FILE_SIZE_MB = 10  # 10MB limit

def validate_file(file_path):
    """Validate file existence and size."""
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found.")
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File size exceeds limit of {MAX_FILE_SIZE_MB}MB.")

def get_file_content(file_path):
    """Extract content from document based on file type."""
    ext = os.path.splitext(file_path)[1].lower()
    validate_file(file_path)
    
    if ext not in SUPPORTED_EXTENSIONS:
        return None, "รูปแบบไฟล์ไม่รองรับ"

    try:
        if ext in ['.txt', '.html', '.htm', '.css', '.js', '.json', '.xml', '.md', '.csv']:
            # Try UTF-8, fallback to latin-1 if fails
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            return content, None
            
        elif ext == '.pdf':
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text, None
            
        elif ext == '.docx':
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs]), None
            
        elif ext == '.xlsx':
            wb = openpyxl.load_workbook(file_path)
            text = ""
            for sheet in wb.worksheets:
                text += f"Sheet: {sheet.title}\n"
                for row in sheet.iter_rows(values_only=True):
                    text += ",".join([str(cell) for cell in row if cell is not None]) + "\n"
            return text, None
            
    except Exception as e:
        return None, f"เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}"

    return None, "รูปแบบไฟล์ไม่รองรับ"
