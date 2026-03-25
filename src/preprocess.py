import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import ssl

# Fix for macOS SSL certificate verify failed error during nltk.download
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Ensure required NLTK resources are available locally
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class TextPreprocessor:
    """
    Handles tokenization, stopword removal, and lemmatization of documents or queries.
    """
    def __init__(self):
        # Load stop words (common words like 'the', 'is', 'in' that don't add search value)
        self.stop_words = set(stopwords.words('english'))
        # Initialize Lemmatizer (reduces words to their base form: 'running' -> 'run')
        self.lemmatizer = WordNetLemmatizer()
    
    def preprocess(self, text: str) -> list[str]:
        """
        Cleans and tokenizes the input text.
        
        Processing Pipeline:
        1. Lowercase the text.
        2. Remove punctuation.
        3. Tokenize (split into words).
        4. Remove stopwords.
        5. Lemmatize.
        
        Args:
            text (str): The raw input string.
            
        Returns:
            list[str]: A list of clean tokens.
        """
        if not text:
            return []
            
        # 1. Lowercase translation
        text = text.lower()
        
        # 2. Remove all punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # 3. Tokenize
        tokens = word_tokenize(text)
        
        # 4 & 5. Filter out stopwords and lemmatize
        processed_tokens = []
        for token in tokens:
            # Check if it's a stopword or just empty whitespace
            if token not in self.stop_words and token.strip():
                lemma = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemma)
                
        return processed_tokens

# --- Development / Verification Block ---
if __name__ == "__main__":
    preprocessor = TextPreprocessor()
    
    sample_text = "Search engines use web crawlers to heavily index the web! They are amazing."
    print("--- Test Preprocessing ---")
    print(f"Original Text: {sample_text}")
    
    tokens = preprocessor.preprocess(sample_text)
    print(f"Processed Tokens: {tokens}")
