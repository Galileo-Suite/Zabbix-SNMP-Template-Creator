from typing import Dict, List


class Tag:
    def __init__(self, key: str, value: str):
        self.key = self._process_tag_key(key)
        self.value = self._process_tag_value(value)

    @staticmethod
    def _parse_tag_string(tag_string: str) -> List[List[str]]:
        return [
            pair.strip().split(":")
            for pair in tag_string.strip("{}").split(",")
            if ":" in pair
        ]

    @classmethod
    def generate_template_tags(
        cls, raw_tags: str, manufacturer: str, device: str
    ) -> List["Tag"]:
        tags = []
        tags.extend(cls._parse_tag_string(f"{{target:{manufacturer}}}"))
        tags.extend(cls._parse_tag_string(f"{{target:{device}}}"))

        if raw_tags:
            tags.extend(cls._parse_tag_string(raw_tags))

        return [Tag(key, value) for key, value in tags]

    @staticmethod
    def _process_tag_key(key: str) -> str:
        key = str(key).strip()
        return key.lower().replace(" ", "_")

    @staticmethod
    def _process_tag_value(value: str) -> str:
        value = str(value).strip()
        return value.lower().replace(" ", "_")

    def generate_yaml_dict(self) -> Dict[str, str]:
        tag_yaml = {"tag": self.key, "value": self.value}

        return tag_yaml
