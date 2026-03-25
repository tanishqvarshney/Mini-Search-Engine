import os

def create_project_structure():
    # Define the project directory structure
    directories = [
        "data/sample_docs",
        "src"
    ]
    
    # Define the files to create
    files = {
        "src/__init__.py": "",
        "src/crawler.py": "# Module for document loading and web crawling\n",
        "src/preprocess.py": "# Module for text preprocessing (tokenization, stopwords, etc.)\n",
        "src/indexer.py": "# Module for creating the inverted index\n",
        "src/ranker.py": "# Module for TF-IDF ranking logic\n",
        "src/search.py": "# Module for handling user queries\n",
        "main.py": "# Main entry point for the mini search engine\n",
        "README.md": "# Mini Search Engine\nA production-quality modular search engine in Python.\n",
        "data/sample_docs/doc1.txt": "Python is a high-level, general-purpose programming language.",
        "data/sample_docs/doc2.txt": "Search engines use web crawlers to index the web.",
        "data/sample_docs/doc3.txt": "TF-IDF stands for Term Frequency-Inverse Document Frequency. It is used in information retrieval."
    }

    print("Creating project folders...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

    print("\nCreating skeleton files...")
    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created file: {filepath}")

    print("\nProject structure initialized successfully!")

if __name__ == "__main__":
    create_project_structure()
