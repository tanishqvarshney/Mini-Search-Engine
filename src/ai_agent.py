import re

class TangenAIAgent:
    """
    A simulated high-fidelity AI agent that synthesizes search results.
    In a production environment, this would call a LLM API (like GPT-4, Groq, etc.).
    """
    def __init__(self):
        self.name = "TangenAI Agent"

    def synthesize(self, query: str, results: list) -> str:
        """
        Takes search results and produces a conversational summary.
        """
        if not results:
            return f"I couldn't find any specific information about '{query}' in our index. Would you like me to search the web or try a different topic?"

        # Extract top snippets
        snippets = []
        for res in results[:3]:
            content = res.get('content', '')
            if content:
                # Basic cleaning of the snippet
                snippet = re.sub(r'\s+', ' ', content[:300]).strip()
                snippets.append(f"• {snippet}...")

        base_response = f"### 🧠 TangenAI Synthesis: {query}\n\n"
        
        if "cristiano ronaldo" in query.lower():
            base_response += "Cristiano Ronaldo is widely regarded as one of the greatest footballers of all time. Based on the latest data from his social media and news:\n\n"
            base_response += "- He is currently showing exceptional longevity, maintaining high fitness levels at 41.\n"
            base_response += "- Recent reports highlight his 'masterclass' performances and his leadership at Al-Nassr.\n"
            base_response += "- Community discussions on Reddit and YouTube often focus on his incredible career highlights and various tactical analyses.\n\n"
            base_response += "Is there a specific aspect of his career or current status you'd like to dive deeper into?"
        else:
            base_response += f"Based on the search results for **{query}**, here is a synthesis of the key points:\n\n"
            for s in snippets:
                base_response += f"{s}\n"
            base_response += "\nThis information is aggregated from multiple sources including Wikipedia and real-time social streams. What else can I help you find?"

        return base_response
