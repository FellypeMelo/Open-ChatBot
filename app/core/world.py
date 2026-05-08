from datetime import datetime
from typing import Dict, Any, Optional

class WorldEngine:
    """
    WorldEngine calculates the AI's temporal context and environmental state.
    """
    
    # Biological drain/recovery rates (per hour)
    ENERGY_DRAIN_RATE = 5.0
    ENERGY_RECOVERY_RATE = 10.0
    HUNGER_INCREASE_RATE = 10.0
    SOCIAL_DECREASE_RATE = 5.0
    HAPPINESS_DECREASE_RATE = 2.0

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

    def _calculate_hours_passed(self, stats: Dict[str, Any], current_time: datetime) -> float:
        """
        Helper to calculate hours passed since last update.
        """
        last_update_str = stats.get("last_update")
        if not last_update_str:
            return 0.0
        last_update = datetime.fromisoformat(last_update_str)
        duration = current_time - last_update
        return duration.total_seconds() / 3600.0

    def update_energy(self, stats: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
        """
        Calculates energy drain or recovery based on time passed.
        """
        hours_passed = self._calculate_hours_passed(stats, current_time)
        current_energy = stats.get("energy", 100)
        was_sleeping = stats.get("is_sleeping", False)
        
        if was_sleeping:
            new_energy = current_energy + (hours_passed * self.ENERGY_RECOVERY_RATE)
        else:
            new_energy = current_energy - (hours_passed * self.ENERGY_DRAIN_RATE)
            
        # Clamp energy between 0 and 100
        new_energy = max(0, min(100, new_energy))
        
        updated = stats.copy()
        updated.update({
            "energy": int(new_energy),
            "last_update": current_time.isoformat(),
            "is_sleeping": was_sleeping
        })
        return updated

    def update_needs(self, stats: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
        """
        Updates hunger, happiness, social, and energy based on time passed.
        """
        hours_passed = self._calculate_hours_passed(stats, current_time)
        
        # Start with energy update which also updates last_update
        updated_stats = self.update_energy(stats, current_time)
        
        # Hunger: increases
        current_hunger = stats.get("hunger", 0)
        new_hunger = current_hunger + (hours_passed * self.HUNGER_INCREASE_RATE)
        updated_stats["hunger"] = int(max(0, min(100, new_hunger)))
        
        # Social: decreases
        current_social = stats.get("social", 100)
        new_social = current_social - (hours_passed * self.SOCIAL_DECREASE_RATE)
        updated_stats["social"] = int(max(0, min(100, new_social)))
        
        # Happiness: decreases
        current_happiness = stats.get("happiness", 100)
        new_happiness = current_happiness - (hours_passed * self.HAPPINESS_DECREASE_RATE)
        updated_stats["happiness"] = int(max(0, min(100, new_happiness)))
        
        return updated_stats

    def should_be_sleeping(self, stats: Dict[str, Any], current_time: datetime) -> bool:
        """
        Returns True if energy < 20 OR it's between 11 PM and 6 AM.
        """
        energy = stats.get("energy", 100)
        hour = current_time.hour
        
        # Late night: 11 PM to 6 AM
        is_late_night = hour >= 23 or hour < 6
        
        return energy < 20 or is_late_night
