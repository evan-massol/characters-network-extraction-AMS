import fitz
from unidecode import unidecode

def filter_antidict(file):
    """Load anti-dictionary words from a file."""
    with open(file, 'r', encoding='utf-8') as f:
        return set(unidecode(line.strip()) for line in f)
    
    
def pdf_to_text(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
    return text

def clean_entity_name(name):
    """Remove unwanted newlines and extra spaces from entity names."""
    return ' '.join(name.replace('\n', ' ').split())