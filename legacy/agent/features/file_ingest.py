import os
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def ingest_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
        if not OCR_AVAILABLE:
            return {"type": "image", "content": "OCR not available - pytesseract and PIL not installed", "error": True}
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return {"type": "image", "content": text}
        except Exception as e:
            return {"type": "image", "content": f"Error processing image: {str(e)}", "error": True}
    elif ext == '.pdf':
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return {"type": "pdf", "content": text}
        except ImportError:
            return {"type": "pdf", "content": "PyPDF2 not available", "error": True}
        except Exception as e:
            return {"type": "pdf", "content": f"Error processing PDF: {str(e)}", "error": True}
    elif ext == '.docx':
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return {"type": "docx", "content": text}
        except ImportError:
            return {"type": "docx", "content": "python-docx not available", "error": True}
        except Exception as e:
            return {"type": "docx", "content": f"Error processing DOCX: {str(e)}", "error": True}
    elif ext in ['.txt', '.md', '.py']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return {"type": ext[1:], "content": text}
        except Exception as e:
            return {"type": ext[1:], "content": f"Error reading file: {str(e)}", "error": True}
    else:
        return {"type": "unknown", "content": f"Unsupported file type: {ext}"}