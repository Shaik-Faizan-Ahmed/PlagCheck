import nltk
from nltk.tokenize import sent_tokenize

# Make sure necessary data is available
nltk.download('punkt')

def get_sentences(text):
    """Splits text into sentences."""
    if not text:
        return []
    return sent_tokenize(text)
