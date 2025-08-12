from PIL import Image
import pytesseract

def ocr_with_tesseract(path: str, lang: str = "eng", config: str = "--oem 3 --psm 6") -> str:
    img = Image.open(path)
    return pytesseract.image_to_string(img, lang=lang, config=config)
