import re
import uuid
from typing import List, Dict, Any, Optional

from src.utils.config import SNMP_ITEM

class SNMPItem:
    def __init__(self, item_data: Dict[str, Any], template_name: str):
        self.mib_module = item_data.get('MIB Module')
        self.oid = item_data.get('OID')
        self.raw_description = item_data.get('Description')
        self.raw_name = item_data.get('Name')
        self.raw_type = item_data.get('Type')

        self.delay = SNMP_ITEM.DELAY
        self.history = SNMP_ITEM.HISTORY
        self.type = SNMP_ITEM.TYPE

        self.name = self._preprocess_name(self.raw_name)
        self.description = self._preprocess_description()
        self.key = self._generate_key(template_name)
        self.value_type = self._determine_value_type()
        self.snmp_oid = self._generate_snmp_oid()        
        self.trends = self._determine_trends(SNMP_ITEM.TRENDS)

    @classmethod
    def generate_snmp_items(cls, snmp_items: List[Dict[str, Any]], template_name: str) -> List['SNMPItem']:
        return [SNMPItem(item, template_name) for item in snmp_items]

    @staticmethod
    def _preprocess_name(raw_name: str) -> str:
        name = re.sub(r'^[^A-Z]*', '', raw_name)
        return re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', name)

    def _generate_snmp_oid(self) -> str:
        return f'get[{self.oid}]'

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

    def _generate_key(self, template_name: str) -> str:
        item_name = self.name.replace(' ', '-').lower()
        key = f'{template_name.lower().replace(' ', '.')}.{item_name}.get'

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
        snmp_item_yaml = {
            'description': self.description,
            'history': self.history,
            'delay': self.delay,
            'key': self.key,
            'name': self.name,
            'snmp_oid': self.oid,
            'trends': self.trends,
            'type': self.type,
            'uuid': uuid.uuid4().hex,
            'value_type': self.value_type,
        }

        # Removes None/null values
        snmp_item_yaml = {k: v for k, v in snmp_item_yaml.items() if v is not None}

        return snmp_item_yaml
