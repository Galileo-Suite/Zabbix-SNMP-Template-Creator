import re
import uuid
from typing import Any, Dict, List

from src.utils.config import SNMP_TRAP


class SNMPTrap:
    def __init__(self, trap_data: Dict[str, Any], template_name: str):
        self.mib_module = trap_data.get("MIB Module")
        self.oid = trap_data.get("OID")
        self.raw_description = trap_data.get("Description")
        self.raw_name = trap_data.get("Name")
        self.raw_type = trap_data.get("Type")

        self.delay = SNMP_TRAP.DELAY
        self.history = SNMP_TRAP.HISTORY
        self.trends = SNMP_TRAP.TRENDS
        self.type = SNMP_TRAP.TYPE
        self.value_type = SNMP_TRAP.VALUE_TYPE

        self.name = self._preprocess_name(self.raw_name)
        self.key = self._generate_key()
        self.description = self._preprocess_description()
        self.default_trigger = self._generate_default_trigger(template_name)

    @classmethod
    def generate_snmp_traps(
        cls, snmp_traps: List[Dict[str, Any]], template_name: str
    ) -> List["SNMPTrap"]:
        return [SNMPTrap(trap, template_name) for trap in snmp_traps]

    @staticmethod
    def _preprocess_name(raw_name: str) -> str:
        name = re.sub(r"^[^A-Z]*", "", raw_name)
        name = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)
        return name.replace(" Trap", "")

    def _preprocess_description(self) -> str:
        if not self.raw_description:
            return f"{self.mib_module}::{self.raw_name}\nOID::{self.oid}\nNo description available."

        # Process each line individually
        processed_lines = []
        for line in self.raw_description.split("\n"):
            line = re.sub(r"\s+", " ", line.strip())
            line = line.replace("'", '"')
            processed_lines.append(line)

        # Join the lines, preserving empty lines for paragraph breaks
        processed_description = "\n".join(processed_lines)

        # Add an extra newline before the processed description
        return f"{self.mib_module}::{self.raw_name}\nOID::{self.oid}\n{processed_description}"

    def _generate_key(self) -> str:
        key = f'snmptrap["{self.oid}"]'
        if len(key) > 255:
            print(f"Warning: Key '{key}' exceeds 255 characters and will be truncated.")
            return key[:255]

        return key

    def _generate_default_trigger(self, template_name: str) -> Dict[str, Any]:
        """
        Generate a default trigger for the SNMP trap.

        Args:
            template_name (str): Name of the template.

        Returns:
            Dict[str, Any]: Dictionary representing the default trigger.
        """
        default_trigger = {
            "description": self.description,
            "expression": f"length(last(/{template_name}/{self.key}))>0",
            "manual_close": SNMP_TRAP.TRIGGER.CLOSE,
            "name": self.name,
            "priority": SNMP_TRAP.TRIGGER.PRIORITY,
            "tags": [{"tag": "snmp_trap", "value": ""}],
            "type": SNMP_TRAP.TRIGGER.TYPE,
            "uuid": uuid.uuid4().hex,
        }
        return default_trigger

    def generate_yaml_dict(self) -> Dict[str, Any]:
        snmp_trap_yaml = {
            "delay": self.delay,
            "description": self.description,
            "history": self.history,
            "key": self.key,
            "name": self.name,
            "trends": self.trends,
            "triggers": [self.default_trigger],
            "type": self.type,
            "uuid": uuid.uuid4().hex,
            "value_type": self.value_type,
        }

        # Removes None/null values
        snmp_trap_yaml = {k: v for k, v in snmp_trap_yaml.items() if v is not None}

        return snmp_trap_yaml
