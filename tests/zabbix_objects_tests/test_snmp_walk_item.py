import textwrap
import uuid

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
    assert snmp_walk_item.name == "Operating Walk"
    assert snmp_walk_item.type == "SNMP_AGENT"
    assert snmp_walk_item.delay == "1m"
    assert snmp_walk_item.history == "0d"
    assert snmp_walk_item.trends == "0"
    assert snmp_walk_item.value_type == "TEXT"


def test_parse_oids(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_oid_string = "1.3.6.1.4.1.2636.3.1.13.1.6"
    assert (
        snmp_walk_item._parse_oids(sample_discovery_rule_table) == expected_oid_string
    )


def test_generate_snmp_oid(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_snmp_oid = "walk[1.3.6.1.4.1.2636.3.1.13.1.6"
    print(snmp_walk_item.snmp_oid, expected_snmp_oid)
    assert snmp_walk_item.snmp_oid == expected_snmp_oid


def test_generate_name(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    assert snmp_walk_item.name == "Operating Walk"


def test_generate_key(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_key = "testtemplate.operating.walk"
    assert snmp_walk_item.key == expected_key


def test_preprocess_description(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    expected_description = textwrap.dedent(
        """
    MIB = TEST-MIB
    Test table description
    jnxOperatingTable.* 1.3.6.1.4.1.2636.3.1.13.1
    jnxOperatingCPU 1.3.6.1.4.1.2636.3.1.13.1.6"""
    ).strip()
    print(snmp_walk_item.description, expected_description)
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


# New tests based on patterns from test_snmp_item.py and test_snmp_trap.py


def test_long_key_warning(sample_discovery_rule_table, capfd):
    long_template_name = "A" * 250
    SNMPWalkItem(sample_discovery_rule_table, long_template_name)
    captured = capfd.readouterr()
    assert "Warning: Walk Key" in captured.out
    assert len(SNMPWalkItem(sample_discovery_rule_table, long_template_name).key) == 255


def test_uuid_generation(sample_discovery_rule_table, sample_template_name):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    yaml_dict = snmp_walk_item.generate_yaml_dict()
    assert "uuid" in yaml_dict
    assert len(yaml_dict["uuid"]) == 32  # UUID should be 32 characters long
    assert uuid.UUID(yaml_dict["uuid"], version=4)  # Ensure it's a valid UUID4


def test_generate_yaml_dict_comprehensive(
    sample_discovery_rule_table, sample_template_name
):
    snmp_walk_item = SNMPWalkItem(sample_discovery_rule_table, sample_template_name)
    yaml_dict = snmp_walk_item.generate_yaml_dict()

    assert yaml_dict["description"] == snmp_walk_item.description
    assert yaml_dict["history"] == snmp_walk_item.history
    assert yaml_dict["delay"] == snmp_walk_item.delay
    assert yaml_dict["key"] == snmp_walk_item.key
    assert yaml_dict["name"] == snmp_walk_item.name
    assert yaml_dict["snmp_oid"] == snmp_walk_item.snmp_oid
    assert yaml_dict["trends"] == snmp_walk_item.trends
    assert yaml_dict["type"] == snmp_walk_item.type
    assert yaml_dict["value_type"] == snmp_walk_item.value_type
    assert "uuid" in yaml_dict


def test_generate_snmp_walk_items():
    tables_data = [
        [
            {
                "MIB Module": "TEST-MIB1",
                "OID": "1.1",
                "Name": "testTableA",
                "Description": "Desc1",
            },
            {
                "MIB Module": "TEST-MIB1",
                "OID": "1.1.1",
                "Name": "testColumnA1",
                "Description": "Desc1.1",
                "Type": "Integer32",
            },
        ],
        [
            {
                "MIB Module": "TEST-MIB2",
                "OID": "1.2",
                "Name": "testTableB",
                "Description": "Desc2",
            },
            {
                "MIB Module": "TEST-MIB2",
                "OID": "1.2.1",
                "Name": "testColumnB1",
                "Description": "Desc2.1",
                "Type": "OCTET STRING",
            },
        ],
    ]
    template_name = "TestTemplate"
    walk_items = SNMPWalkItem.generate_snmp_walk_items(tables_data, template_name)
    assert len(walk_items) == 2
    assert all(isinstance(item, SNMPWalkItem) for item in walk_items)
    assert walk_items[0].name == "Walk A"
    assert walk_items[1].name == "Walk B"
