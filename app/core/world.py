from datetime import datetime
from typing import Dict, Any, Optional

class WorldEngine:
    """
    WorldEngine calculates the AI's temporal context and environmental state.
    """
    
    def get_time_context(self, current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Returns time string, day/night boolean, and suggested mood based on hour ranges.
        """
        if current_time is None:
            current_time = datetime.now()
            
        hour = current_time.hour
        time_str = current_time.strftime("%H:%M")
        
        # Simple hour-based logic for night and mood
        # Night: 22:00 to 06:00
        is_night = hour >= 22 or hour < 6
        
        # Suggested mood logic
        if 0 <= hour < 6:
            suggested_mood = "Sleepy and quiet"
        elif 6 <= hour < 12:
            suggested_mood = "Energetic and fresh"
        elif 12 <= hour < 18:
            suggested_mood = "Focused and productive"
        elif 18 <= hour < 22:
            suggested_mood = "Relaxed and winding down"
        else: # 22 <= hour < 24
            suggested_mood = "Sleepy and contemplative"
            
        return {
            "time": time_str,
            "is_night": is_night,
            "suggested_mood": suggested_mood
        }
