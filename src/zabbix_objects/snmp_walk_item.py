import uuid
from typing import Any, Dict, List

from src.utils.config import SNMP_WALK_ITEM
from src.zabbix_objects.snmp_item import SNMPItem


class SNMPWalkItem:
    def __init__(self, discovery_rule_table: List[Dict[str, Any]], template_name: str):
        snmp_walk_item_data = discovery_rule_table[0]
        self.mib_module = snmp_walk_item_data["MIB Module"]

        self.delay = SNMP_WALK_ITEM.DELAY
        self.history = SNMP_WALK_ITEM.HISTORY
        self.trends = SNMP_WALK_ITEM.TRENDS
        self.type = SNMP_WALK_ITEM.TYPE
        self.value_type = SNMP_WALK_ITEM.VALUE_TYPE

        self.name = self._generate_name(snmp_walk_item_data)
        self.key = self._generate_key(self.name, template_name)
        oid_string = self._parse_oids(discovery_rule_table)
        self.snmp_oid = self._generate_snmp_oid(oid_string)
        self.description = self._preprocess_description(discovery_rule_table)

    def _parse_oids(self, discovery_rule_table: List[Dict[str, Any]]) -> str:
        oids = [entry["OID"] for entry in discovery_rule_table]
        oid_string = ""
        skipped_oids = []

        for oid in oids[2:]:
            if len(oid_string) + len(oid) + 2 <= 250:  # +2 for comma and space
                oid_string += f"{oid}, " if oid_string else oid
            else:
                skipped_oids.append(oid)

        oid_string = oid_string.rstrip(", ")

        if skipped_oids:
            print(f"\t\tWarning: {self.name} SNMP_OID length exceeded 250 characters.")
            print(
                f"\tDiscovery Rule '{self.name}' is not complete. {len(skipped_oids)} OIDs were omitted."
            )
            print(f"\t\tSkipped OIDs: {', '.join(skipped_oids)}")

        return oid_string

    def _generate_snmp_oid(self, oids):
        # Skipping Table and Entry
        return f"walk[{oids[2:]}"

    def _generate_name(self, snmp_walk_item: Dict[str, Any]) -> str:
        item_name = SNMPItem.preprocess_name(snmp_walk_item.get("Name"))
        return item_name.replace("Table", "Walk")

    def _generate_key(self, item_name: str, template_name: str) -> str:
        template_string = template_name.lower().replace(" ", ".")
        item_string = item_name.replace(" Walk", "")
        item_string = item_string.replace(" ", "-").lower()
        key = f"{template_string}.{item_string}.walk"

        if len(key) > 255:
            print(
                f"Warning: Walk Key '{key}' exceeds 255 characters and will be truncated."
            )
            return key[:255]

        return key

    def _preprocess_description(
        self, discovery_rule_table: List[Dict[str, Any]]
    ) -> str:
        mib_module = discovery_rule_table[0]["MIB Module"]
        table_description = discovery_rule_table[0]["Description"]
        description = f"MIB = {mib_module}\n{table_description}\n"
        description += (
            f"{discovery_rule_table[0]['Name']}.* {discovery_rule_table[0]['OID']}\n"
        )
        # Skip the table entry as well as the "Entry" entry
        for entry in discovery_rule_table[2:]:
            description += f"{entry['Name']} {entry['OID']}\n"
        return description.rstrip()

    @classmethod
    def generate_snmp_walk_items(
        cls, snmp_items: List[List[Dict[str, Any]]], template_name: str
    ) -> List["SNMPWalkItem"]:
        return [SNMPWalkItem(item, template_name) for item in snmp_items]

    def generate_yaml_dict(self) -> Dict[str, Any]:
        snmp_item_yaml = {
            "uuid": uuid.uuid4().hex,
            "description": self.description,
            "history": self.history,
            "delay": self.delay,
            "key": self.key,
            "name": self.name,
            "snmp_oid": self.snmp_oid,
            "trends": self.trends,
            "type": self.type,
            "value_type": self.value_type,
        }

        # Removes None/null values
        snmp_item_yaml = {k: v for k, v in snmp_item_yaml.items() if v is not None}

        return snmp_item_yaml
