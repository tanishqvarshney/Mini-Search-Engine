import sys
import os

# Add the 'src' directory to the path so we can import our modules cleanly
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from crawler import DocumentLoader
from search import SearchEngine

def print_menu():
    print("\n" + "="*40)
    print("      MINI SEARCH ENGINE")
    print("="*40)
    print("1. Load documents from local folder")
    print("2. Crawl and index a webpage")
    print("3. Search the engine")
    print("4. Exit")
    print("="*40)

def main():
    engine = SearchEngine()
    loader = DocumentLoader()
    
    # Pre-index sample docs during initialization
    print("Initializing Search Engine...")
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_docs")
    local_docs = loader.load_local_documents(sample_path)
    if local_docs:
        print(f"Automatically loaded {len(local_docs)} sample documents.")
        for doc_id, text in local_docs.items():
            engine.add_document(doc_id, text)
            
    while True:
        print_menu()
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            folder_path = input("Enter folder path (e.g., data/sample_docs): ").strip()
            # Resolve relative paths gracefully
            full_path = os.path.join(os.path.dirname(__file__), folder_path)
            docs = loader.load_local_documents(full_path)
            if docs:
                for doc_id, text in docs.items():
                    engine.add_document(doc_id, text)
                print(f"Success! Indexed {len(docs)} documents.")
            else:
                print("No documents found or directory does not exist.")
                
        elif choice == "2":
            url = input("Enter webpage URL to crawl (e.g., https://example.com): ").strip()
            print("Crawling...")
            web_docs = loader.crawl_webpage(url)
            if web_docs:
                for url_id, text in web_docs.items():
                    engine.add_document(url_id, text)
                print(f"Success! Indexed content from {url}.")
            else:
                print("Failed to crawl or empty webpage.")
                
        elif choice == "3":
            query = input("Enter your search query: ").strip()
            if not query:
                print("Query cannot be empty.")
                continue
                
            print(f"\nSearching for: '{query}'...")
            results = engine.search(query, top_k=5)
            
            if not results:
                print("No results found. Try different keywords.")
            else:
                print(f"\nTop {len(results)} Results:")
                for i, (doc_id, score, snippet) in enumerate(results, 1):
                    # Replace newlines in snippet to keep display clean
                    clean_snippet = snippet.replace('\n', ' ')
                    print(f"\n{i}. [{doc_id}] (Score: {score:.4f})")
                    print(f"   Snippet: {clean_snippet}")
                    
        elif choice == "4":
            print("Exiting Mini Search Engine. Goodbye!")
            sys.exit(0)
            
        else:
            print("Invalid option. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Mini Search Engine. Goodbye!")
        sys.exit(0)
