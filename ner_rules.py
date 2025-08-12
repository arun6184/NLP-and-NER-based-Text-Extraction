# ner_rules.py
import re
from typing import Optional, Dict, Tuple

# Numbered Rx lines with a form label (e.g., "1) TAB. ...", "3) CAP, ...")
LINE_FORM_RE = re.compile(
    r"^\s*\d+\)\s*(Tab|Tablet|Cap|Capsule|Syrup|Syp|Susp|Inj|Solution)[\.,]?\s*",
    re.I
)

# Totals like "(Tot:8 Tab)" to ignore completely
TOTAL_RE = re.compile(
    r"^\(?\s*Tot\s*:\s*\d+\s*(Tab|Tabs?|Cap|Caps)\)?$",
    re.I
)

# Duration and frequency patterns
DURATION_RE = re.compile(r"\b(\d+)\s*(day|days|week|weeks)\b", re.I)
FREQ_TRIPLET_RE = re.compile(r"\b\d[-/]\d[-/]\d\b")
FREQ_ENGLISH_RE = re.compile(r"\b(\d+\s*morning|\d+\s*night|\d+\s*noon)\b", re.I)
AFTER_BEFORE_FOOD_RE = re.compile(r"\b(after|before)\s*food\b", re.I)

# Dosage with proper medical units (case-insensitive)
DOSAGE_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mcg|ug|µg|g|ml|mL|IU|units)\b",
    re.I
)

# A lone numeric strength adjacent to the name (e.g., "ZOCLAR 500")
TRAILING_STRENGTH_RE = re.compile(r"\b([1-9]\d{1,4})\b")

# Abbreviation map for frequencies
FREQ_ABBR: Dict[str, str] = {
    "qd": "once daily", "od": "once daily",
    "bid": "twice daily", "bd": "twice daily",
    "tid": "three times daily", "tds": "three times daily",
    "qid": "four times daily",
    "qhs": "at bedtime", "hs": "at bedtime",
    "prn": "as needed",
}

def is_total_line(line: str) -> bool:
    if TOTAL_RE.search(line):
        return True
    return line.strip().lower().startswith("(tot:")

def normalize_frequency(line: str) -> Optional[str]:
    # 1-0-1 / 1/0/1
    m = FREQ_TRIPLET_RE.search(line)
    if m:
        trip = m.group(0).replace("/", "-")
        mapping = {
            "1-1-1": "three times daily",
            "1-0-1": "morning and evening",
            "0-1-1": "noon and evening",
            "1-0-0": "morning",
        }
        return mapping.get(trip, trip)

    # English phrases like "1 Morning, 1 Night"
    parts = []
    if re.search(r"\b1\s*morning\b", line, re.I): parts.append("morning")
    if re.search(r"\b1\s*noon\b", line, re.I): parts.append("noon")
    if re.search(r"\b1\s*night\b", line, re.I): parts.append("night")
    if parts:
        return " and ".join(parts)

    # Abbreviations (bid, tid, etc.)
    for tok in re.findall(r"\b[a-zA-Z]{2,4}\b", line.lower()):
        if tok in FREQ_ABBR:
            return FREQ_ABBR[tok]

    # After/before food
    m2 = AFTER_BEFORE_FOOD_RE.search(line)
    if m2:
        return f"{m2.group(1).lower()} food"

    return None

def clean_form_noise(s: str) -> str:
    # Normalize things like "10/SR." -> "10 SR"
    s = s.replace("/", " ")
    s = re.sub(r"\s{2,}", " ", s)
    s = s.strip(" -:,")
    return s

def extract_medicine_and_tail(line: str) -> Tuple[Optional[str], str]:
    """
    Returns (medicine_name, remaining_tail_of_line)
    Medicine is the text after the form label and before first freq/duration cue.
    """
    m = LINE_FORM_RE.search(line)
    tail = line[m.end():].strip() if m else line.strip()

    # Determine the earliest cut position for medicine end
    cut_idx = len(tail)
    cues = [
        re.search(r"\b\d\s*morning\b", tail, re.I),
        re.search(r"\b\d\s*night\b", tail, re.I),
        re.search(r"\b\d\s*noon\b", tail, re.I),
        DURATION_RE.search(tail),
    ]
    for c in cues:
        if c:
            cut_idx = min(c.start(), cut_idx)

    # Also cut before ", 1 Night" etc.
    comma_freq = re.search(r",\s*\d\s*(morning|noon|night)\b", tail, re.I)
    if comma_freq:
        cut_idx = min(comma_freq.start(), cut_idx)

    med = clean_form_noise(tail[:cut_idx])
    med = " ".join(med.split()[:6]) if med else None
    rest = tail[cut_idx:].strip()
    return (med if med else None, rest)

def is_instruction_only(line: str) -> bool:
    # Lines that only contain instructions like "(After Food)" and no clear med/dose
    if AFTER_BEFORE_FOOD_RE.search(line):
        if not LINE_FORM_RE.search(line) and not DOSAGE_RE.search(line):
            return True
    return False

def is_candidate_line(line: str) -> bool:
    if is_total_line(line):
        return False
    if is_instruction_only(line):
        # Keep as candidate so frequency like "after food" can be captured
        return True
    return bool(
        LINE_FORM_RE.search(line)
        or DOSAGE_RE.search(line)
        or FREQ_TRIPLET_RE.search(line)
        or FREQ_ENGLISH_RE.search(line)
        or DURATION_RE.search(line)
    )

def extract_entities_from_line(line: str) -> dict:
    # Ignore totals entirely
    if is_total_line(line):
        return {"medicine": None, "dosage": None, "frequency": None, "duration": None, "source": line}

    # Extract medicine (if any) and the rest for later parsing
    med, tail = extract_medicine_and_tail(line)

    # Frequency and duration from the full line
    frequency = normalize_frequency(line)

    duration = None
    m_dur = DURATION_RE.search(line)
    if m_dur:
        num, unit = m_dur.group(1), m_dur.group(2).lower()
        unit = "days" if unit.startswith("day") else "weeks"
        duration = f"{num} {unit}"

    # Dosage with units (skip totals)
    dosage = None
    for m in DOSAGE_RE.finditer(line):
        left = line[:m.start()]
        if re.search(r"Tot\s*:\s*$", left, re.I):
            continue
        dosage = m.group(0)
        break

    # If no unit-dosage found, try trailing numeric strength attached to the medicine
    if not dosage and med:
        m_strength = TRAILING_STRENGTH_RE.search(med)
        if m_strength and m_strength.end() == len(med):
            dosage = m_strength.group(1)
            med = med[:m_strength.start()].strip()

    # If instruction-only (e.g., "(After Food)"), do not treat as medicine row
    if is_instruction_only(line):
        med = None

    return {
        "medicine": med or None,
        "dosage": dosage,
        "frequency": frequency,
        "duration": duration,
        "source": line,
    }
