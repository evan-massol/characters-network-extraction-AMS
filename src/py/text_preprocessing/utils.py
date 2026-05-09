import fitz
import re
from unidecode import unidecode


def filter_antidict(file : str) -> set:
    """Load anti-dictionary words from a file."""
    with open(file, 'r', encoding='utf-8') as f:
        return set(unidecode(line.strip()) for line in f)


def pdf_to_text(pdf_path : str) -> str:
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
            text += " -_ENDPAGE_- "
    return text

def clean_entity_name(name : str | list) -> str:
    """Remove unwanted newlines and extra spaces from entity names."""
    if isinstance(name, list):
        val = ' '.join(str(name) for name in name)
        return val
    return ' '.join(name.replace('\n', ' ').split())

def supprPageNum(texte : str) -> str:
    print("Suppression des numéros de pages...")
    texte = re.sub(r'\ufffd\s*\d+\s*\ufffd', ' ', texte)
    texte = re.sub(r'- *\d -', ' ', texte)
    return texte

# Remove incomplete sentences
def supprCutSentences(texte : str) -> str:
    print("Suppression des phrases incomplètes...")
    matches = list(re.finditer(r"( -_ENDPAGE_- )", texte))
    for match in reversed(matches):             #Start from the end to avoid disrupting indices
        avant = texte[:match.start()]
        apres = texte[match.end():]
        last_ponct = max(avant.rfind('.'), avant.rfind('!'), avant.rfind('?'))
        if last_ponct != -1:
            avant = avant[:last_ponct+1]        #Remove after the last punctuation
        else:
            avant = ""

        texte = avant + " -_ENDPAGE_- " + apres #Keep markers to process post-marker sentences

    matches = list(re.finditer(r"( -_ENDPAGE_- )", texte))
    for match in reversed(matches):                       #Start from the beginning to avoid disrupting indices
        avant = texte[:match.start()]
        apres = texte[match.end():]
        if len(apres)!=0:
            premiere_lettre = next((c for c in apres if c.isalpha()))
            if not premiere_lettre.isupper():              #If no uppercase letter right after the marker
                apres_poncts = [apres.find('.'), apres.find('!'), apres.find('?')]
                if not all(x == -1 for x in apres_poncts):
                    apres_poncts = [x for x in apres_poncts if x != -1]
                first_ponct = min(apres_poncts)
                if first_ponct != -1:
                    apres = apres[first_ponct+1:]   #Remove before the first punctuation
                else:
                    apres = ""

        texte = avant + apres

    return texte

# Remove part titles
def supprPartsTitle(texte : str) -> str:
    print("Suppression des titres de parties...")
    texte = re.sub(r'\n[A-ZÈ]+ PARTIE \n \n \n[A-ZÀÂÇÉÈÊËÎÏÔÙÛ ]+', '', texte)
    return texte

# Remove chapter numbers
def supprChapterNum(texte : str) -> str:
    print("Suppression des numéros de chapitres...")
    texte = re.sub(r'\n\b[IVXLCDM]+(?!\')\b \n', '', texte)
    return texte

def removeChar(texte : str) -> str:
    texte = re.sub(r'\n', ' ', texte)
    texte = re.sub(r'’', '\'', texte)
    texte = re.sub(r'—', ' ', texte)      # traitement U+2014
    texte = re.sub(r'―', ' ', texte)      # traitement U+2015
    texte = re.sub(r'‖', ' ', texte)
    texte = re.sub(r' - ', ' ', texte)
    texte = re.sub(r' {2,}', ' ', texte)
    return texte


###CONSTANTS
ANTI_DICT = filter_antidict('fonctionnels_fr.txt')