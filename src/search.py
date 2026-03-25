import re
import os
import json
from typing import Dict, List, Tuple, Any
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
        # Rich media store
        self.metadata: Dict[str, Dict[str, str]] = {}

        # Load Entity Config for Alias Mapping
        self.entity_config = {}
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "data", "entity_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.entity_config = json.load(f).get("entities", {})
        except Exception as e:
            print(f"Error loading entity config: {e}")

    def add_document(self, doc_id: str, document_data: Any):
        """
        Processes and indexes a single document containing text and rich media metadata.
        Applies field-level indexing for Title vs Content.
        """
        if isinstance(document_data, str):
            text = document_data
            title = doc_id
            self.metadata[doc_id] = {}
        else:
            text = document_data.get("text", "")
            title = document_data.get("title", doc_id)
            
            self.metadata[doc_id] = {
                "title": title,
                "url": document_data.get("url", doc_id),
                "meta_description": document_data.get("meta_description", ""),
                "image_url": document_data.get("image_url"),
                "platform": document_data.get("platform", "Web")
            }
            if "metadata" in document_data:
                self.metadata[doc_id]["metadata"] = document_data["metadata"]

        self.document_store[doc_id] = text
        
        # Preprocess and index the fields separately for Title Boosting
        title_tokens = self.preprocessor.preprocess(title)
        content_tokens = self.preprocessor.preprocess(text)
        
        self.indexer.add_document(doc_id, {
            "title": title_tokens,
            "content": content_tokens
        })

    def _extract_smart_snippet(self, query_tokens: List[str], text: str) -> str:
        """Finds the most relevant sentences and highlights keywords"""
        sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
        if not sentences:
            return ""
            
        best_idx = 0
        max_score = 0
        query_set = set([t.lower() for t in query_tokens])
        junk_terms = {"jump to content", "main menu", "move to sidebar", "navigation", "search"}
        
        for i, sentence in enumerate(sentences):
            lower_s = sentence.lower()
            if len(sentence) < 20 or any(jt in lower_s[:40] for jt in junk_terms):
                continue
                
            sentence_tokens = set(self.preprocessor.preprocess(sentence))
            score = len(query_set.intersection(sentence_tokens))
            
            words = set(re.findall(r'\w+', lower_s))
            score += len(query_set.intersection(words))

            if score > max_score:
                max_score = score
                best_idx = i
                
        start_idx = max(0, best_idx - 1)
        end_idx = min(len(sentences), start_idx + 3)
        
        snippet = " ".join(sentences[start_idx:end_idx])
        if len(snippet) > 300:
            snippet = snippet[:300] + "..."
            
        for term in query_tokens:
            if len(term) > 2:
                pattern = re.compile(f'\\b({re.escape(term)})\\w*\\b', re.IGNORECASE)
                snippet = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", snippet)
                
        return snippet

    def _extract_entity_facts(self, text: str) -> dict:
        """Heuristic-based extraction of key person/entity facts"""
        facts = {}
        patterns = {
            "Born": r"(?i)born\s+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
            "Nationality": r"(?i)nationality\s+([A-Z][a-z]+)",
            "Role": r"(?i)(?:role|position)\s+([A-Z][a-z\s]+)",
            "Teams": r"(?i)current\s+team\s+([A-Z][a-z\s]+)",
            "Full Name": r"(?i)full\s+name\s+([A-Z][a-z\s]+)"
        }
        
        for label, pattern in patterns.items():
            match = re.search(pattern, text[:2000])
            if match:
                facts[label] = match.group(1).strip()
                
        if "cricket" in text.lower():
            bat_match = re.search(r"(?i)batting\s+style\s+([A-Z][a-z\s]+)", text[:2000])
            if bat_match: facts["Batting"] = bat_match.group(1).strip()
            
        return facts

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Executes search with entity-aware ranking"""
        query_tokens = self.preprocessor.preprocess(query)
        if not query_tokens:
            return []

        # Entity Disambiguation Pass
        matched_entity_id = None
        for entity_id, info in self.entity_config.items():
            if query.lower() == entity_id.lower() or any(alias in query.lower() for alias in info.get("aliases", [])):
                matched_entity_id = entity_id
                break

        search_results = self.ranker.rank(query_tokens, entity_id=matched_entity_id)
        
        results = []
        for doc_id, score in search_results[:top_k]:
            meta = self.metadata.get(doc_id, {})
            content = self.document_store.get(doc_id, "")
            
            snippet = self._extract_smart_snippet(query_tokens, content)
            facts = self._extract_entity_facts(content)
            is_hero = score > 12.0
            
            res_obj = {
                "id": doc_id,
                "score": score,
                "title": meta.get("title", doc_id),
                "url": meta.get("url", "#"),
                "meta_description": meta.get("meta_description", ""),
                "snippet": snippet,
                "image_url": meta.get("image_url", ""),
                "facts": facts,
                "is_hero": is_hero,
                "platform": meta.get("platform", "Web")
            }
            if "metadata" in meta:
                res_obj["metadata"] = meta["metadata"]
            
            results.append(res_obj)
            
        return results

if __name__ == "__main__":
    engine = SearchEngine()
    engine.add_document("wiki_python", "Python is a great programming language.")
    print(f"Searching 'python': {engine.search('python')}")
