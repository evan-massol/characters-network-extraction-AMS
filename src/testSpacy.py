import spacy as sp
import fitz
import re

def pdf_to_text(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
    return text

corpus = pdf_to_text("src/pdf/Fondation_sample.pdf")
corpus = re.sub(r'\s+', ' ', corpus)

nlp = sp.load("fr_core_news_md")
doc = nlp(corpus)

LP = []
for ent in doc.ents:
    if ent.label == "PER":
        LP.add(ent.text)

print(LP)