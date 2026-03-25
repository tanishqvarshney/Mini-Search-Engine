import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from crawler import DocumentLoader

urls = {
    # Football
    "Cristiano_Ronaldo": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo",
    "Lionel_Messi": "https://en.wikipedia.org/wiki/Lionel_Messi",
    "Neymar": "https://en.wikipedia.org/wiki/Neymar",
    "Zidane": "https://en.wikipedia.org/wiki/Zinedine_Zidane",
    "Ronaldinho": "https://en.wikipedia.org/wiki/Ronaldinho",
    "UEFA_Euro": "https://en.wikipedia.org/wiki/UEFA_European_Championship",
    "Copa_America": "https://en.wikipedia.org/wiki/Copa_Am%C3%A9rica",
    "Champions_League": "https://en.wikipedia.org/wiki/UEFA_Champions_League",
    "World_Cup_Football": "https://en.wikipedia.org/wiki/FIFA_World_Cup",
    "Real_Madrid": "https://en.wikipedia.org/wiki/Real_Madrid_CF",
    "Manchester_United": "https://en.wikipedia.org/wiki/Manchester_United_F.C.",
    
    # Cricket
    "Sachin_Tendulkar": "https://en.wikipedia.org/wiki/Sachin_Tendulkar",
    "Virat_Kohli": "https://en.wikipedia.org/wiki/Virat_Kohli",
    "MS_Dhoni": "https://en.wikipedia.org/wiki/MS_Dhoni",
    "Rohit_Sharma": "https://en.wikipedia.org/wiki/Rohit_Sharma",
    "Don_Bradman": "https://en.wikipedia.org/wiki/Don_Bradman",
    "Cricket_World_Cup": "https://en.wikipedia.org/wiki/Cricket_World_Cup",
    "IPL": "https://en.wikipedia.org/wiki/Indian_Premier_League",
    "Ashes": "https://en.wikipedia.org/wiki/The_Ashes"
}

loader = DocumentLoader()
out_dir = os.path.join(os.path.dirname(__file__), "data", "sample_docs")
os.makedirs(out_dir, exist_ok=True)

print(f"Starting mass ingestion of {len(urls)} sports documents...")

for name, url in urls.items():
    print(f"Crawling {name}...")
    docs = loader.crawl_webpage(url)
    if url in docs:
        doc_data = docs[url]
        # Save to JSON
        file_path = os.path.join(out_dir, f"{name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=4)
        print(f"-> Saved {name}.json")
    else:
        print(f"-> Failed to crawl {name}")

print("Ingestion complete!")
