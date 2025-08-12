from typing import List, Dict
from ocr_tesseract import ocr_with_tesseract
from ocr_easyocr import ocr_with_easyocr
from preprocess import normalize_text, split_into_candidate_lines
from ner_rules import extract_entities_from_line, is_candidate_line

def run_pipeline(image_path: str, engine: str = "tesseract", debug: bool = False) -> List[Dict]:
    # OCR
    raw = ocr_with_tesseract(image_path) if engine == "tesseract" else ocr_with_easyocr(image_path)

    if debug:
        print("\n--- RAW OCR ---")
        print(raw)

    # Normalize and segment
    norm = normalize_text(raw)
    lines = split_into_candidate_lines(norm)

    if debug:
        print("\n--- LINES ---")
        for i, ln in enumerate(lines, 1):
            print(f"{i:02d}: {ln}")

    # Extract
    items: List[Dict] = []
    for ln in lines:
        if not is_candidate_line(ln):
            continue

        ent = extract_entities_from_line(ln)

        # Merge instruction-only frequency lines (e.g., "after food") with the previous medicine item
        if ent.get("medicine") is None and ent.get("frequency") and not any([ent.get("dosage"), ent.get("duration")]):
            if items:
                if not items[-1].get("frequency"):
                    items[-1]["frequency"] = ent["frequency"]
                else:
                    items[-1]["frequency"] = f'{items[-1]["frequency"]}; {ent["frequency"]}'
            continue

        # Keep entries that have at least one meaningful field
        if any([ent.get("medicine"), ent.get("dosage"), ent.get("frequency"), ent.get("duration")]):
            items.append(ent)

    return items

def to_table(items: List[Dict]) -> str:
    headers = ["medicine", "dosage", "frequency", "duration"]
    # Set column widths, e.g., frequency column is wider for long instructions
    colw = [20, 10, 32, 10]

    def row(vals):
        return " | ".join(str(vals[i])[:colw[i]].ljust(colw[i]) for i in range(len(headers)))

    out = [row(headers), "-+-".join("-" * w for w in colw)]
    for it in items:
        out.append(row([
            it.get("medicine", "") or "",
            it.get("dosage", "") or "",
            it.get("frequency", "") or "",
            it.get("duration", "") or "",
        ]))
    return "\n".join(out)