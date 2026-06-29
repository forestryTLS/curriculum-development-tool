import pymupdf

from app.schemas import Topic


# A slide "title" longer than this is probably body text, not a title.
MAX_TITLE_WORDS = 15


def extract(file_bytes: bytes) -> list[Topic]:
    """Extract slide titles from a PPTX-exported PDF (one slide per page).
    Each slide's title is taken to be the largest-font text on that page. Returns
    an empty list if the file is not a readable PDF.
    """
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception:
        return []

    titles: list[str] = []
    try:
        for page in doc:
            title = _slide_title(page)
            if title:
                titles.append(title)
    finally:
        doc.close()

    seen: set[str] = set()
    topics: list[Topic] = []
    for title in titles:
        key = title.lower()
        if key not in seen:
            seen.add(key)
            topics.append(Topic(topic=title, score=0.0))
    return topics


def _slide_title(page) -> str | None:
    spans: list[tuple[float, str]] = []
    for block in page.get_text("dict").get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text:
                    spans.append((round(span.get("size", 0.0), 1), text))

    if not spans:
        return None

    max_size = max(size for size, _ in spans)
    # The title is the run of text at (or very near) the largest font on the slide.
    title = " ".join(text for size, text in spans if size >= max_size - 0.5).strip()

    if title and len(title.split()) <= MAX_TITLE_WORDS:
        return title
    return None