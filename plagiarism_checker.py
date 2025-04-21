import requests
import random
import pandas as pd
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urlparse

# Random User-Agent Headers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
]

def get_random_headers():
    """Returns a random header to make HTTP requests."""
    return {'User-Agent': random.choice(USER_AGENTS)}

def get_url(sentence):
    """Fetches the first URL result for the sentence from Google Search."""
    params = {
        "q": sentence,
        "api_key": "db9aaffe49f83295b88ab03a5d93881db87811e90016706f059513e13541b61d",  # Replace with your actual API key
        "engine": "google",
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        if 'organic_results' in results:
            return results['organic_results'][0].get('link', None)
    except Exception as e:
        print(f"Error fetching URL: {e}")
    return None

def get_text_from_url(url):
    """Fetches and returns the textual content from a URL."""
    try:
        if any(domain in url for domain in ["facebook.com", "instagram.com"]):
            print(f"Skipping unsupported URL: {url}")
            return ""
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return ' '.join([p.text for p in soup.find_all('p')])
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch from {url}: {e}")
        return ""

def get_similarity(text1, text2):
    """Calculates cosine similarity between two texts."""
    if not text1 or not text2:
        return 0.0
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    return cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]

def get_similarity_between_files(file_texts):
    """Calculates cosine similarity between multiple file texts."""
    similarity_list = []
    for i in range(len(file_texts)):
        for j in range(i + 1, len(file_texts)):
            similarity = get_similarity(file_texts[i], file_texts[j])
            similarity_list.append({
                'File 1': f"File {i + 1}",
                'File 2': f"File {j + 1}",
                'Similarity': similarity
            })
    return similarity_list

def check_plagiarism(sentences, text):
    """Checks for plagiarism in given sentences."""
    similarity_list = []
    urls = []

    for sentence in sentences:
        url = get_url(sentence)
        urls.append(url)

    for idx, url in enumerate(urls):
        if url:
            try:
                text_from_url = get_text_from_url(url)
                if text_from_url.strip():  # Avoid comparing with empty content
                    similarity = get_similarity(text, text_from_url)
                    similarity_list.append({
                        'Sentence': sentences[idx],
                        'Source': url,
                        'Similarity': similarity
                    })
            except Exception as e:
                print(f"Error processing URL at index {idx}: {e}")

    df = pd.DataFrame(similarity_list).sort_values(by='Similarity', ascending=False).reset_index(drop=True)

    # Clean display: Show "Source1", "Source2", etc. with links
    df['Source'] = df['Source'].apply(
    lambda x: x if x else 'No URL found'
)



    return df
