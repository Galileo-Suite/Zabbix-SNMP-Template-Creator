import pytest

from src.zabbix_objects.snmp_walk_item import SNMPWalkItem


@pytest.fixture
def sample_discovery_rule_table():
    return [
        {
            "MIB Module": "TEST-MIB",
            "OID": "1.3.6.1.4.1.2636.3.1.13.1",
            "Name": "jnxOperatingTable",
            "Description": "Test table description",
        },
        {
            "MIB Module": "TEST-MIB",
            "OID": "1.3.6.1.4.1.2636.3.1.13.1.5",
            "Name": "jnxOperatingTemp",
            "Description": "Test temperature description",
            "Type": "Integer32",
        },
        {
            "MIB Module": "TEST-MIB",
            "OID": "1.3.6.1.4.1.2636.3.1.13.1.6",
            "Name": "jnxOperatingCPU",
            "Description": "Test CPU description",
            "Type": "Integer32",
        },
    ]


@pytest.fixture
def sample_template_name():
    return "TestTemplate"


def test_snmp_walk_item_initialization(
    sample_discovery_rule_table, sample_template_name
):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)

    assert snmp_walk_item.mib_module == "TEST-MIB"
    assert snmp_walk_item.name == "jnx Operating Walk"
    assert snmp_walk_item.type == 4
    assert snmp_walk_item.delay == "1m"
    assert snmp_walk_item.history == "7d"
    assert snmp_walk_item.trends == "0"
    assert snmp_walk_item.value_type == 4


def test_parse_oids(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_oid_string = "1.3.6.1.4.1.2636.3.1.13.1.6"
    assert (
        snmp_walk_item._parse_oids(sample_discovery_rule_table) == expected_oid_string
    )


def test_generate_snmp_oid(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_snmp_oid = "walk[1.3.6.1.4.1.2636.3.1.13.1.6"
    assert snmp_walk_item.snmp_oid == expected_snmp_oid


def test_generate_name(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    assert snmp_walk_item.name == "jnx Operating Walk"


def test_generate_key(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_key = "testtemplate.jnx-operating.walk"
    assert snmp_walk_item.key == expected_key


def test_preprocess_description(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_description = """MIB = TEST-MIB
Test table description
jnxOperatingTable.* 1.3.6.1.4.1.2636.3.1.13.1
jnxOperatingTemp 1.3.6.1.4.1.2636.3.1.13.1.5
jnxOperatingCPU 1.3.6.1.4.1.2636.3.1.13.1.6"""
    assert snmp_walk_item.description == expected_description


def test_generate_yaml_dict(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    yaml_dict = snmp_walk_item.generate_yaml_dict()

    assert "uuid" in yaml_dict
    assert "description" in yaml_dict
    assert "history" in yaml_dict
    assert "delay" in yaml_dict
    assert "key" in yaml_dict
    assert "name" in yaml_dict
    assert "snmp_oid" in yaml_dict
    assert "trends" in yaml_dict
    assert "type" in yaml_dict
    assert "value_type" in yaml_dict
