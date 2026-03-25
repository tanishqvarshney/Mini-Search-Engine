from collections import defaultdict
from typing import Dict, List, Set

class InvertedIndex:
    """
    Builds and manages an inverted index that maps terms to the documents they occur in.
    """
    
    def __init__(self):
        # Maps field -> term -> document_id -> frequency
        # e.g., index['title']['search'] = {'doc1.txt': 1}
        self.index: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        # Keeps track of all processed documents
        self.document_ids: Set[str] = set()

    def add_document(self, doc_id: str, field_tokens: Dict[str, List[str]]):
        """
        Adds tokens for various fields to the inverted index.
        
        Args:
            doc_id (str): Unique doc identifier.
            field_tokens (Dict[str, List[str]]): A map of field_name -> tokens.
        """
        self.document_ids.add(doc_id)
        
        for field, tokens in field_tokens.items():
            for token in tokens:
                self.index[field][token][doc_id] += 1

    def get_postings(self, term: str, field: str = "content") -> Dict[str, int]:
        """Retrieves postings for a specific field."""
        return self.index.get(field, {}).get(term, {})
        
    def get_document_frequency(self, term: str, field: str = "content") -> int:
        """Returns DF across all documents for a term in a specific field."""
        return len(self.index.get(field, {}).get(term, {}))

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
