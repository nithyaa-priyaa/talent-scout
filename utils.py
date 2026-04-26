from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
import re

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')


# ---------- TEXT EXTRACTION ----------
def extract_text(file):
    try:
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + " "

        return text.strip()
    except:
        return ""


# ---------- DOCUMENT CLASSIFICATION ----------
def classify_document(text):
    if not text or len(text.strip()) == 0:
        return "empty"

    words = text.split()

    if len(words) < 10:
        return "too_small"

    text_lower = text.lower()

    keywords = ["experience", "education", "skills", "projects"]
    keyword_hits = sum(1 for k in keywords if k in text_lower)

    has_email = "@" in text
    has_numbers = bool(re.search(r"\d", text))

    score = keyword_hits + has_email + has_numbers

    if score >= 3:
        return "resume"
    elif score == 2:
        return "maybe_resume"
    else:
        return "not_resume"


# ---------- KEYWORD SCORE ----------
def keyword_score(jd, text):
    jd_words = set(jd.lower().split())
    text_words = set(text.lower().split())

    if len(jd_words) == 0:
        return 0

    return len(jd_words & text_words) / len(jd_words)


# ---------- COSINE SIM ----------
def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ---------- RANKING ----------
def rank_resumes(jd, resumes):
    jd_lower = jd.lower().strip()

    valid = []
    rejected = []

    # ---------- NAME SEARCH ----------
    if "resume of" in jd_lower or len(jd.split()) <= 5:
        search_term = jd_lower.replace("resume of", "").strip()

        for r in resumes:
            if r["type"] not in ["resume", "maybe_resume"]:
                rejected.append(r)
                continue

            if search_term and search_term in r["text"].lower():
                r["score"] = 0.99
            else:
                r["score"] = 0.05

            valid.append(r)

        return sorted(valid, key=lambda x: x["score"], reverse=True), rejected

    # ---------- VECTOR SEARCH ----------
    jd_vec = model.encode([jd])[0]

    for r in resumes:

        if r["type"] not in ["resume", "maybe_resume"]:
            rejected.append(r)
            continue

        text = r["text"]

        # semantic
        res_vec = model.encode([text])[0]
        sim = cosine(jd_vec, res_vec)

        # keyword
        kw = keyword_score(jd, text)

        # ---------- HYBRID SCORE ----------
        score = (0.7 * sim) + (0.3 * kw)

        # ---------- PENALTIES ----------
        word_count = len(text.split())

        if word_count < 40:
            score *= 0.6   # too small penalty

        if word_count > 1000:
            score *= 0.9   # long noisy docs

        r["score"] = score
        valid.append(r)

    return sorted(valid, key=lambda x: x["score"], reverse=True), rejected