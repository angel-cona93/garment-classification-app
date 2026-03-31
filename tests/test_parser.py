import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app", "backend"))

from parser import parse_classification


class TestParseClassification:
    def test_happy_path(self):
        raw = """DESCRIPTION: A stunning red silk evening dress with intricate gold embroidery along the neckline. The dress features a fitted bodice and flowing A-line skirt, perfect for formal occasions.
ATTRIBUTES: {"garment_type": "dress", "style": "formal", "material": "silk", "color_palette": "red, gold", "pattern": "solid", "season": "fall/winter", "occasion": "evening", "consumer_profile": "luxury", "trend_notes": "quiet luxury"}"""

        result = parse_classification(raw)

        assert result["description"] is not None
        assert "red silk evening dress" in result["description"]
        attrs = result["attributes"]
        assert attrs["garment_type"] == "dress"
        assert attrs["style"] == "formal"
        assert attrs["material"] == "silk"
        assert attrs["color_palette"] == "red, gold"
        assert attrs["pattern"] == "solid"
        assert attrs["season"] == "fall/winter"
        assert attrs["occasion"] == "evening"
        assert attrs["consumer_profile"] == "luxury"
        assert attrs["trend_notes"] == "quiet luxury"

    def test_json_in_code_fence(self):
        raw = """DESCRIPTION: A casual denim jacket with distressed details.
ATTRIBUTES: ```json
{"garment_type": "jacket", "style": "streetwear", "material": "denim", "color_palette": "blue", "pattern": "solid", "season": "transitional", "occasion": "casual", "consumer_profile": "teen", "trend_notes": "Y2K revival"}
```"""

        result = parse_classification(raw)
        assert result["description"] == "A casual denim jacket with distressed details."
        assert result["attributes"]["garment_type"] == "jacket"
        assert result["attributes"]["style"] == "streetwear"

    def test_missing_description(self):
        raw = """ATTRIBUTES: {"garment_type": "skirt", "style": "bohemian"}"""
        result = parse_classification(raw)
        assert result["description"] is None
        assert result["attributes"]["garment_type"] == "skirt"

    def test_missing_attributes(self):
        raw = """DESCRIPTION: A beautiful floral dress perfect for spring."""
        result = parse_classification(raw)
        assert result["description"] == "A beautiful floral dress perfect for spring."
        assert result["attributes"] == {}

    def test_malformed_json(self):
        raw = """DESCRIPTION: A knitted sweater.
ATTRIBUTES: {garment_type: "knitwear" this is not valid json}"""
        result = parse_classification(raw)
        assert result["description"] == "A knitted sweater."
        assert result["attributes"] == {}

    def test_empty_input(self):
        result = parse_classification("")
        assert result["description"] is None
        assert result["attributes"] == {}

    def test_none_like_input(self):
        result = parse_classification("   ")
        assert result["description"] is None
        assert result["attributes"] == {}

    def test_all_expected_attributes_present(self):
        raw = """DESCRIPTION: Test garment.
ATTRIBUTES: {"garment_type": "top", "style": "casual", "material": "cotton", "color_palette": "white", "pattern": "solid", "season": "spring/summer", "occasion": "casual", "consumer_profile": "young professional", "trend_notes": "minimalism"}"""

        result = parse_classification(raw)
        expected_keys = [
            "garment_type", "style", "material", "color_palette", "pattern",
            "season", "occasion", "consumer_profile", "trend_notes",
        ]
        for key in expected_keys:
            assert key in result["attributes"], f"Missing key: {key}"

    def test_extra_whitespace_in_format(self):
        raw = """DESCRIPTION:   A loose cotton blouse with ruffled sleeves.

ATTRIBUTES:   {"garment_type": "blouse", "style": "romantic"}  """

        result = parse_classification(raw)
        assert "cotton blouse" in result["description"]
        assert result["attributes"]["garment_type"] == "blouse"
