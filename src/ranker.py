import math
from typing import Dict, List, Tuple, Any
from indexer import InvertedIndex

class Ranker:
    """
    Ranks documents for a given query using the TF-IDF scoring model.
    """
    
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1
        self.b = b

    def _compute_idf(self, doc_freq: int) -> float:
        """BM25 IDF: log((N - df + 0.5) / (df + 0.5) + 1)"""
        N = self.index.get_total_documents()
        if N == 0: return 0.0
        return math.log((N - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)

    def rank(self, query_tokens: List[str], entity_id: str = None) -> List[Tuple[str, float]]:
        """
        Ranks documents using the BM25 algorithm with field-level boosting.
        """
        scores: Dict[str, float] = {}
        fields = {"title": 10.0, "content": 1.0}  # Increased title boost

        for field, weight in fields.items():
            avgdl = self.index.get_avg_doc_length(field=field)
            for token in query_tokens:
                postings = self.index.get_postings(token, field=field)
                doc_freq = self.index.get_document_frequency(token, field=field)
                idf = self._compute_idf(doc_freq)
                
                if idf <= 0.0: continue
                    
                for doc_id, tf in postings.items():
                    doc_len = self.index.get_doc_length(doc_id, field=field)
                    
                    # BM25 Formula
                    num = tf * (self.k1 + 1)
                    denom = tf + self.k1 * (1 - self.b + self.b * (doc_len / avgdl if avgdl > 0 else 1))
                    
                    field_score = idf * (num / denom)
                    
                    if doc_id not in scores: scores[doc_id] = 0.0
                    scores[doc_id] += field_score * weight

        # Apply Entity Boost
        if entity_id:
            canon_id = entity_id.lower().replace(" ", "_")
            for doc_id in scores:
                if canon_id in doc_id.lower().replace(" ", "_"):
                    scores[doc_id] *= 15.0  # Significant entity multiplier

        # Penalty for extremely short content (e.g. less than 50 chars) - Explicit
        # (Though BM25 handles this, we add a floor for 'low information' docs)
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)

# --- Development / Verification Block ---
if __name__ == "__main__":
    from preprocess import TextPreprocessor
    from indexer import InvertedIndex
    
    preprocessor = TextPreprocessor()
    indexer = InvertedIndex()
    
    docs = {
        "doc1": {"title": "Quick Brown Fox", "content": "The quick brown fox jumps over the lazy dog."},
        "doc2": {"title": "Fast Fox", "content": "A fast brown fox."},
        "doc3": {"title": "Lazy Dogs", "content": "Dogs are great pets, but lazy dogs sleep all day!"}
    }
    
    for doc_id, data in docs.items():
        tokens = {"title": preprocessor.preprocess(data["title"]), "content": preprocessor.preprocess(data["content"])}
        indexer.add_document(doc_id, tokens)
        
    ranker = Ranker(indexer)
    query = "lazy brown fox"
    print(f"--- Query: '{query}' ---")
    query_tokens = preprocessor.preprocess(query)
    results = ranker.rank(query_tokens)
    
    print("\n--- BM25 Ranking Results ---")
    for doc_id, score in results:
        print(f"{doc_id}: Score = {score:.4f}")
