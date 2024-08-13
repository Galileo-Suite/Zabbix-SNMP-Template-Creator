import uuid
from typing import List, Dict, Any

from zabbix_objects.snmp_walk_item import SNMPWalkItem
from zabbix_objects.item_prototype import ItemPrototype
from utils.config import DISCOVERY_RULE

class DiscoveryRule:
    def __init__(self, discovery_rule_table: List[Dict[str, Any]], template_name: str):
        self.type = DISCOVERY_RULE.TYPE

        self.snmp_walk_item = SNMPWalkItem(discovery_rule_table, template_name)
        self.master_item = self.snmp_walk_item.key
        self.item_prototypes = self._generate_item_prototypes(self.master_item, discovery_rule_table)
        self.key = self._generate_key()
        self.description = self._generate_description()
        self.name = self._generate_name()

    def _generate_name(self) -> str:
        name = self.snmp_walk_item.name
        return name.replace('Walk', 'Discovery')

    def _generate_key(self) -> str:
        master_item_key = self.snmp_walk_item.key
        return master_item_key.replace("walk", "discovery")

    def _generate_description(self) -> str:
        return self.snmp_walk_item.description

    @classmethod
    def generate_discovery_rules(cls, discovery_rule_table: Dict[str, List[Dict[str, Any]]], template_name: str) -> List['DiscoveryRule']:
        return [DiscoveryRule(table_data, template_name) for _,table_data in discovery_rule_table.items()]

    def _generate_item_prototypes(self, master_item_key: str, discovery_rule_table: List[Dict[str, Any]]) -> List[ItemPrototype]:
        # Start at 2nd index in DiscoveryRuleTable b/c the 1st entry will always be the master item
        return [ItemPrototype(entry, master_item_key) for entry in discovery_rule_table[1:]]

    def generate_yaml_dict(self) -> Dict[str, Any]:
        discovery_rule_yaml = {
            'description': self.description,
            'key': self.key,
            'master_item': {'key': self.master_item},
            'name': self.name,
            'type': self.type,
            'uuid': uuid.uuid4().hex,
        }

        item_prototype_yaml = [ item_prototype.generate_yaml_dict() for item_prototype in self.item_prototypes]

        if item_prototype_yaml:
            discovery_rule_yaml['item_prototypes'] = item_prototype_yaml
        
        # Removes None/null values
        discovery_rule_yaml = {k: v for k, v in discovery_rule_yaml.items() if v is not None}
        
        return discovery_rule_yaml