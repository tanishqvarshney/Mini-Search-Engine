import os
import requests
import json
from bs4 import BeautifulSoup
from typing import Dict, Any

class DocumentLoader:
    """
    A unified loader to fetch documents from local directories or the web.
    """
    
    @staticmethod
    def load_local_documents(folder_path: str) -> Dict[str, Any]:
        """Reads files in a specified folder. Supports .txt and .json files."""
        documents = {}
        if not os.path.exists(folder_path):
            print(f"Directory {folder_path} does not exist.")
            return documents

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    documents[filename] = {"text": f.read().strip()}
            elif filename.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if "text" in data:
                            documents[filename] = data
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON in {filename}")
                    
        return documents

    @staticmethod
    def crawl_webpage(url: str) -> Dict[str, Any]:
        """
        Fetches text from a single webpage using BeautifulSoup, and extracts OpenGraph metadata.
        """
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()  # Check for HTTP errors
            
            # Parse HTML and extract raw text
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract OpenGraph and SEO Metadata
            og_image = soup.find("meta", property="og:image")
            og_title = soup.find("meta", property="og:title")
            meta_desc = soup.find("meta", attrs={"name": "description"})
            
            image_url = og_image["content"] if og_image and og_image.get("content") else None
            title = og_title["content"] if og_title and og_title.get("content") else soup.title.string if soup.title else url
            description = meta_desc["content"] if meta_desc and meta_desc.get("content") else ""
            
            # Extract Headings
            headings = []
            for h in soup.find_all(['h1', 'h2']):
                if h.get_text(strip=True):
                    headings.append(h.get_text(strip=True))
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            text = soup.get_text(separator=" ", strip=True)
            return {url: {
                "url": url,
                "title": title,
                "meta_description": description,
                "headings": headings,
                "image_url": image_url,
                "text": text
            }}
        except Exception as e:
            print(f"Failed to crawl {url}: {e}")
            return {}

# Example usage (can be removed or kept as a test execution block)
if __name__ == "__main__":
    loader = DocumentLoader()
    
    # 1. Test Local Loader
    print("--- Loading Local Documents ---")
    local_docs = loader.load_local_documents("../data/sample_docs")
    for doc_id, text in local_docs.items():
        print(f"[{doc_id}]: {text[:50]}...")
        
    # 2. Test Web Crawler
    print("\n--- Crawling Webpage ---")
    web_docs = loader.crawl_webpage("https://example.com")
    for url, text in web_docs.items():
        print(f"[{url}]: {text[:50]}...")
