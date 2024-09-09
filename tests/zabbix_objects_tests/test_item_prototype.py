import pytest

from src.zabbix_objects.item_prototype import ItemPrototype


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
def sample_master_item_key():
    return "test.walk"


def test_item_prototype_initialization(sample_item_data, sample_master_item_key):
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)

    assert item_prototype.master_item == sample_master_item_key
    assert item_prototype.mib_module == "TEST-MIB"
    assert item_prototype.oid == "1.3.6.1.4.1.2636.3.1.13.1.5"
    assert item_prototype.name == "Operating Temp"
    assert item_prototype.type == 18
    assert item_prototype.history == "7d"


def test_preprocess_name():
    assert ItemPrototype._preprocess_name("jnxOperatingTemp") == "Operating Temp"
    assert ItemPrototype._preprocess_name("testCamelCase") == "test Camel Case"
    assert ItemPrototype._preprocess_name("TEST_SNAKE_CASE") == "TEST SNAKE CASE"


def test_preprocess_description(sample_item_data, sample_master_item_key):
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    expected_description = "TEST-MIB::jnxOperatingTemp\nOID::1.3.6.1.4.1.2636.3.1.13.1.5\nThe temperature of this subject in degrees Celsius.\nTest paragraph."
    assert item_prototype.description == expected_description


def test_generate_key(sample_item_data, sample_master_item_key):
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    expected_key = "test.operatingtemp[{#SNMPINDEX}]"
    assert item_prototype.key == expected_key


def test_determine_value_type(sample_item_data, sample_master_item_key):
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    assert item_prototype.value_type is None  # Because the type is Integer32

    sample_item_data["Type"] = "DISPLAYSTRING"
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    assert item_prototype.value_type == "CHAR"

    sample_item_data["Type"] = "Float"
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    assert item_prototype.value_type == "FLOAT"


def test_determine_trends(sample_item_data, sample_master_item_key):
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    assert item_prototype.trends == "365d"  # Default for Integer32

    sample_item_data["Type"] = "DISPLAYSTRING"
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    assert item_prototype.trends == "0"


def test_generate_yaml_dict(sample_item_data, sample_master_item_key):
    item_prototype = ItemPrototype(sample_item_data, sample_master_item_key)
    yaml_dict = item_prototype.generate_yaml_dict()

    assert "description" in yaml_dict
    assert "history" in yaml_dict
    assert "key" in yaml_dict
    assert "master_item" in yaml_dict
    assert "name" in yaml_dict
    assert "trends" in yaml_dict
    assert "type" in yaml_dict
    assert "uuid" in yaml_dict
    assert "value_type" not in yaml_dict  # Should be removed as it's None for Integer32
