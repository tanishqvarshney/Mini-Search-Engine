import math
from typing import Dict, List
from indexer import InvertedIndex

class Ranker:
    """
    Ranks documents for a given query using the TF-IDF scoring model.
    """
    
    def __init__(self, index: InvertedIndex):
        self.index = index

    def _compute_tf(self, term_freq: int) -> float:
        """
        Computes the Term Frequency (TF). 
        Using sublinear TF scaling: 1 + log(tf).
        """
        if term_freq == 0:
            return 0.0
        return 1.0 + math.log(term_freq)

    def _compute_idf(self, doc_freq: int) -> float:
        """
        Computes the Inverse Document Frequency (IDF).
        Using standard formula: log(N / df).
        """
        total_docs = self.index.get_total_documents()
        if doc_freq == 0 or total_docs == 0:
            return 0.0
        return math.log(total_docs / doc_freq)

    def score_documents(self, query_tokens: List[str]) -> Dict[str, float]:
        """
        Calculates the TF-IDF score for all documents that match the query.
        
        Args:
            query_tokens (List[str]): Preprocessed query tokens.
            
        Returns:
            Dict[str, float]: A dictionary mapping document IDs to their relevance score, 
                              sorted highest to lowest.
        """
        scores: Dict[str, float] = {}

        for token in query_tokens:
            postings = self.index.get_postings(token)
            doc_freq = self.index.get_document_frequency(token)
            idf = self._compute_idf(doc_freq)
            
            # If the term hasn't appeared anywhere, skip it
            if idf == 0.0:
                continue
                
            for doc_id, tf in postings.items():
                tf_score = self._compute_tf(tf)
                
                # Ensure the document exists in our score tracking
                if doc_id not in scores:
                    scores[doc_id] = 0.0
                    
                # TF-IDF Score = TF * IDF
                scores[doc_id] += tf_score * idf

        # Sort documents by score in descending order
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        return sorted_scores

# --- Development / Verification Block ---
if __name__ == "__main__":
    from preprocess import TextPreprocessor
    
    # 1. Initialize components
    preprocessor = TextPreprocessor()
    indexer = InvertedIndex()
    ranker = Ranker(indexer)
    
    # 2. Add sample documents
    docs = {
        "doc1": "The quick brown fox jumps over the lazy dog.",
        "doc2": "A fast brown fox.",
        "doc3": "Dogs are great pets, but lazy dogs sleep all day!"
    }
    
    for doc_id, text in docs.items():
        tokens = preprocessor.preprocess(text)
        indexer.add_document(doc_id, tokens)
        
    # 3. Process a query
    query = "lazy brown fox"
    print(f"--- Query: '{query}' ---")
    query_tokens = preprocessor.preprocess(query)
    print(f"Tokens: {query_tokens}")
    
    # 4. Rank the results
    results = ranker.score_documents(query_tokens)
    print("\n--- Ranking Results ---")
    for doc_id, score in results.items():
        print(f"{doc_id}: Score = {score:.4f} (Text: '{docs[doc_id]}')")
