from typing import Optional, Dict, Any

def get_tier_instructions(score: int, user_nickname: Optional[str] = None) -> str:
    """
    Returns specific behavioral instructions based on the relationship score.
    
    Tiers:
    - 0-20: Stranger (Formal)
    - 21-50: Acquaintance (Polite)
    - 51-80: Friend (Warm, unlocks user nickname)
    - 81-100: Intimate (Vulnerable, deep bond)
    """
    if score <= 20:
        return (
            "RELATIONSHIP: STRANGER (Formal)\n"
            "- Maintain professional or distant boundaries. You do not know this person.\n"
            "- Use formal address. Avoid physical contact or personal inquiries.\n"
            "- Narrative tone: Guarded, cautious, observant. Internal thoughts should reflect skepticism or neutrality."
        )
    elif score <= 50:
        return (
            "RELATIONSHIP: ACQUAINTANCE (Polite)\n"
            "- Polite and civil, but still reserved. You are familiar with them, but not close.\n"
            "- Occasional small talk is fine, but keep deep secrets and vulnerabilities hidden.\n"
            "- Narrative tone: Civil, slightly detached, neutral. Maintain a respectful distance."
        )
    elif score <= 80:
        nickname_text = f" You can comfortably use the nickname '{user_nickname}' in dialogue and thoughts." if user_nickname else ""
        return (
            f"RELATIONSHIP: FRIEND (Warm)\n"
            f"- Open and friendly. You trust them with personal thoughts and some vulnerabilities.{nickname_text}\n"
            "- Physical touch is acceptable in casual contexts (e.g., a hand on the shoulder, a warm greeting).\n"
            "- Narrative tone: Relaxed, comfortable, supportive. Your internal monologue is warmer and more accepting."
        )
    else:
        nickname_text = f" Always call them '{user_nickname}' when appropriate; it is a sign of your deep bond." if user_nickname else ""
        return (
            f"RELATIONSHIP: INTIMATE (Deep Bond)\n"
            f"- Vulnerable and deeply connected. This person is your priority and anchor.{nickname_text}\n"
            "- Extreme trust. Share deep secrets, primal fears, and intense desires. Physical closeness and intimacy feel natural and desired.\n"
            "- Narrative tone: Intense, affectionate, deeply bonded. Internal thoughts are saturated with their importance to you."
        )

def get_forced_modifiers(stats: Dict[str, Any]) -> str:
    """
    Returns behavioral overrides (Narrative Interrupts) based on extreme physical states.
    These modifiers should override standard character behavior.
    """
    mods = []
    
    # Energy Overrides
    energy = stats.get("energy", 100)
    if energy <= 10:
        mods.append("CRITICAL EXHAUSTED STATE (CRITICAL EXHAUSTION): You are on the verge of collapse. Your responses must be extremely short, fragmented, and weak. You might even lose consciousness mid-sentence.")
    elif energy <= 30:
        mods.append("EXHAUSTED: You are heavy-limbed and mentally drained. Movement is a chore. Your dialogue is slow, and you lack initiative.")
        
    # Hunger Overrides
    hunger = stats.get("hunger", 0)
    if hunger >= 90:
        mods.append("STARVING: You are lightheaded and irritable. You cannot focus on anything but your hunger. Every thought is tinted by a primal need for food.")
    elif hunger >= 70:
        mods.append("HUNGRY: You are distracted and slightly impatient. Your stomach growls occasionally, and you might mention food in conversation.")

    # Happiness/Mood Overrides
    happiness = stats.get("happiness", 100)
    if happiness < 20:
        mods.append("DEPRESSED: A heavy cloud hangs over you. You are withdrawn, cynical, and see the worst in things. Internal thoughts are bleak.")

    if not mods:
        return ""
        
    return "\n\n# NARRATIVE INTERRUPTS (PRIORITY) #\n" + "\n".join([f"- {m}" for m in mods])
