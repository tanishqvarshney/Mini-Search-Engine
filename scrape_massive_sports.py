import os
import json
import time
from src.crawler import DocumentLoader

def main():
    loader = DocumentLoader()
    data_dir = "data/sample_docs"
    os.makedirs(data_dir, exist_ok=True)

    entities = {
        # CRICKET - Players
        "Virat_Kohli": "https://en.wikipedia.org/wiki/Virat_Kohli",
        "MS_Dhoni": "https://en.wikipedia.org/wiki/MS_Dhoni",
        "Sachin_Tendulkar": "https://en.wikipedia.org/wiki/Sachin_Tendulkar",
        "Rohit_Sharma": "https://en.wikipedia.org/wiki/Rohit_Sharma",
        "Steve_Smith": "https://en.wikipedia.org/wiki/Steve_Smith_(cricketer)",
        "Kane_Williamson": "https://en.wikipedia.org/wiki/Kane_Williamson",
        "Joe_Root": "https://en.wikipedia.org/wiki/Joe_Root",
        "Babar_Azam": "https://en.wikipedia.org/wiki/Babar_Azam",
        "Hardik_Pandya": "https://en.wikipedia.org/wiki/Hardik_Pandya",
        "Jasprit_Bumrah": "https://en.wikipedia.org/wiki/Jasprit_Bumrah",
        "Ben_Stokes": "https://en.wikipedia.org/wiki/Ben_Stokes",
        "Pat_Cummins": "https://en.wikipedia.org/wiki/Pat_Cummins",
        "Mitchell_Starc": "https://en.wikipedia.org/wiki/Mitchell_Starc",
        "Rashid_Khan": "https://en.wikipedia.org/wiki/Rashid_Khan",
        
        # CRICKET - Teams & Tournaments
        "Indian_Cricket_Team": "https://en.wikipedia.org/wiki/India_national_cricket_team",
        "Australia_Cricket_Team": "https://en.wikipedia.org/wiki/Australia_men%27s_national_cricket_team",
        "England_Cricket_Team": "https://en.wikipedia.org/wiki/England_cricket_team",
        "Pakistan_Cricket_Team": "https://en.wikipedia.org/wiki/Pakistan_national_cricket_team",
        "IPL": "https://en.wikipedia.org/wiki/Indian_Premier_League",
        "Cricket_World_Cup": "https://en.wikipedia.org/wiki/Cricket_World_Cup",
        "The_Ashes": "https://en.wikipedia.org/wiki/The_Ashes",
        "WPL": "https://en.wikipedia.org/wiki/Women%27s_Premier_League_(cricket)",
        
        # FOOTBALL - Players
        "Lionel_Messi": "https://en.wikipedia.org/wiki/Lionel_Messi",
        "Cristiano_Ronaldo": "https://en.wikipedia.org/wiki/Cristiano_Ronaldo",
        "Kylian_Mbappe": "https://en.wikipedia.org/wiki/Kylian_Mbapp%C3%A9",
        "Erling_Haaland": "https://en.wikipedia.org/wiki/Erling_Haaland",
        "Neymar": "https://en.wikipedia.org/wiki/Neymar",
        "Kevin_De_Bruyne": "https://en.wikipedia.org/wiki/Kevin_De_Bruyne",
        "Mohamed_Salah": "https://en.wikipedia.org/wiki/Mohamed_Salah",
        "Lamine_Yamal": "https://en.wikipedia.org/wiki/Lamine_Yamal",
        "Jude_Bellingham": "https://en.wikipedia.org/wiki/Jude_Bellingham",
        "Vinicius_Junior": "https://en.wikipedia.org/wiki/Vin%C3%ADcius_J%C3%BAnior",
        "Harry_Kane": "https://en.wikipedia.org/wiki/Harry_Kane",
        
        # FOOTBALL - Clubs & Tournaments
        "Real_Madrid": "https://en.wikipedia.org/wiki/Real_Madrid_CF",
        "Manchester_City": "https://en.wikipedia.org/wiki/Manchester_City_F.C.",
        "FC_Barcelona": "https://en.wikipedia.org/wiki/FC_Barcelona",
        "Liverpool_FC": "https://en.wikipedia.org/wiki/Liverpool_F.C.",
        "Arsenal_FC": "https://en.wikipedia.org/wiki/Arsenal_F.C.",
        "Manchester_United": "https://en.wikipedia.org/wiki/Manchester_United_F.C.",
        "FIFA_World_Cup": "https://en.wikipedia.org/wiki/FIFA_World_Cup",
        "UEFA_Champions_League": "https://en.wikipedia.org/wiki/UEFA_Champions_League",
        "Premier_League": "https://en.wikipedia.org/wiki/Premier_League",
        "La_Liga": "https://en.wikipedia.org/wiki/La_Liga",
        
        # OTHER SPORTS & VENUES
        "Roger_Federer": "https://en.wikipedia.org/wiki/Roger_Federer",
        "Rafael_Nadal": "https://en.wikipedia.org/wiki/Rafael_Nadal",
        "Novak_Djokovic": "https://en.wikipedia.org/wiki/Novak_Djokovic",
        "Usain_Bolt": "https://en.wikipedia.org/wiki/Usain_Bolt",
        "LeBron_James": "https://en.wikipedia.org/wiki/LeBron_James",
        "Wimbledon": "https://en.wikipedia.org/wiki/The_Championships,_Wimbledon",
        "Olympics": "https://en.wikipedia.org/wiki/Olympic_Games",
        "Lords_Cricket_Ground": "https://en.wikipedia.org/wiki/Lord%27s",
        "Wembley_Stadium": "https://en.wikipedia.org/wiki/Wembley_Stadium",
        "Wankhede_Stadium": "https://en.wikipedia.org/wiki/Wankhede_Stadium",
        "Narendra_Modi_Stadium": "https://en.wikipedia.org/wiki/Narendra_Modi_Stadium"
    }

    print(f"Starting massive ingestion of {len(entities)} entities...")
    
    for name, url in entities.items():
        print(f"Crawling {name}...")
        try:
            docs = loader.crawl_webpage(url)
            if docs:
                for url_id, data in docs.items():
                    filename = f"{name}.json"
                    file_path = os.path.join(data_dir, filename)
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                print(f"-> Saved {name}.json")
            time.sleep(1) # Be nice to Wiki
        except Exception as e:
            print(f"Failed to crawl {name}: {e}")

    print("\nMassive Ingestion complete!")

if __name__ == "__main__":
    main()
