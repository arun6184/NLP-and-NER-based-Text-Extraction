import easyocr

_reader = None

def get_reader(langs=["en"], gpu=False):
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(langs, gpu=gpu)
    return _reader

def ocr_with_easyocr(path: str, langs=["en"], gpu=False) -> str:
    reader = get_reader(langs, gpu)
    results = reader.readtext(path)  # [(bbox, text, conf), ...]
    return "\n".join([t for (_, t, _) in results])
