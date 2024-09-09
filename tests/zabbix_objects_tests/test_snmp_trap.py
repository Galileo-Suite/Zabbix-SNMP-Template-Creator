import pytest

from src.zabbix_objects.snmp_trap import SNMPTrap


@pytest.fixture
def sample_trap_data():
    return {
        "MIB Module": "TEST-MIB",
        "OID": "1.3.6.1.4.1.2636.4.1.1",
        "Name": "jnxTestTrap",
        "Description": "This is a test trap.\nIt has multiple lines.",
        "Type": "NOTIFICATION-TYPE",
    }


@pytest.fixture
def sample_template_name():
    return "TestTemplate"


def test_snmp_trap_initialization(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)

    assert snmp_trap.mib_module == "TEST-MIB"
    assert snmp_trap.oid == "1.3.6.1.4.1.2636.4.1.1"
    assert snmp_trap.name == "jnx Test"
    assert snmp_trap.type == 17
    assert snmp_trap.delay == "0"
    assert snmp_trap.history == "1w"
    assert snmp_trap.trends == "0"
    assert snmp_trap.value_type == 4


def test_preprocess_name():
    assert SNMPTrap._preprocess_name("jnxTestTrap") == "jnx Test"
    assert SNMPTrap._preprocess_name("testCamelCaseTrap") == "test Camel Case"
    assert SNMPTrap._preprocess_name("TEST_SNAKE_CASE_TRAP") == "TEST SNAKE CASE"


def test_preprocess_description(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    expected_description = "TEST-MIB::jnxTestTrap\nOID::1.3.6.1.4.1.2636.4.1.1\nThis is a test trap.\nIt has multiple lines."
    assert snmp_trap.description == expected_description


def test_generate_key(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    expected_key = 'snmptrap["1.3.6.1.4.1.2636.4.1.1"]'
    assert snmp_trap.key == expected_key


def test_generate_default_trigger(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    default_trigger = snmp_trap.default_trigger

    assert default_trigger["description"] == snmp_trap.description
    assert (
        default_trigger["expression"]
        == f"length(last(/TestTemplate/{snmp_trap.key}))>0"
    )
    assert default_trigger["manual_close"] == 1
    assert default_trigger["name"] == snmp_trap.name
    assert default_trigger["priority"] == 2
    assert default_trigger["tags"] == [{"tag": "snmp_trap", "value": ""}]
    assert default_trigger["type"] == 0
    assert "uuid" in default_trigger


def test_generate_yaml_dict(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    yaml_dict = snmp_trap.generate_yaml_dict()

    assert "delay" in yaml_dict
    assert "description" in yaml_dict
    assert "history" in yaml_dict
    assert "key" in yaml_dict
    assert "name" in yaml_dict
    assert "trends" in yaml_dict
    assert "triggers" in yaml_dict
    assert "type" in yaml_dict
    assert "uuid" in yaml_dict
    assert "value_type" in yaml_dict
