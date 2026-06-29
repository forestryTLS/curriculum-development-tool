import regex as re

def process(text : str) -> str:
    """Preprocess text for topic extraction"""
    
    # Remove whole links with
    text = re.sub(r'http:.*?/.*?\. .*(?:jpg|jpeg|png|gif|bmp|svg|webp)', '', text)
    # Remove any stray link elements
    text = re.sub(r'\b(?:http|https|www)\S*\b', '', text)
    text = re.sub(r'\b(?:jpg|jpeg|png|gif|bmp|svg|webp)\b', '', text)
    
    # Add periods after newlines if not already present
    # NOTE: This is useful for slides where lines don't end with periods.
    #       However, this may not be great for multi-line paragraphs.
    # TODO: If material type is 'slides', then do this. Otherwise, don't.
    text = re.sub(r'(?<![.!?])\n', '. \n', text)
    
    # print(f"Preprocessed text:\n {text}...")
        
    return text