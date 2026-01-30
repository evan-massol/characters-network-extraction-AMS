import re
from collections import Counter
from unidecode import unidecode
from py.text_preprocessing.utils import filter_antidict, pdf_to_text

corpus = pdf_to_text("pdf/Fondation_sample.pdf")
corpus = re.sub(r'\s+', ' ', corpus)
tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ\-']+", corpus)


def generate_candidates(tokens):
    """Generate candidate words from tokens."""
    L = []
    anti_words = filter_antidict('fonctionnels_fr.txt')
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

LP = [entity for entity in LP]
LP.sort()
print(LP, "\n\n", len(LP))