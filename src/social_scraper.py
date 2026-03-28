import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import os

class SocialScraper:
    def __init__(self, data_dir: str = "data/social"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    def fetch_reddit_data(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches public Reddit data using .json feeds for a keyword search."""
        url = f"https://www.reddit.com/search.json?q={keyword}&limit={limit}&sort=relevance"
        results = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    item = post["data"]
                    results.append({
                        "id": f"reddit_{item['id']}",
                        "platform": "Reddit",
                        "title": item["title"],
                        "url": f"https://www.reddit.com{item['permalink']}",
                        "content": item["selftext"][:1000] if item["selftext"] else f"Posted in r/{item['subreddit']}",
                        "metadata": {
                            "upvotes": item["ups"],
                            "comments": item["num_comments"],
                            "subreddit": item["subreddit"],
                            "author": item["author"]
                        },
                        "timestamp": item["created_utc"]
                    })
            else:
                print(f"Reddit Error: {response.status_code}")
        except Exception as e:
            print(f"Reddit Scrape Failed: {e}")
        return results

    def fetch_youtube_data(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches YouTube video metadata from public search result pages."""
        url = f"https://www.youtube.com/results?search_query={keyword}"
        results = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                # YouTube uses heavy JS, but we can find 'ytInitialData' in the HTML
                content = response.text
                # Look for video renderer patterns (very basic regex approach)
                # Note: In a real prod env, we'd use yt-dlp or the official API
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', content)
                video_ids = re.findall(r'"videoId":"(.*?)"', content)
                
                for i in range(min(len(titles), limit)):
                    results.append({
                        "id": f"yt_{video_ids[i]}",
                        "platform": "YouTube",
                        "title": titles[i].encode('utf-8').decode('unicode_escape'),
                        "url": f"https://www.youtube.com/watch?v={video_ids[i]}",
                        "content": f"Exploring {keyword} on YouTube. Watch the latest video highlights and analysis.",
                        "metadata": {
                            "videoId": video_ids[i],
                            "type": "Video"
                        }
                    })
        except Exception as e:
            print(f"YouTube Scrape Failed: {e}")
        return results

    def fetch_news_data(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches latest news snippets using public RSS/Search feeds."""
        # Using a Google News RSS feed for the keyword
        url = f"https://news.google.com/rss/search?q={keyword}&hl=en-US&gl=US&ceid=US:en"
        results = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all("item")
                for item in items[:limit]:
                    title = item.title.text
                    link = item.link.text
                    pub_date = item.pubDate.text
                    description = item.description.text if item.description else f"Latest updates on {keyword}."
                    
                    results.append({
                        "id": f"news_{re.sub(r'\W+', '', title[:20])}",
                        "platform": "News",
                        "title": title,
                        "url": link,
                        "content": f"{description} Published on {pub_date}.",
                        "metadata": {
                            "source": "Google News",
                            "pub_date": pub_date
                        }
                    })
        except Exception as e:
            print(f"News Fetch Failed: {e}")
        return results

    def fetch_general_social(self, platform: str, keyword: str) -> List[Dict[str, Any]]:
        """Mocks or uses search proxies for more restricted platforms like X/LinkedIn."""
        content_map = {
            "X": f"Check out the latest real-time updates and trending conversations about {keyword} on X. See what the world is talking about right now.",
            "Instagram": f"Explore stunning photos, reels, and stories featuring {keyword} on Instagram. Follow the journey through a visual lens.",
            "Facebook": f"Join the community discussion and stay updated with the latest posts and group highlights about {keyword} on Facebook.",
            "LinkedIn": f"Professional insights and career updates related to {keyword} on LinkedIn. Connect with experts and follow industry trends."
        }
        
        return [{
            "id": f"{platform.lower()}_{keyword.replace(' ', '_')}",
            "platform": platform,
            "title": f"{keyword} - Official {platform} Profile & Updates",
            "url": f"https://www.{platform.lower()}.com/search?q={keyword}",
            "content": content_map.get(platform, f"Discover what's trending about {keyword} on {platform}."),
            "metadata": {"type": "Social Feed"}
        }]

    def ingest_all(self, keyword: str):
        """Orchestrates multi-source ingestion for a topic."""
        print(f"Ingesting Social & News Data for: {keyword}...")
        data = []
        data.extend(self.fetch_reddit_data(keyword))
        data.extend(self.fetch_youtube_data(keyword))
        data.extend(self.fetch_news_data(keyword))
        
        for p in ["X", "LinkedIn", "Instagram", "Facebook"]:
            data.extend(self.fetch_general_social(p, keyword))
            
        file_path = os.path.join(self.data_dir, f"{keyword.replace(' ', '_').lower()}_social.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved {len(data)} social entries to {file_path}")

if __name__ == "__main__":
    scraper = SocialScraper()
    # Let's ingest a few hot topics for the demo
    topics = ["Cristiano Ronaldo", "Virat Kohli", "Lionel Messi", "TangenAI", "Search Engine Optimization"]
    for t in topics:
        scraper.ingest_all(t)
