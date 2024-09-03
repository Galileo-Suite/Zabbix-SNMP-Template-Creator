import pytest
from unittest.mock import patch, MagicMock

from src.zabbix_objects.item_prototype import ItemPrototype

from src.zabbix_objects.discovery_rule import DiscoveryRule

@pytest.fixture
def sample_discovery_rule_table():
    return [
        {
            "MIB Module": "TEST-MIB",
            "OID": "1.3.6.1.4.1.2636.3.1.13.1",
            "Name": "jnxOperatingTable",
            "Description": "Test table description"
        },
        {
            "MIB Module": "TEST-MIB",
            "OID": "1.3.6.1.4.1.2636.3.1.13.1.5",
            "Name": "jnxOperatingTemp",
            "Description": "Test temperature description",
            "Type": "Integer32"
        }
    ]

@pytest.fixture
def sample_template_name():
    return "TestTemplate"

def test_discovery_rule_initialization(sample_discovery_rule_table, sample_template_name):
    with patch('src.zabbix_objects.snmp_walk_item.SNMPWalkItem') as mock_snmp_walk_item:
        mock_snmp_walk_item.return_value.key = 'test.walk'
        mock_snmp_walk_item.return_value.name = 'Test Walk'
        
        discovery_rule = DiscoveryRule(sample_discovery_rule_table, sample_template_name)
        
        assert discovery_rule.type == 10
        assert discovery_rule.master_item == 'test.walk'
        assert isinstance(discovery_rule.item_prototypes, list)
        assert discovery_rule.key == 'test.discovery'
        assert discovery_rule.name == 'Test Discovery'

def test_generate_discovery_rules(sample_discovery_rule_table, sample_template_name):
    discovery_rule_table = {"table1": sample_discovery_rule_table}
    
    with patch('src.zabbix_objects.discovery_rule.DiscoveryRule') as mock_discovery_rule:
        DiscoveryRule.generate_discovery_rules(discovery_rule_table, sample_template_name)
        mock_discovery_rule.assert_called_once_with(sample_discovery_rule_table, sample_template_name)

def test_generate_yaml_dict(sample_discovery_rule_table, sample_template_name):
    with patch('src.zabbix_objects.snmp_walk_item.SNMPWalkItem') as mock_snmp_walk_item:
        mock_snmp_walk_item.return_value.key = 'test.walk'
        mock_snmp_walk_item.return_value.name = 'Test Walk'
        mock_snmp_walk_item.return_value.description = 'Test description'
        
        discovery_rule = DiscoveryRule(sample_discovery_rule_table, sample_template_name)
        yaml_dict = discovery_rule.generate_yaml_dict()
        
        assert 'description' in yaml_dict
        assert 'key' in yaml_dict
        assert 'master_item' in yaml_dict
        assert 'name' in yaml_dict
        assert 'type' in yaml_dict
        assert 'uuid' in yaml_dict
        assert 'item_prototypes' in yaml_dict

def test_generate_item_prototypes(sample_discovery_rule_table, sample_template_name):
    with patch('src.zabbix_objects.snmp_walk_item.SNMPWalkItem') as mock_snmp_walk_item:
        mock_snmp_walk_item.return_value.key = 'test.walk'
        
        discovery_rule = DiscoveryRule(sample_discovery_rule_table, sample_template_name)
        
        assert len(discovery_rule.item_prototypes) == 1
        assert isinstance(discovery_rule.item_prototypes[0], ItemPrototype)
