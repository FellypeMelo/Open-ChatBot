import json
from sqlalchemy.orm import Session
from app.core.llm import LlamaClient
from app.db.models import Tag

class Profiler:
    def __init__(self, llama: LlamaClient):
        self.llama = llama

    async def suggest_tags(self, description: str, db: Session) -> list[int]:
        """
        Analyzes a character description and returns a list of suggested tag IDs from the existing library.
        """
        # 1. Fetch available tags
        all_tags = db.query(Tag).all()
        if not all_tags:
            return []

        tag_list_str = "\n".join([f"- ID {t.id}: {t.label} ({t.instruction})" for t in all_tags])

        # 2. Build analysis prompt
        prompt = f"""### TASK ###
Analyze the following character description and select the most appropriate personality tags from the provided list.
Return ONLY a valid JSON list of IDs.

### DESCRIPTION ###
{description}

### AVAILABLE TAGS ###
{tag_list_str}

### RESPONSE (JSON IDs ONLY) ###
"""
        
        # 3. Call LLM
        result = await self.llama.complete(prompt)
        content = result.get("content", "[]")
        
        try:
            # Clean possible markdown block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            ids = json.loads(content)
            if isinstance(ids, list):
                # Validate IDs exist
                valid_ids = [t.id for t in all_tags]
                return [i for i in ids if i in valid_ids]
        except:
            return []
        
        return []
