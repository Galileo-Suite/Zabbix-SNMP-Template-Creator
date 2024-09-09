import uuid

import pytest

from src.zabbix_objects.snmp_item import SNMPItem


@pytest.fixture
def sample_item_data():
    return {
        "MIB Module": "TEST-MIB",
        "OID": "1.3.6.1.4.1.2636.3.1.13.1.5",
        "Name": "jnxOperatingTemp",
        "Description": "The temperature of this subject in degrees Celsius.\nTest paragraph.",
        "Type": "Integer32",
    }


@pytest.fixture
def sample_template_name():
    return "TestTemplate"


def test_snmp_item_initialization(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)

    assert snmp_item.mib_module == "TEST-MIB"
    assert snmp_item.oid == "1.3.6.1.4.1.2636.3.1.13.1.5"
    assert snmp_item.name == "Operating Temp"
    assert snmp_item.type == "SNMP_AGENT"
    assert snmp_item.delay == "1h"
    assert snmp_item.history == "90d"


def test_preprocess_name():
    assert SNMPItem._preprocess_name("jnxOperatingTemp") == "Operating Temp"
    assert SNMPItem._preprocess_name("testCamelCase") == "Camel Case"


def test_preprocess_description(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    expected_description = "TEST-MIB::jnxOperatingTemp\nOID::1.3.6.1.4.1.2636.3.1.13.1.5\nThe temperature of this subject in degrees Celsius.\nTest paragraph."
    assert snmp_item.description == expected_description


def test_generate_key(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    expected_key = "testtemplate.operating-temp.get"
    assert snmp_item.key == expected_key


def test_generate_snmp_oid(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    expected_snmp_oid = "get[1.3.6.1.4.1.2636.3.1.13.1.5]"
    assert snmp_item.snmp_oid == expected_snmp_oid


def test_determine_value_type(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    assert snmp_item.value_type is None  # Because the type is Integer32

    sample_item_data["Type"] = "DISPLAYSTRING"
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    assert snmp_item.value_type == "CHAR"

    sample_item_data["Type"] = "Float"
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    assert snmp_item.value_type == "FLOAT"


def test_determine_trends(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    assert snmp_item.trends == "365d"  # Default for Integer32

    sample_item_data["Type"] = "DISPLAYSTRING"
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    assert snmp_item.trends == "0"


def test_generate_yaml_dict(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    yaml_dict = snmp_item.generate_yaml_dict()

    assert "description" in yaml_dict
    assert "history" in yaml_dict
    assert "delay" in yaml_dict
    assert "key" in yaml_dict
    assert "name" in yaml_dict
    assert "snmp_oid" in yaml_dict
    assert "trends" in yaml_dict
    assert "type" in yaml_dict
    assert "uuid" in yaml_dict
    assert "value_type" not in yaml_dict  # Should be removed as it's None for Integer32


def test_generate_snmp_items():
    items_data = [
        {
            "MIB Module": "TEST-MIB1",
            "OID": "1.1",
            "Name": "testA",
            "Description": "Desc1",
            "Type": "Integer32",
        },
        {
            "MIB Module": "TEST-MIB2",
            "OID": "1.2",
            "Name": "testB",
            "Description": "Desc2",
            "Type": "DISPLAYSTRING",
        },
    ]
    template_name = "TestTemplate"
    items = SNMPItem.generate_snmp_items(items_data, template_name)
    assert len(items) == 2
    assert all(isinstance(item, SNMPItem) for item in items)
    assert items[0].name == "A"
    assert items[1].name == "B"


def test_long_key_warning(sample_item_data, capfd):
    long_template_name = "A" * 250
    snmp_item = SNMPItem(sample_item_data, long_template_name)
    captured = capfd.readouterr()
    assert "Warning: Key" in captured.out
    assert len(snmp_item.key) == 255


def test_determine_value_type_edge_cases(sample_item_data, sample_template_name):
    sample_item_data["Type"] = "OCTET STRING"
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    assert snmp_item.value_type == "CHAR"

    sample_item_data["Type"] = "Unknown"
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    assert snmp_item.value_type == "TEXT"


def test_generate_yaml_dict_comprehensive(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    yaml_dict = snmp_item.generate_yaml_dict()

    assert yaml_dict["description"] == snmp_item.description
    assert yaml_dict["history"] == snmp_item.history
    assert yaml_dict["delay"] == snmp_item.delay
    assert yaml_dict["key"] == snmp_item.key
    assert yaml_dict["name"] == snmp_item.name
    assert yaml_dict["snmp_oid"] == snmp_item.oid
    assert yaml_dict["trends"] == snmp_item.trends
    assert yaml_dict["type"] == snmp_item.type
    assert "uuid" in yaml_dict
    assert "value_type" not in yaml_dict  # For Integer32 type

    # Test with a value_type that should be included
    sample_item_data["Type"] = "DISPLAYSTRING"
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    yaml_dict = snmp_item.generate_yaml_dict()
    assert yaml_dict["value_type"] == "CHAR"


# Additional test to ensure UUID is being generated correctly
def test_uuid_generation(sample_item_data, sample_template_name):
    snmp_item = SNMPItem(sample_item_data, sample_template_name)
    yaml_dict = snmp_item.generate_yaml_dict()
    assert "uuid" in yaml_dict
    assert len(yaml_dict["uuid"]) == 32  # UUID should be 32 characters long
    assert uuid.UUID(yaml_dict["uuid"], version=4)  # Ensure it's a valid UUID4


# Test for empty or None values in item_data
def test_empty_item_data():
    empty_item_data = {
        "MIB Module": "",
        "OID": None,
        "Name": "",
        "Description": None,
        "Type": "",
    }
    template_name = "EmptyTemplate"
    snmp_item = SNMPItem(empty_item_data, template_name)

    assert snmp_item.mib_module == ""
    assert snmp_item.oid is None
    assert snmp_item.name == ""
    assert "No description available." in snmp_item.description
    assert snmp_item.value_type == "TEXT"  # Default for empty type


# Test for description preprocessing with various input formats
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
        item_data = {
            "MIB Module": "TEST-MIB",
            "OID": "testOID",
            "Name": "testName",
            "Type": "Integer32",
            **case["input"],
        }
        snmp_item = SNMPItem(item_data, sample_template_name)
        assert snmp_item.description == case["expected"]
