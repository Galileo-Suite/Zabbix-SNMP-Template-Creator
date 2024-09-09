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
    assert snmp_item.type == 4
    assert snmp_item.delay == "1m"
    assert snmp_item.history == "7d"


def test_preprocess_name():
    assert SNMPItem._preprocess_name("jnxOperatingTemp") == "Operating Temp"
    assert SNMPItem._preprocess_name("testCamelCase") == "test Camel Case"
    assert SNMPItem._preprocess_name("TEST_SNAKE_CASE") == "TEST SNAKE CASE"


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
