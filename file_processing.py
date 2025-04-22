import docx2txt
from PyPDF2 import PdfReader
import os

def read_file(file):
    """Reads content from a file path or uploaded file and returns it as text."""
    content = ""

    if file is None:
        return content

    try:
        # If file is a string (i.e., file path)
        if isinstance(file, str):
            ext = os.path.splitext(file)[1].lower()

            if ext == '.txt':
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()

            elif ext == '.pdf':
                with open(file, 'rb') as f:
                    pdf_reader = PdfReader(f)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            content += text

            elif ext == '.docx':
                content = docx2txt.process(file)

        # If file is an uploaded FileStorage object (e.g., from Flask)
        else:
            if file.mimetype == "text/plain":
                content = file.read().decode("utf-8")

            elif file.mimetype == "application/pdf":
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text

            elif file.mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = docx2txt.process(file)

    except Exception as e:
        print(f"Error reading file: {e}")

    return content
