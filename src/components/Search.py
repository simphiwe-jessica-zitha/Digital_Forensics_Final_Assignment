import os
import string
import json

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus   import stopwords
from nltk.corpus   import wordnet


for _pkg, _path in [
    ("punkt_tab", "tokenizers/punkt_tab"),
    ("stopwords", "corpora/stopwords"),
    ("wordnet", "corpora/wordnet"),
    ("omw-1.4", "corpora/omw-1.4"),
]:
    try:
        nltk.data.find(_path)
    except LookupError:
        nltk.download(_pkg, quiet=True)

_HERE       = os.path.dirname(os.path.abspath(__file__))
_PROJECT    = os.path.abspath(os.path.join(_HERE, "..", ".."))
UPLOADS_DIR = os.path.join(_PROJECT, "evidence", "uploads")
INDEX_FILE  = os.path.join(UPLOADS_DIR, "index.json")

_BASE_STOP_WORDS = set(stopwords.words("english"))

_EXTRA_STOP_WORDS = {
    # email / chat noise
    "re", "fw", "fwd", "cc", "bcc", "hi", "hello", "hey", "dear", "regards",
    "sincerely", "thanks", "thank", "best", "cheers", "sent", "wrote",
    # document noise
    "page", "subject", "date", "from", "to", "attachment",
    # common filler
    "ok", "okay", "yes", "no", "yeah", "nope", "sure", "right",
    # single chars that slip through punctuation strip
    "s", "t", "m", "d", "ll", "ve", "re",
}

STOP_WORDS = _BASE_STOP_WORDS | _EXTRA_STOP_WORDS

def _load_index() -> list:
    if not os.path.exists(INDEX_FILE):
        return []
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _read_txt(file_id: str) -> str:
    path = os.path.join(UPLOADS_DIR, f"{file_id}.txt")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _tokenize(text: str) -> list:
    # 1. lowercase
    text = text.lower()

    # 2. tokenize — splits on whitespace AND punctuation,
    raw_tokens = word_tokenize(text)

    # 3. keep only tokens with at least one alphabetic character
    alpha_tokens = [t for t in raw_tokens if any(c.isalpha() for c in t)]

    # 4. strip punctuation from token edges
    stripped = [t.strip(string.punctuation) for t in alpha_tokens]

    # 5. remove stop words and empty strings
    clean = [t for t in stripped if t and t not in STOP_WORDS]

    return clean

def prepare_evidence() -> list:
    index    = _load_index()
    prepared = []

    for entry in index:
        file_id = entry["id"]
        raw     = _read_txt(file_id)

        if not raw.strip():
            continue

        tokens = _tokenize(raw)

        prepared.append({
            "id":            file_id,
            "original_name": entry.get("original_name", "unknown"),
            "file_type":     entry.get("file_type",     "txt"),
            "source":        entry.get("source",        "unknown"),
            "original_path": entry.get("original_path", ""),
            "tokens":        tokens,
            "token_count":   len(tokens),
        })

    return prepared

#finding synonyms for query
def expand_query(query: str) -> list[str]:
    original_tokens = tokenize_query(query)
    expanded = set(original_tokens)

    for token in original_tokens:
        for syn in wordnet.synsets(token):
            for lemma in syn.lemmas():
                word = lemma.name().lower().replace("_", " ")
                expanded.add(word)

    return list(expanded)


def tokenize_query(query: str) -> list:
    return _tokenize(query)


def match_evidecne (query_tokens:list,evidence:list)->list:
    results=[]
    query_set=set(query_tokens)

    for doc in evidence:
        doc_tokens=doc["tokens"]
        token_poisition:dict[str,list[int]]={}

        for i,token in enumerate(doc_tokens):
            if token in query_set:
                token_poisition.setdefault(token,[]).append(i)

        if not token_poisition:
            continue

        hits=sorted(pos for positions in token_poisition.values() for pos in positions)

        results.append({
            "id": doc["id"],
            "original_name": doc["original_name"],
            "file_type": doc["file_type"],
            "source": doc["source"],
            "matched_tokens": token_poisition,
            "match_count": len(hits),
            "hit_positions": hits,
            "token_count": doc["token_count"],
            "score": len(hits) / (doc["token_count"] or 1)

        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results



def run_search(query: str) -> dict:
    # 1. validate
    query = query.strip()
    if not query:
        return {
            "query":        "",
            "query_tokens": [],
            "evidence":     [],
            "file_count":   0,
            "error":        "Query is empty.",
        }

    # 2. tokenize the query
    query_tokens = expand_query(query)

    # 3. load + tokenize all evidence files
    try:
        evidence = prepare_evidence()
    except Exception as e:
        return {
            "query":        query,
            "query_tokens": query_tokens,
            "evidence":     [],
            "file_count":   0,
            "error":        f"Failed to load evidence: {e}",
        }

    print("Evidence Json:")
    print(json.dumps(evidence, indent=4))

    #$4. Match the query token to the token in the evidence

    matches=match_evidecne(query_tokens,evidence)
    matched_files=[match["original_name"] for match in matches]
    print("matches:", json.dumps(matches, indent=4))
    return {
        "query":        query,
        "query_tokens": query_tokens,
        "evidence":     matches,
        "matched_files": matched_files,
        "match_count":  len(matches),
        "file_count":   len(matches),
        "error":        None,
    }
