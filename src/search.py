from typing import Dict, List, Tuple
from preprocess import TextPreprocessor
from indexer import InvertedIndex
from ranker import Ranker

class SearchEngine:
    """
    The orchestrator class that ties together preprocessing, indexing, and ranking
    to provide a unified search interface.
    """
    
    def __init__(self):
        # Initialize our three core engine components
        self.preprocessor = TextPreprocessor()
        self.indexer = InvertedIndex()
        self.ranker = Ranker(self.indexer)
        
        # Simple document store to retrieve the actual text for the UI
        self.document_store: Dict[str, str] = {}

    def add_document(self, doc_id: str, text: str):
        """
        Processes and indexes a single document.
        """
        # Save original text for result display
        self.document_store[doc_id] = text
        
        # Preprocess and index
        tokens = self.preprocessor.preprocess(text)
        self.indexer.add_document(doc_id, tokens)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, str]]:
        """
        Executes a search query and returns the top results.
        
        Args:
            query (str): The raw string query.
            top_k (int): Number of top results to return.
            
        Returns:
            List[Tuple[str, float, str]]: A list of tuples containing 
                                          (doc_id, score, document_snippet).
        """
        # 1. Preprocess the query
        query_tokens = self.preprocessor.preprocess(query)
        if not query_tokens:
            return []

        # 2. Get ranked documents
        ranked_results = self.ranker.score_documents(query_tokens)
        
        # 3. Format output mapping to actual documents
        formatted_results = []
        for doc_id, score in list(ranked_results.items())[:top_k]:
            text_snippet = self.document_store.get(doc_id, "")
            # Snip text if it's too long
            if len(text_snippet) > 100:
                text_snippet = text_snippet[:100] + "..."
            formatted_results.append((doc_id, score, text_snippet))
            
        return formatted_results

# --- Development / Verification Block ---
if __name__ == "__main__":
    engine = SearchEngine()
    
    print("--- Initializing Search Engine ---")
    # Load some documents manually for testing
    docs = {
        "wiki_python": "Python is a high-level, general-purpose programming language.",
        "wiki_search": "Search engines use web crawlers to index the web. They parse text and rank it.",
        "wiki_tfidf": "TF-IDF stands for Term Frequency-Inverse Document Frequency. It is used in information retrieval.",
        "random.txt": "I love my lazy brown dog."
    }
    
    for doc_id, text in docs.items():
        engine.add_document(doc_id, text)
        print(f"Indexed: {doc_id}")
        
    # Run a search
    user_query = "python programming"
    print(f"\n--- Searching for: '{user_query}' ---")
    
    results = engine.search(user_query)
    
    if not results:
        print("No results found.")
    else:
        for i, (doc_id, score, snippet) in enumerate(results, 1):
            print(f"{i}. [{doc_id}] (Score: {score:.4f}): {snippet}")
