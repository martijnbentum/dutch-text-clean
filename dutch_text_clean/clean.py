from . import cgn_utils
import re
import string
import unicodedata

def clean_dutch_cgn(text):
    "Minimal Dutch + CGN-ish cleaning: keep apostrophe clitics and keep EOL markers"
    text = normalize_unicode(text)
    text = normalize_quotes_dashes(text)
    text = normalize_ellipsis_to_eol(text)
    tokens = remove_cgn_codes_from_tokens(text.split(), cgn_utils.star_list)
    tokens = expand_clitic_tokens(tokens, cgn_utils.cgn_clitic_map)
    tokens = remove_unwanted_tokens(tokens, cgn_utils.remove_words
    text = ' '.join(tokens)
    text = keep_allowed_chars(text)
    text = remove_non_word_dashes(text)
    text = lowercase(text)
    text = normalize_whitespace(text)
    text = collapse_multiple_eols(text)
    return text

def remove_unwanted_tokens(tokens, remove_words):
    '''Remove unwanted tokens from a list of tokens.
    '''
    output = []
    for token in tokens:
        tok = token.strip(string.punctuation)
        if tok in remove_words:
            continue
        output.append(token)
    return output


def normalize_unicode(text):
    '''Normalize unicode to NFKC.
    e.g. unicodedata.normalize("NFKC", "ﬁlm ①") -> "film 1"
    '''
    return unicodedata.normalize('NFKC', text)

def normalize_quotes_dashes(text):
    '''Normalize typographic quotes/dashes to plain ASCII.
    '''
    replacements = {'’': "'",'‘': "'",'“': '"','”': '"','–': '-','—': '-',}
    for src, tgt in replacements.items():
        text = text.replace(src, tgt)
    return text

def lowercase(text):
    'Lowercase text'
    return text.lower()

def normalize_question_and_exclamation_mark(text):
    '''Collapse repeated sentence-final punctuation to a single ? or !
    '''
    def repl(match):
        seq = match.group(0)
        return '?' if '?' in seq else '!'
    return re.sub(r'[?!]{2,}', repl, text)

def normalize_ellipsis_to_eol(text):
    "CGN: treat ellipsis (...) as an end-of-line marker"
    text = normalize_question_and_exclamation_mark(text)
    text = re.sub(r'\.{3,}', '.', text)     # '...' or longer -> newline
    text = re.sub(r'\s+([.?!])', r'\1', text)
    return text

def normalize_whitespace(text):
    '''Collapse spaces/tabs.
    ''' 
    return ' '.join(text.split())

def keep_allowed_chars(text, allowed = None):
    '''Keep only letters, digits, whitespace, and: ' , . ? ! -
    '''
    if allowed is None:
        allowed = set(["'", ",", ".", "?", "!", "-"])
    out = []
    for ch in text:
        if ch.isalpha() or ch.isdigit() or ch in allowed or ch.isspace():
            out.append(ch)
    return ''.join(out)

def remove_cgn_codes(token, star_list):
    '''Remove trailing CGN codes like *v even when followed by punctuation
    '''
    m = re.match(r"^(.*?)(\*[^ \t\r\n.,;:!?]+)?([.,;:!?]+)?$", token)
    if not m:
        return token

    base, code, punct = m.group(1), m.group(2), m.group(3)

    if code in star_list:
        return base + (punct or '')
    return token

def remove_cgn_codes_from_tokens(tokens, star_list = None):
    if star_list is None:
        star_list = cgn_utils.star_list
    'Apply CGN code removal to a list of tokens'
    return [remove_cgn_codes(tok, star_list) for tok in tokens]

def expand_clitic_tokens(tokens, clitic_map = None):
    '''Expand clitics in a list of tokens.
    '''
    if clitic_map is None:
        clitic_map = cgn_utils.cgn_clitic_map
    expanded = []
    for tok in tokens:
        if tok in clitic_map:
            expanded.extend(clitic_map[tok].split())
        else:
            expanded.append(tok)
    return expanded

def remove_non_word_dashes(text):
    '''Remove dashes not occurring inside words'''
    # remove dashes with whitespace on at least one side
    text = re.sub(r'\s+-\s+', ' ', text)   # " - " -> space
    text = re.sub(r'(^|\s)-(\s|$)', r'\1', text)  # leading/trailing dashes
    return text

def collapse_multiple_eols(text):
    '''map two or more sentence end markers (.) to a single one.
    '''
    def repl(match):
        seq = match.group(0)
        return '?' if '?' in seq else '!'
    return re.sub(r'[.?!]{2,}', repl, text)

test_sentences = [
    "  'k   weet   't   niet...   z'n   fiets*a  is  kapot!!??  ",
    "d’r  jas*d,  ja  —  die  heb  'k   gezien...  echt!!! ",
    "'tis   wel  mooi??!!   maar   m’n  huis*z   nee... ",
    "  ‘k   zag  'm   lopen*v,   en   d’rin  stond  iets?? ",
    "Da’s   raar . . .   ‘t   klopt*d  niet!!! ",
    "  z’n  broer*v  zei:   “nee!!”   maar  'k  denk  ??  anders ",
    "  m’n   auto*a kapot...  'k  ben  boos!!! ",
    "  d’r  hond*n   liep  weg . . .  ‘t   was  stil?? ",
    "ja   ...   nee   ?! ?!   'k   snap  't  echt  niet*d ",
    "  ‘t   is   klaar!!   z’n   idee*x  werkte  niet . . .  ",
    "dit  -  echt  -  werkt  niet!!!",
    "-  nee  -  zo  bedoel  ik  het  niet",
    "co-op  is  iets  anders  dan  co op  -  echt!",
    "dit-is-goed  maar  dit  -  is  fout",
]

def small_test():
    for sentence in test_sentences:
        print("Original: ", repr(sentence))
        cleaned = clean_dutch_cgn(sentence)
        print("Cleaned:  ", repr(cleaned))
        print()


