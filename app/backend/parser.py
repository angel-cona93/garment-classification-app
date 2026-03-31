import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

EXPECTED_ATTRIBUTES = [
    "garment_type", "style", "material", "color_palette", "pattern",
    "season", "occasion", "consumer_profile", "trend_notes",
]

# Precompiled patterns for parsing model output
_RE_DESCRIPTION = re.compile(r"DESCRIPTION:\s*(.+?)(?=ATTRIBUTES:|$)", re.DOTALL)
_RE_ATTRIBUTES = re.compile(r"ATTRIBUTES:\s*(.*)", re.DOTALL)
_RE_CODE_FENCE_START = re.compile(r"^```(?:json)?\s*")
_RE_CODE_FENCE_END = re.compile(r"\s*```\s*$")
_RE_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_classification(raw_text: str) -> dict[str, Any]:
    """Extract description and attributes from model response text.

    Expects the format:
        DESCRIPTION: <text>
        ATTRIBUTES: <json>
    """
    result: dict[str, Any] = {"description": None, "attributes": {}}

    if not raw_text or not raw_text.strip():
        return result

    desc_match = _RE_DESCRIPTION.search(raw_text)
    if desc_match:
        result["description"] = desc_match.group(1).strip()

    attr_match = _RE_ATTRIBUTES.search(raw_text)
    if attr_match:
        json_str = attr_match.group(1).strip()
        # Strip markdown code fences some models wrap JSON in
        json_str = _RE_CODE_FENCE_START.sub("", json_str)
        json_str = _RE_CODE_FENCE_END.sub("", json_str)
        obj_match = _RE_JSON_OBJECT.search(json_str)
        if obj_match:
            try:
                result["attributes"] = json.loads(obj_match.group(0))
            except json.JSONDecodeError:
                logger.warning("Failed to parse attributes JSON: %.200s", json_str)

    return result
