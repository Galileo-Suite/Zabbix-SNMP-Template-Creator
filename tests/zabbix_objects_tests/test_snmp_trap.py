import uuid

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
    assert snmp_trap.name == "Test"
    assert snmp_trap.type == "SNMP_TRAP"
    assert snmp_trap.delay == "0m"
    assert snmp_trap.history == "90d"
    assert snmp_trap.trends == "0"
    assert snmp_trap.value_type == "LOG"


def test_preprocess_name():
    assert SNMPTrap._preprocess_name("jnxTestTrap") == "Test"
    assert SNMPTrap._preprocess_name("testCamelCaseTrap") == "Camel Case"


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
    assert default_trigger["manual_close"] == "YES"
    assert default_trigger["name"] == snmp_trap.name
    assert default_trigger["priority"] == "INFO"
    assert default_trigger["tags"] == [{"tag": "snmp_trap", "value": ""}]
    assert default_trigger["type"] == "MULTIPLE"
    assert "uuid" in default_trigger


def test_generate_yaml_dict(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    yaml_dict = snmp_trap.generate_yaml_dict()

    assert yaml_dict["delay"] == snmp_trap.delay
    assert yaml_dict["description"] == snmp_trap.description
    assert yaml_dict["history"] == snmp_trap.history
    assert yaml_dict["key"] == snmp_trap.key
    assert yaml_dict["name"] == snmp_trap.name
    assert yaml_dict["trends"] == snmp_trap.trends
    assert "triggers" in yaml_dict
    assert yaml_dict["type"] == snmp_trap.type
    assert "uuid" in yaml_dict
    assert yaml_dict["value_type"] == snmp_trap.value_type


def test_generate_snmp_traps():
    traps_data = [
        {
            "MIB Module": "TEST-MIB1",
            "OID": "1.1",
            "Name": "testTriggerA",
            "Description": "Desc1",
            "Type": "NOTIFICATION-TYPE",
        },
        {
            "MIB Module": "TEST-MIB2",
            "OID": "1.2",
            "Name": "testTriggerB",
            "Description": "Desc2",
            "Type": "NOTIFICATION-TYPE",
        },
    ]
    template_name = "TestTemplate"
    traps = SNMPTrap.generate_snmp_traps(traps_data, template_name)
    assert len(traps) == 2
    assert all(isinstance(trap, SNMPTrap) for trap in traps)
    assert traps[0].name == "Trigger A"
    assert traps[1].name == "Trigger B"


def test_long_key_warning(sample_trap_data, capfd):
    long_oid = "1." + ".".join(["1" * 10] * 25)  # This will create a very long OID
    sample_trap_data["OID"] = long_oid
    SNMPTrap(sample_trap_data, "TestTemplate")
    captured = capfd.readouterr()
    assert "Warning: Key" in captured.out
    assert len(SNMPTrap(sample_trap_data, "TestTemplate").key) == 255


def test_empty_trap_data():
    empty_trap_data = {
        "MIB Module": "",
        "OID": None,
        "Name": "",
        "Description": None,
        "Type": "",
    }
    template_name = "EmptyTemplate"
    snmp_trap = SNMPTrap(empty_trap_data, template_name)

    assert snmp_trap.mib_module == ""
    assert snmp_trap.oid is None
    assert snmp_trap.name == ""
    assert "No description available." in snmp_trap.description
    assert snmp_trap.type == "SNMP_TRAP"


def test_preprocess_description_formats(sample_template_name):
    test_cases = [
        {
            "input": {"Description": "Line1\n  Line2  \nLine3"},
            "expected": "TEST-MIB::testName\nOID::testOID\nLine1\nLine2\nLine3",
        },
        {
            "input": {"Description": "Text with 'single quotes'"},
            "expected": 'TEST-MIB::testName\nOID::testOID\nText with "single quotes"',
        },
        {
            "input": {"Description": None},
            "expected": "TEST-MIB::testName\nOID::testOID\nNo description available.",
        },
    ]

    for case in test_cases:
        trap_data = {
            "MIB Module": "TEST-MIB",
            "OID": "testOID",
            "Name": "testName",
            "Type": "NOTIFICATION-TYPE",
            **case["input"],
        }
        snmp_trap = SNMPTrap(trap_data, sample_template_name)
        assert snmp_trap.description == case["expected"]


def test_uuid_generation(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    yaml_dict = snmp_trap.generate_yaml_dict()
    assert "uuid" in yaml_dict
    assert len(yaml_dict["uuid"]) == 32  # UUID should be 32 characters long
    assert uuid.UUID(yaml_dict["uuid"], version=4)  # Ensure it's a valid UUID4


def test_default_trigger_uuid(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    default_trigger = snmp_trap.default_trigger
    assert "uuid" in default_trigger
    assert len(default_trigger["uuid"]) == 32
    assert uuid.UUID(default_trigger["uuid"], version=4)


def test_generate_yaml_dict_triggers(sample_trap_data, sample_template_name):
    snmp_trap = SNMPTrap(sample_trap_data, sample_template_name)
    yaml_dict = snmp_trap.generate_yaml_dict()
    assert "triggers" in yaml_dict
    assert len(yaml_dict["triggers"]) == 1
    assert yaml_dict["triggers"][0] == snmp_trap.default_trigger
