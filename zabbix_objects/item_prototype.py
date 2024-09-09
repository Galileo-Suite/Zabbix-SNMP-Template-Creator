import re
import uuid
from typing import Any, Dict, List, Optional

from utils.config import ITEM_PROTOTYPE


class ItemPrototype:
    def __init__(self, item_data: Dict[str, Any], master_item_key: str):
        self.master_item = master_item_key
        self.mib_module = item_data.get('MIB Module')
        self.oid = item_data.get('OID')
        self.raw_description = item_data.get('Description')
        self.raw_name = item_data.get('Name')
        self.raw_type = item_data.get('Type')

        self.history = ITEM_PROTOTYPE.HISTORY
        self.type = ITEM_PROTOTYPE.TYPE

        self.name = self._preprocess_name(self.raw_name)
        self.description = self._preprocess_description()
        self.key = self._generate_key(master_item_key)
        self.value_type = self._determine_value_type()
        self.trends = self._determine_trends(ITEM_PROTOTYPE.TRENDS)

    @classmethod
    def generate_item_prototypes(cls, item_prototypes: List[Dict[str, Any]], template_name: str) -> List['ItemPrototype']:
        return [ItemPrototype(item, template_name) for item in item_prototypes]

    @staticmethod
    def _preprocess_name(raw_name: str) -> str:
        name = re.sub(r'^[^A-Z]*', '', raw_name)
        return re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', name)

    def _preprocess_description(self) -> str:
        if not self.raw_description:
            return f"{self.mib_module}::{self.raw_name}\nOID::{self.oid}\nNo description available."

        paragraphs = self.raw_description.split('\n\n')
        processed_paragraphs = []
        for paragraph in paragraphs:
            paragraph = re.sub(r'\s+', ' ', paragraph.strip())
            paragraph = paragraph.replace("'", '"')
            processed_paragraphs.append(paragraph)

        processed_description = '\n'.join(processed_paragraphs)

        return f"{self.mib_module}::{self.raw_name}\nOID::{self.oid}\n{processed_description}"

    def _generate_key(self, master_item_key: str) -> str:
        key_without_walk = master_item_key.replace(".walk", "")
        master_subkey = key_without_walk.split(".")[-1]
        item_name = self.name.replace(' ', '-').lower()
        final_item_name = item_name.replace(master_subkey, "")
        key = f"{key_without_walk}.{final_item_name.replace("-", "")}"+'[{#SNMPINDEX}]'

        if len(key) > 255:
            print(f"Warning: Key '{key}' exceeds 255 characters and will be truncated.")
            return key[:255]

        return key

    def _determine_value_type(self) -> Optional[str]:
        if self.raw_type == 'DISPLAYSTRING' or self.raw_type == 'OCTET STRING':
            return 'CHAR'

        if self.raw_type == 'Integer32':
            return None

        if self.raw_type == 'Float':
            return 'FLOAT'

        return 'TEXT'

    def _determine_trends(self, default_from_config: str) -> str:
        if (self.value_type == 'FLOAT') or (self.value_type is None):
            return default_from_config
        else:
            return '0'

    def generate_yaml_dict(self) -> Dict[str, Any]:
        item_prototype_yaml = {
            'description': self.description,
            'history': self.history,
            'key': self.key,
            'master_item': {'key': self.master_item},
            'name': self.name,
            'trends': self.trends,
            'type': self.type,
            'uuid': uuid.uuid4().hex,
            'value_type': self.value_type,
        }

        # Removes None/null values
        item_prototype_yaml = {k: v for k, v in item_prototype_yaml.items() if v is not None}

        return item_prototype_yaml
