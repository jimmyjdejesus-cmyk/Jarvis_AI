import os
from PIL import Image
import pytesseract

def ingest_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return {"type": "image", "content": text}
    elif ext == '.pdf':
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return {"type": "pdf", "content": text}
    elif ext == '.docx':
        import docx
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return {"type": "docx", "content": text}
    elif ext in ['.txt', '.md', '.py']:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return {"type": ext[1:], "content": text}
    else:
        return {"type": "unknown", "content": None}