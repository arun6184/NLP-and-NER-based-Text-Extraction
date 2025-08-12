import re

SECTION_SKIP_HEADS = [
    "Chief Complaints",
    "Clinical Findings",
    "Advice",
    "Follow Up",
    "Diagnosis",
]

def normalize_text(text: str) -> str:
    t = text.replace("–", "-").replace("—", "-")
    t = re.sub(r"[|•]+", " ", t)
    t = re.sub(r"\s+\n\s+", "\n", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = t.strip()
    # normalize common OCR confusions lightly
    t = t.replace(" O ", " 0 ")
    return t

def split_into_candidate_lines(text: str):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # drop known non-Rx sections until the Rx table begins
    pruned = []
    skip = False
    for ln in lines:
        # toggle skipping for complaint/clinical sections
        if any(h.lower() in ln.lower() for h in SECTION_SKIP_HEADS):
            skip = True
            continue
        # Rx table typically starts around "R" or a numbered medicine list
        if re.match(r"^\s*R\s*$", ln) or re.match(r"^\s*\d+\)", ln):
            skip = False
        if skip:
            continue
        pruned.append(ln)
    return pruned
