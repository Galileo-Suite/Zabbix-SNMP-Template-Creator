import os
import sys
import time
import yaml
from typing import Literal

from zabbix_objects.template import Template
from utils.mib_validator import MIBValidator

def create_all_yaml(template: Template, include_items: bool = True, include_traps: bool = True, include_discovery_rules: bool = True) -> Literal['YAMLStr']:
    """
    Create a YAML representation of the template and its components.

    Args:
        template (Template): The Template object to convert to YAML.
        include_items (bool): Whether to include SNMP items in the YAML.
        include_traps (bool): Whether to include SNMP traps in the YAML.
        include_discovery_rules (bool): Whether to include discovery rules in the YAML.

    Returns:
        str: A YAML string representation of the template and its components.
    """
    template_yaml = template.generate_yaml_dict()

    if include_items and template.snmp_items:
        snmp_item_yaml = [ snmp_item.generate_yaml_dict() for snmp_item in template.snmp_items]
        template_yaml['zabbix_export']['templates'][0]['items'].extend(snmp_item_yaml)
    
    if include_traps and template.snmp_traps:
        snmp_trap_yaml = [ snmp_trap.generate_yaml_dict() for snmp_trap in template.snmp_traps]
        template_yaml['zabbix_export']['templates'][0]['items'].extend(snmp_trap_yaml)
    
    if include_discovery_rules and template.discovery_rules:
        discovery_rule_yaml = [ discovery_rule.generate_yaml_dict() for discovery_rule in template.discovery_rules]
        if discovery_rule_yaml:
            template_yaml['zabbix_export']['templates'][0]['discovery_rules'] = discovery_rule_yaml

    return yaml.dump(template_yaml, default_flow_style=False, sort_keys=False)

def main() -> None:
    """
    Main function to process an Excel file and generate a Zabbix template YAML.

    This function:
    1. Validates the command-line arguments
    2. Extracts data from the provided Excel file
    3. Creates a Template object
    4. Generates a YAML representation of the template
    5. Writes the YAML to a file
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <excel_file_path>")
        sys.exit(1)

    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found.")
        sys.exit(1)

    print("Extracting data from Excel...")
    snmp_items_json_list, snmp_traps_json_list, template_info_json, discovery_rule_tables = MIBValidator.extract_from_excel(excel_file)

    print("Creating Template...")
    template = Template(template_info_json, snmp_items_json_list, snmp_traps_json_list, discovery_rule_tables)

    print("Creating YAML...")
    yaml_template = create_all_yaml(template)

    print("Writing YAML to file...")
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_dir = './created_templates'
    output_file = f'{output_dir}/{timestamp} {template.name} Template.yaml'

    # Check if the directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    with open(output_file, 'w') as f:
        f.write(yaml_template)

    print(f"YAML template saved as '{output_file}'")
    print("Process completed successfully!")

if __name__ == "__main__":
    main()