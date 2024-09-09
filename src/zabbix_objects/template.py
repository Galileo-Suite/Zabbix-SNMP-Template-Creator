import concurrent.futures
import uuid
from typing import Any, Dict, List

from src.zabbix_objects.discovery_rule import DiscoveryRule
from src.zabbix_objects.snmp_item import SNMPItem
from src.zabbix_objects.snmp_trap import SNMPTrap
from src.zabbix_objects.tag import Tag


class Template:
    def __init__(
        self,
        template_info_json: Dict[str, Any],
        snmp_item_json_list: List[Dict[str, Any]],
        snmp_trap_json_list: List[Dict[str, Any]],
        discovery_rule_tables: Dict[str, List[Dict[str, Any]]],
    ):
        self.group = template_info_json.get("Group")
        self.macros = template_info_json.get("Macros")
        self.manufacturer = template_info_json.get("Manufacturer")
        self.model = template_info_json.get("Model")
        self.raw_tags = template_info_json.get("Tags")
        self.device = template_info_json.get("Device")

        self.name = self._generate_template_name()

        self.template_tags = Tag.generate_template_tags(
            self.raw_tags, self.manufacturer, self.device
        )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_items = executor.submit(
                SNMPItem.generate_snmp_items, snmp_item_json_list, self.name
            )
            future_traps = executor.submit(
                SNMPTrap.generate_snmp_traps, snmp_trap_json_list, self.name
            )
            future_discovery_rules = executor.submit(
                DiscoveryRule.generate_discovery_rules, discovery_rule_tables, self.name
            )

            self.snmp_items = future_items.result()
            self.snmp_traps = future_traps.result()
            self.discovery_rules = future_discovery_rules.result()

        for discovery_rule in self.discovery_rules:
            if discovery_rule.snmp_walk_item:
                self.snmp_items.append(discovery_rule.snmp_walk_item)

        self.mib_modules = self._get_mib_modules()
        self.description = self._preprocess_description()

    def _generate_template_name(self) -> str:
        return f"{self.manufacturer} {self.device} {self.model}"

    def _get_mib_modules(self) -> List[str]:
        """
        Get the list of MIB modules used in the template.

        Returns:
            List[str]: List of MIB module names.
        """
        mib_modules = set()
        for entry in self.snmp_items or self.snmp_traps or []:
            if mib_module := entry.mib_module:
                mib_modules.add(mib_module)

        return list(mib_modules) or ["N/A"]

    def _preprocess_description(self) -> str:
        return f"Template {self.name}\nMIB(s) used:" + "\n".join(
            f"- {mib}" for mib in self.mib_modules
        )

    def generate_yaml_dict(self) -> Dict[str, Any]:
        inner_yaml_structure = {
            "uuid": str(uuid.uuid4().hex),
            "template": self.name,
            "name": self.name,
            "description": self.description,
            "groups": [{"name": self.group}],
            "items": [],
        }

        template_tag_yaml = [tag.generate_yaml_dict() for tag in self.template_tags]
        if template_tag_yaml:
            inner_yaml_structure["tags"] = template_tag_yaml

        outer_yaml_structure = {
            "zabbix_export": {
                "version": "7.0",
                "template_groups": [
                    {"uuid": str(uuid.uuid4().hex), "name": self.group}
                ],
                "templates": [inner_yaml_structure],
            }
        }

        return outer_yaml_structure
