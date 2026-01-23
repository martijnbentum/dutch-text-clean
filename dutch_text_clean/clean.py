import re
import unicodedata

def normalize_unicode(text):
    '''Normalize unicode to NFKC.
    e.g. unicodedata.normalize("NFKC", "ﬁlm ①") -> "film 1"
    '''
    return unicodedata.normalize('NFKC', text)


def normalize_quotes_dashes(text):
    'Normalize typographic quotes/dashes to plain ASCII.'
    replacements = {
        '’': "'",
        '‘': "'",
        '“': '"',
        '”': '"',
        '–': '-',
        '—': '-',
    }
    for src, tgt in replacements.items():
        text = text.replace(src, tgt)
    return text


def lowercase(text):
    'Lowercase text'
    return text.lower()

def normalize_sentence_punctuation(text):
    '''Collapse repeated sentence-final punctuation to a single ? or !
    '''
    def repl(match):
        seq = match.group(0)
        return '?' if '?' in seq else '!'
    return re.sub(r'[?!]{2,}', repl, text)

def normalize_ellipsis_to_eol(text):
    "CGN: treat ellipsis (...) as an end-of-line marker"
    text = normalize_sentence_punctuation(text)
    text = re.sub(r'\.{3,}', '.', text)     # '...' or longer -> newline
    text = re.sub(r'\s+([.?!])', r'\1', text)
    return text

def normalize_whitespace(text):
    '''Collapse spaces/tabs.
    ''' 
    return ' '.join(text.split())

def keep_allowed_chars(text):
    "Keep only letters, digits, whitespace, and: ' , . ? ! -"
    allowed = set(["'", ",", ".", "?", "!", "-"])
    out = []
    for ch in text:
        if ch.isalpha() or ch.isdigit() or ch in allowed or ch.isspace():
            out.append(ch)
    return ''.join(out)

def remove_cgn_codes(token, star_list):
    'Remove trailing CGN codes like *v even when followed by punctuation'
    m = re.match(r"^(.*?)(\*[^ \t\r\n.,;:!?]+)?([.,;:!?]+)?$", token)
    if not m:
        return token

    base, code, punct = m.group(1), m.group(2), m.group(3)

    if code in star_list:
        return base + (punct or '')
    return token

def remove_cgn_codes_from_tokens(tokens, star_list):
    'Apply CGN code removal to a list of tokens'
    return [remove_cgn_codes(tok, star_list) for tok in tokens]


def clean_dutch_cgn(text):
    "Minimal Dutch + CGN-ish cleaning: keep apostrophe clitics and keep EOL markers"
    text = normalize_unicode(text)
    text = normalize_quotes_dashes(text)
    text = lowercase(text)
    text = cgn_normalize_ellipsis_to_eol(text)
    text = cgn_normalize_apostrophes(text)
    text = remove_punct_keep_eol_and_apostrophe(text)
    text = normalize_whitespace_keep_newlines(text)
    return text

