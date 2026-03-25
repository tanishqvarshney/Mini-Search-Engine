import os
import requests
from bs4 import BeautifulSoup
from typing import Dict

class DocumentLoader:
    """
    A unified loader to fetch documents from local directories or the web.
    """
    
    @staticmethod
    def load_local_documents(folder_path: str) -> Dict[str, str]:
        """
        Reads all text files in a specified folder.
        
        Args:
            folder_path (str): The directory containing text files.
            
        Returns:
            Dict[str, str]: A dictionary where keys are filenames and values are the text content.
        """
        documents = {}
        if not os.path.exists(folder_path):
            print(f"Directory {folder_path} does not exist.")
            return documents

        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    documents[filename] = f.read().strip()
                    
        return documents

    @staticmethod
    def crawl_webpage(url: str) -> Dict[str, str]:
        """
        Fetches text from a single webpage using BeautifulSoup.
        
        Args:
            url (str): The URL to crawl.
            
        Returns:
            Dict[str, str]: A dictionary mapping the URL to its fetched plain text content.
        """
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Check for HTTP errors
            
            # Parse HTML and extract raw text
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            text = soup.get_text(separator=" ", strip=True)
            return {url: text}
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
