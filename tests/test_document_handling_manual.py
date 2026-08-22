import os
from services.document_service import get_file_content

def test_document_processing():
    # Setup: Create dummy files
    test_files = {
        'test.txt': 'Hello World',
        'test.html': '<html><body><h1>Test</h1></body></html>',
        'test.json': '{"key": "value"}',
        'test.md': '# Title\nContent'
    }
    
    for filename, content in test_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
    print("Testing document extraction...")
    
    for filename in test_files.keys():
        content, error = get_file_content(filename)
        if error:
            print(f"FAILED: {filename} - {error}")
        else:
            print(f"PASSED: {filename} - Content length: {len(content)}")
        
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

    # Test unsupported
    with open('test.exe', 'wb') as f:
        f.write(b'binary')
    _, error = get_file_content('test.exe')
    if error == "รูปแบบไฟล์ไม่รองรับ":
        print("PASSED: Unsupported file handling")
    else:
        print(f"FAILED: Unsupported file handling - {error}")
    
    if os.path.exists('test.exe'):
        os.remove('test.exe')

if __name__ == "__main__":
    test_document_processing()
