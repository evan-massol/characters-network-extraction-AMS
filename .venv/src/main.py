import re
import fitz
from collections import Counter
from unidecode import unidecode

def pdf_to_text(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
    return text

corpus = pdf_to_text("src/pdf/Fondation_sample.pdf")
corpus = re.sub(r'\s+', ' ', corpus)
tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ\-']+", corpus)

def filter_antidict(file):
    """Load anti-dictionary words from a file."""
    with open(file, 'r', encoding='utf-8') as f:
        return set(unidecode(line.strip()) for line in f)

def generate_candidates(tokens):
    """Generate candidate words from tokens."""
    L = []
    anti_words = filter_antidict('src/fonctionnels_fr.txt')
    for i, token in enumerate(tokens):
        if token.istitle() and unidecode(token.lower()) not in anti_words:
            L.append(token)
            if i+2 < len(tokens) and tokens[i+1].istitle() and tokens[i+2].istitle():
                L.remove(token)
                L.append(token + " " + tokens[i+1] + " " + tokens[i+2])
            elif i+1 < len(tokens) and tokens[i+1].istitle():
                L.remove(token)
                L.append(token + " " + tokens[i+1])
    return L

L = generate_candidates(tokens)

L = Counter(L)
LP = [word for word, count in L.items() if count > 2]

def generate_entities(L):
    """Filter out entities based on an anti-dictionary."""
    return [token for token in L if unidecode(token.lower()) not in filter_antidict('src/fonctionnels_fr.txt')]

LP = generate_entities(LP)
LP.sort()
print(LP, len(LP))