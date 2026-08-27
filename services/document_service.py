import os
import csv
from pypdf import PdfReader
from docx import Document
import openpyxl

def process_document(file_path, chunk_size=30000):
    ext = os.path.splitext(file_path)[1].lower()
    
    # Text-based source/doc formats
    text_formats = {
        '.txt', '.md', '.py', '.js', '.mjs', '.ts', '.tsx', '.css', '.html', '.htm',
        '.json', '.xml', '.yaml', '.yml'
    }
    
    content = ""
    if ext in text_formats:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
    elif ext == '.pdf':
        reader = PdfReader(file_path)
        for page in reader.pages:
            content += page.extract_text() + "\n"
        
    elif ext == '.docx':
        doc = Document(file_path)
        content = "\n".join([p.text for p in doc.paragraphs])
        
    elif ext == '.csv':
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            content = "\n".join([",".join(row) for row in reader])
            
    elif ext == '.xlsx':
        wb = openpyxl.load_workbook(file_path, data_only=True)
        for sheet in wb.worksheets:
            content += f"Sheet: {sheet.title}\n"
            for row in sheet.iter_rows(values_only=True):
                content += ",".join([str(cell) for cell in row if cell is not None]) + "\n"
        
    else:
        return ["รูปแบบไฟล์ไม่รองรับ"]
        
    # Split content into chunks
    if not content:
        return []
        
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunks.append(content[i:i+chunk_size])
    return chunks
