class SocialManager:
    def __init__(self):
        self.sentiment_map = {
            "Positive": 2,
            "Negative": -2,
            "Neutral": 0
        }

    def update_relationship(self, agent_stats, sentiment, message_type):
        if "relationship" not in agent_stats:
            return agent_stats
        
        rel = agent_stats["relationship"]
        change = self.sentiment_map.get(sentiment, 0)
        
        # Apply quirks/preferences
        if message_type in rel.get("dynamic_preferences", []):
            if change >= 0:
                change += 3 # Bonus for preferred message type
            else:
                change += 1 # Mitigate negative if it's a preferred style? 
                # Actually plan says "increase the score more". 
                # Let's stick to positive bonus.
        
        rel["score"] += change
        rel["user_sentiment"] = sentiment
        
        # Clamp score between 0 and 100
        rel["score"] = max(0, min(100, rel["score"]))
        
        return agent_stats
