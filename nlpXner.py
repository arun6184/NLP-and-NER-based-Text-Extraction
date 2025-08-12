import json
import sys
from extract import run_pipeline, to_table

def main():
    # Usage: python nlpXner.py <image_path> [tesseract|easyocr] [--debug]
    if len(sys.argv) < 2:
        print("Usage: python nlpXner.py <image_path> [tesseract|easyocr] [--debug]")
        sys.exit(1)

    path = sys.argv[1]

    # Determine OCR engine (default: tesseract)
    engine = "tesseract"
    debug = False
    if len(sys.argv) >= 3:
        if sys.argv[2].lower() in ("tesseract", "easyocr"):
            engine = sys.argv[2].lower()
        elif sys.argv[2] == "--debug":
            debug = True
    if len(sys.argv) >= 4:
        if sys.argv[3].lower() in ("tesseract", "easyocr"):
            engine = sys.argv[3].lower()
        elif sys.argv[3] == "--debug":
            debug = True

    try:
        items = run_pipeline(path, engine=engine, debug=debug)
    except FileNotFoundError:
        print(f"Error: file not found -> {path}")
        sys.exit(1)
    except Exception as e:
        print(f"Pipeline error: {e}")
        sys.exit(1)

    print("Extracted Items (table):")
    print(to_table(items))
    print("\nJSON:")
    print(json.dumps(items, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()