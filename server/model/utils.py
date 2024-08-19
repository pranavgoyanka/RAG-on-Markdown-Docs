import re
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_markdown(line):
    # Remove headers (e.g., # Header, ## Header)
    line = re.sub(r'^#+\s', '', line)
    # Remove bold and italics (e.g., **bold**, *italic*)
    line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
    line = re.sub(r'\*(.*?)\*', r'\1', line)
    # Remove inline code (e.g., `code`)
    line = re.sub(r'`(.*?)`', r'\1', line)
    # Remove links (e.g., [text](url))
    line = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', line)
    # Remove images (e.g., ![alt text](url))
    line = re.sub(r'!\[(.*?)\]\((.*?)\)', r'\1', line)
    # Remove blockquotes (e.g., > Quote)
    line = re.sub(r'^>\s', '', line)
    # Remove unordered list items (e.g., - Item, * Item)
    line = re.sub(r'^[-*]\s', '', line)
    # Remove ordered list items (e.g., 1. Item)
    line = re.sub(r'^\d+\.\s', '', line)
    # Remove horizontal rules (e.g., ---)
    line = re.sub(r'^-{3,}$', '', line)
    # Remove other markdown artifacts as needed
    return line.strip()

def extract_keywords_tfidf(text, num_keywords=5):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]
    keywords = sorted(list(zip(feature_names, tfidf_scores)), key=lambda x: x[1], reverse=True)
    return [word for word, score in keywords[:num_keywords]]