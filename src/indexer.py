from collections import defaultdict
from typing import Dict, List, Set

class InvertedIndex:
    """
    Builds and manages an inverted index that maps terms to the documents they occur in.
    """
    
    def __init__(self):
        # Maps a term directly to a dictionary of {document_id: frequency}
        # e.g., index['search'] = {'doc1.txt': 2, 'doc2.txt': 1}
        self.index: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Keeps track of all processed documents (useful for calculating IDF later)
        self.document_ids: Set[str] = set()

    def add_document(self, doc_id: str, tokens: List[str]):
        """
        Adds a document's tokens to the inverted index.
        
        Args:
            doc_id (str): The unique identifier for the document.
            tokens (List[str]): The preprocessed tokens of the document.
        """
        self.document_ids.add(doc_id)
        
        for token in tokens:
            self.index[token][doc_id] += 1

    def get_postings(self, term: str) -> Dict[str, int]:
        """
        Retrieves the postings list (documents and frequencies) for a given term.
        
        Args:
            term (str): The term to look up.
            
        Returns:
            Dict[str, int]: A map of doc_id -> frequency for the given term.
        """
        return self.index.get(term, {})
        
    def get_document_frequency(self, term: str) -> int:
        """
        Returns the number of documents that contain the given term.
        """
        return len(self.index.get(term, {}))

    def get_total_documents(self) -> int:
        """
        Returns the total number of documents indexed.
        """
        return len(self.document_ids)

# --- Development / Verification Block ---
if __name__ == "__main__":
    from preprocess import TextPreprocessor
    
    preprocessor = TextPreprocessor()
    indexer = InvertedIndex()
    
    docs = {
        "doc1": "Python is a great programming language.",
        "doc2": "Python developers love programming in Python!"
    }
    
    print("--- Building Inverted Index ---")
    for doc_id, text in docs.items():
        tokens = preprocessor.preprocess(text)
        indexer.add_document(doc_id, tokens)
        print(f"Added {doc_id}.")
        
    print("\n--- Index Lookup ---")
    search_term = "python"
    print(f"Term '{search_term}' is found in: {indexer.get_postings(search_term)}")
    
    search_term2 = "programming"
    print(f"Term '{search_term2}' is found in: {indexer.get_postings(search_term2)}")
