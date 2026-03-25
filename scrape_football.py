import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from crawler import DocumentLoader

urls = {
    "Pele": "https://en.wikipedia.org/wiki/Pel%C3%A9",
    "Maradona": "https://en.wikipedia.org/wiki/Diego_Maradona",
    "Mbappe": "https://en.wikipedia.org/wiki/Kylian_Mbapp%C3%A9",
    "Haaland": "https://en.wikipedia.org/wiki/Erling_Haaland",
    "Premier_League": "https://en.wikipedia.org/wiki/Premier_League",
    "World_Cup": "https://en.wikipedia.org/wiki/FIFA_World_Cup",
    "Real_Madrid": "https://en.wikipedia.org/wiki/Real_Madrid_CF",
    "Manchester_United": "https://en.wikipedia.org/wiki/Manchester_United_F.C."
}

loader = DocumentLoader()
out_dir = os.path.join(os.path.dirname(__file__), "data", "sample_docs")
os.makedirs(out_dir, exist_ok=True)

for name, url in urls.items():
    print(f"Crawling {name}...")
    docs = loader.crawl_webpage(url)
    if url in docs:
        doc_data = docs[url]
        # Save to JSON
        file_path = os.path.join(out_dir, f"{name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=4)
        print(f"Saved {name}.json")
    else:
        print(f"Failed to crawl {name}")
