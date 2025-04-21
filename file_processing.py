import docx2txt
from PyPDF2 import PdfReader

def read_file(file):
    """Reads content from a file and returns it as text."""
    content = ""
    if file is None:
        return content

    try:
        if file.mimetype == "text/plain":
            content = file.read().decode("utf-8")
        elif file.mimetype == "application/pdf":
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:  # Ensure only non-empty text is added
                    content += text
        elif file.mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            content = docx2txt.process(file)
        
    except Exception as e:
        # Log or print error if needed
        print(f"Error reading file: {e}")

    return content
