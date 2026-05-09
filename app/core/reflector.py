import json
import logging

REFLECTION_GRAMMAR = r'''
root ::= "{" space "\"summary\"" ":" space string "," space "\"facts\"" ":" space list "," space "\"traits\"" ":" space list space "}"
list ::= "[" space (string ("," space string)*)? space "]"
string ::= "\"" ([^"\\] | "\\" ["\\/bfnrt] | "\\u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])* "\""
space ::= [ \t\n\r]*
'''

class Reflector:
    def __init__(self, llm):
        self.llm = llm

    async def reflect(self, messages: list[dict]) -> dict:
        """
        Summarizes the interaction and identifies new traits or facts.
        """
        recent_messages = messages[-10:]
        prompt = (
            "Analyze the interaction. Extract a brief summary, new facts about the user, and character trait updates. "
            "Respond ONLY with a JSON object.\n\n"
        )
        for msg in recent_messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        try:
            # Use grammar for structured output
            response = await self.llm.complete(prompt, grammar=REFLECTION_GRAMMAR)
            content = response.get("content", "{}")
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logging.error(f"Failed to parse reflector response: {content}")
                return {"summary": content, "facts": [], "traits": []}
        except Exception as e:
            logging.error(f"LLM call failed in reflector: {e}")
            return {"summary": "Error during reflection.", "facts": [], "traits": []}
