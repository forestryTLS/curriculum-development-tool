# FastAPI Topic Extraction Service

# Overview

Extracts candidate topics (keywords and key phrases) from the text of a course
material file. RAKE (Rapid Automatic Keyword Extraction) is the current
algorithm.

The service runs on `http://127.0.0.1:8003`.

## How It Works

- The caller sends the already-extracted page text (the `course_material_chunks`
  rows produced by the Laravel indexing job) as a list of pages.
- The route combines the pages into a single document and passes it to the
  extractor's `extract` function.
- The extractor returns topics with a relevance score, ordered from most to
  least relevant.

### Swapping the algorithm

The actual extraction lives in one file, `app/services/rake_extractor.py`, which
exposes `extract(text) -> list[Topic]`. To try a different algorithm, either edit
that file, or add a new file with the same `extract` function and change the one
import line in `app/api/routes.py`:

```python
# Swap this import to test a different algorithm.
from app.services import rake_extractor as extractor
```

## API

**POST `/extract`**: Extract topics from page text

```json
{
  "pages": [
    {"page_number": 1, "content": "..."},
    {"page_number": 2, "content": "..."}
  ]
}
```

Returns:

```json
{
  "topics": [
    {"topic": "forest ecosystems", "score": 4.0},
    {"topic": "chemical energy", "score": 3.5}
  ]
}
```

**GET `/health`**: Health check endpoint

## NLTK data

RAKE relies on the NLTK `stopwords` and `punkt`/`punkt_tab` data packages. They
are downloaded automatically on first use if they are not already present, so no
manual step is required.
