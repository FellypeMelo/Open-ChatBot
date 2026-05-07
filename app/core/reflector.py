import json
import logging

class Reflector:
    def __init__(self, llm):
        self.llm = llm

    async def reflect(self, messages: list[dict]) -> dict:
        """
        Summarizes the interaction and identifies new traits or facts.
        Returns a dictionary with 'summary', 'facts', and 'traits'.
        """
        # Resource Efficiency: Limit to last 10 messages
        recent_messages = messages[-10:]
        
        # Structured Output: Ask for JSON
        prompt = (
            "Summarize the following interaction and identify any new traits or facts about the user. "
            "Respond ONLY with a valid JSON object containing 'summary', 'facts', and 'traits'.\n\n"
        )
        for msg in recent_messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        try:
            response = await self.llm.complete(prompt)
            content = response.get("content", "{}")
            # Attempt to parse JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logging.error(f"Failed to parse reflector response: {content}")
                return {
                    "summary": content,
                    "facts": [],
                    "traits": []
                }
        except Exception as e:
            logging.error(f"LLM call failed in reflector: {e}")
            return {
                "summary": "Error during reflection.",
                "facts": [],
                "traits": []
            }
