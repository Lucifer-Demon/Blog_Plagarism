
from nltk.corpus import stopwords
from plagiarismchecker.algorithm import webSearch
import sys
import re
import os
import json
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib


# Given a text string, remove all non-alphanumeric
# characters (using Unicode definition of alphanumeric).

def getQueries(text, n):
    sentenceEnders = re.compile("['.!?]")
    sentenceList = sentenceEnders.split(text)
    sentencesplits = []
    en_stops = set(stopwords.words('english'))

    for sentence in sentenceList:
        x = re.compile(r'\W+', re.UNICODE).split(sentence)
        for word in x:
            if word.lower() in en_stops:
                x.remove(word)
        x = [ele for ele in x if ele != '']
        sentencesplits.append(x)
    finalq = []
    for sentence in sentencesplits:
        l = len(sentence)
        if l > n:
            l = int(l/n)
            index = 0
            for i in range(0, l):
                finalq.append(sentence[index:index+n])
                index = index + n-1
                if index+n > l:
                    index = l-n-1
            if index != len(sentence):
                finalq.append(sentence[len(sentence)-index:len(sentence)])
        else:
            if l > 4:
                finalq.append(sentence)
    return finalq


def findSimilarity(text):
    # n-grams N VALUE SET HERE
    n = 9
    queries = getQueries(text, n)
    print('GetQueries task complete')
    q = [' '.join(d) for d in queries]
    output = {}
    c = {}
    i = 1
    while("" in q):
        q.remove("")
    count = len(q)
    if count > 100:
        count = 100
    numqueries = count
    for s in q[0:count]:
        output, c, errorCount = webSearch.searchWeb(s, output, c)
        print('Web search task complete')
        numqueries = numqueries - errorCount
        # print(output,c)
        sys.stdout.flush()
        i = i+1
    totalPercent = 0
    outputLink = {}
    print(output, c)
    prevlink = ''
    for link in output:
        percentage = (output[link]*c[link]*100)/numqueries
        if percentage > 10:
            totalPercent = totalPercent + percentage
            prevlink = link
            outputLink[link] = percentage
        elif len(prevlink) != 0:
            totalPercent = totalPercent + percentage
            outputLink[prevlink] = outputLink[prevlink] + percentage
        elif c[link] == 1:
            totalPercent = totalPercent + percentage
        print(link, totalPercent)

    print(count, numqueries)
    print(totalPercent, outputLink)
    print("\nDone!")
    return totalPercent, outputLink


# TF-IDF training/inference

def train_tfidf_model(documents: List[str], model_dir: str) -> Tuple[str, str, str]:
    os.makedirs(model_dir, exist_ok=True)
    # Character n-grams are robust to punctuation/spacing differences and capture near-exact matches
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 5), lowercase=True)
    tfidf_matrix = vectorizer.fit_transform(documents)

    vectorizer_path = os.path.join(model_dir, 'vectorizer.joblib')
    matrix_path = os.path.join(model_dir, 'matrix.joblib')
    index_path = os.path.join(model_dir, 'doc_index.json')

    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(tfidf_matrix, matrix_path)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump({'num_docs': len(documents)}, f)

    return vectorizer_path, matrix_path, index_path


def infer_similarity(query: str, model_dir: str) -> float:
    vectorizer_path = os.path.join(model_dir, 'vectorizer.joblib')
    matrix_path = os.path.join(model_dir, 'matrix.joblib')
    if not (os.path.exists(vectorizer_path) and os.path.exists(matrix_path)):
        return 0.0

    vectorizer = joblib.load(vectorizer_path)
    tfidf_matrix = joblib.load(matrix_path)
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, tfidf_matrix)[0]
    return float(sims.max() * 100.0) if sims.size > 0 else 0.0


def containment_similarity(query: str, document_text: str, n: int = 5) -> float:
    """Containment-based similarity using character n-grams.
    Returns percentage of query n-grams that are present in the document.
    If the query is a verbatim substring of the document (after lowercasing),
    this returns 100.
    """
    if not query or not document_text:
        return 0.0
    q = query.lower()
    d = document_text.lower()
    if len(q) < n:
        # Fallback to direct substring check for very short queries
        return 100.0 if q in d else 0.0
    q_shingles = {q[i:i+n] for i in range(len(q) - n + 1)}
    d_shingles = {d[i:i+n] for i in range(len(d) - n + 1)}
    if not q_shingles:
        return 0.0
    overlap = q_shingles.intersection(d_shingles)
    return (len(overlap) / len(q_shingles)) * 100.0
