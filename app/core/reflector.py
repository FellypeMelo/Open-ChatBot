class Reflector:
    def __init__(self, llm):
        self.llm = llm

    async def reflect(self, messages: list[dict]) -> str:
        """
        Summarizes the interaction and identifies new traits or facts.
        """
        prompt = "Summarize the following interaction and identify any new traits or facts about the user:\n\n"
        for msg in messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        response = await self.llm.complete(prompt)
        return response.get("content", "")
