import re
import math

# Robust stopwords handling with graceful fallback
try:
    from nltk.corpus import stopwords as nltk_stopwords
    import nltk  # noqa: F401
except Exception:
    nltk_stopwords = None

_cached_english_stopwords = None


def _get_english_stopwords():
    """Return a set of English stopwords, attempting to use NLTK with graceful fallback."""
    global _cached_english_stopwords
    if _cached_english_stopwords is not None:
        return _cached_english_stopwords

    if nltk_stopwords is not None:
        try:
            _cached_english_stopwords = set(nltk_stopwords.words('english'))
            return _cached_english_stopwords
        except LookupError:
            try:
                import nltk
                nltk.download('stopwords', quiet=True)
                _cached_english_stopwords = set(nltk_stopwords.words('english'))
                return _cached_english_stopwords
            except Exception:
                pass

    # Fallback minimal stopword list
    _cached_english_stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'while', 'with', 'of', 'at', 'by', 'for',
        'to', 'in', 'on', 'from', 'up', 'down', 'out', 'over', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', "don't", "should",
        "should've", 'now', "aren't", "couldn't", "didn't", "doesn't", "hadn't", "hasn't",
        "haven't", "isn't", "mightn't", "mustn't", "needn't", "shan't", "shouldn't",
        "wasn't", "weren't", "won't", "wouldn't"
    }
    return _cached_english_stopwords


def findFileSimilarity(inputQuery, database):
    universalSetOfUniqueWords = set()
    matchPercentage = 0

    lowercaseQuery = inputQuery.lower()
    en_stops = _get_english_stopwords()

    # Replace punctuation with space and split
    queryWordList = re.sub(r"[^\w]", " ", lowercaseQuery).split()
    
    # Convert to a set for efficiency
    universalSetOfUniqueWords.update(queryWordList)

    database1 = database.lower()

    # Replace punctuation with space and split
    databaseWordList = re.sub(r"[^\w]", " ", database1).split()
    
    # Convert to a set for efficiency
    universalSetOfUniqueWords.update(databaseWordList)

    # Remove stopwords
    universalSetOfUniqueWords = {word for word in universalSetOfUniqueWords if word not in en_stops}

    queryTF = []
    databaseTF = []

    for word in universalSetOfUniqueWords:
        queryTF.append(queryWordList.count(word))
        databaseTF.append(databaseWordList.count(word))

    dotProduct = sum(q * d for q, d in zip(queryTF, databaseTF))

    queryVectorMagnitude = math.sqrt(sum(q**2 for q in queryTF))
    databaseVectorMagnitude = math.sqrt(sum(d**2 for d in databaseTF))

    # Avoid divide-by-zero errors
    if queryVectorMagnitude == 0 or databaseVectorMagnitude == 0:
        return 0  

    matchPercentage = (dotProduct / (queryVectorMagnitude * databaseVectorMagnitude)) * 100

    return matchPercentage
