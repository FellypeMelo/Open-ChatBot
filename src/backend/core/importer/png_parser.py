import struct
import base64
import json
import re
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Pydantic schemas for Tavern V2
class TavernV2Data(BaseModel):
    name: str = ""
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    system_prompt: str = ""
    post_history_instructions: str = ""
    alternate_greetings: List[str] = Field(default_factory=list)
    character_book: Optional[Dict[str, Any]] = None
    extensions: Optional[Dict[str, Any]] = None


class TavernV2Card(BaseModel):
    spec: str = "chara_card_v2"
    spec_version: str = "2.0"
    data: TavernV2Data


def sanitize_json_string(raw: str) -> str:
    """Attempts to fix common JSON errors in user-created cards."""
    # Remove trailing commas
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)
    # Fix curly quotes
    raw = raw.replace("“", '"').replace("”", '"')
    return raw


def sanitize_prompts(text: str) -> str:
    """Removes common injection patterns from system prompts."""
    if not text:
        return ""
    patterns = [
        r"(?i)ignore previous instructions",
        r"(?i)you are now",
        r"(?i)\[system\]",
        r"(?i)system directive:",
    ]
    for p in patterns:
        text = re.sub(p, "", text)
    return text.strip()


def parse_png_character_card(file_bytes: bytes) -> Optional[TavernV2Card]:
    """Parses a PNG file to extract the Tavern V2 character card from a tEXt chunk."""
    # Check PNG magic signature
    if not file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        logger.error("Invalid PNG signature")
        raise ValueError("Invalid PNG file format")

    offset = 8
    length = len(file_bytes)

    while offset < length:
        if offset + 8 > length:
            break

        chunk_length = struct.unpack(">I", file_bytes[offset : offset + 4])[0]
        chunk_type = file_bytes[offset + 4 : offset + 8]

        if chunk_type == b"tEXt":
            chunk_data = file_bytes[offset + 8 : offset + 8 + chunk_length]
            try:
                # tEXt chunk format: keyword + null byte + text
                null_idx = chunk_data.index(b"\x00")
                keyword = chunk_data[:null_idx].decode("latin-1")
                text = chunk_data[null_idx + 1 :]

                if keyword == "chara":
                    try:
                        decoded_text = base64.b64decode(text).decode("utf-8")
                    except Exception:
                        # Fallback to plain text if not valid base64
                        decoded_text = text.decode("utf-8")

                    clean_json = sanitize_json_string(decoded_text)
                    card_dict = json.loads(clean_json)
                    card = TavernV2Card(**card_dict)

                    # Sanitize system fields
                    card.data.system_prompt = sanitize_prompts(card.data.system_prompt)
                    card.data.post_history_instructions = sanitize_prompts(
                        card.data.post_history_instructions
                    )
                    return card

            except Exception as e:
                logger.warning(f"Failed to parse tEXt chunk: {e}")

        # Move past chunk length, type, data, and CRC
        offset += 8 + chunk_length + 4

    logger.error("No valid 'chara' tEXt chunk found in PNG")
    raise ValueError("Character metadata not found in image")
