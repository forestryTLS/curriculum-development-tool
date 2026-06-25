import nltk
from rake_nltk import Rake

from app.schemas import Topic


TOPICS_COUNT = 30

# RAKE tokenizes into sentences then words and filters stopwords, so it needs
# these NLTK data packages. They are fetched once if not already present.
_REQUIRED_NLTK_DATA = (
    ("corpora/stopwords", "stopwords"),
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("tokenizers/punkt", "punkt"),
)


def _ensure_nltk_data() -> None:
    for find_path, download_id in _REQUIRED_NLTK_DATA:
        try:
            nltk.data.find(find_path)
        except LookupError:
            nltk.download(download_id, quiet=True)


_ensure_nltk_data()


def extract(text: str) -> list[Topic]:
    """Extract topics from text using RAKE, most relevant to least."""
    rake = Rake()
    rake.extract_keywords_from_text(text)
    ranked = rake.get_ranked_phrases_with_scores()[:TOPICS_COUNT]
    return [
        Topic(topic=phrase, score=round(float(score), 4))
        for score, phrase in ranked
    ]
