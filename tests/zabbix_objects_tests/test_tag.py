import pytest

from src.zabbix_objects.tag import Tag


def test_tag_initialization():
    tag = Tag("Key", "Value")
    assert tag.key == "key"
    assert tag.value == "value"


def test_process_tag_key():
    assert Tag._process_tag_key("TEST KEY") == "test_key"
    assert Tag._process_tag_key("  spaced  ") == "spaced"


def test_process_tag_value():
    assert Tag._process_tag_value("TEST VALUE") == "test_value"
    assert Tag._process_tag_value("  spaced  ") == "spaced"


def test_parse_tag_string():
    tag_string = "{key1:value1, key2:value2}"
    result = Tag._parse_tag_string(tag_string)
    assert result == [["key1", "value1"], ["key2", "value2"]]


def test_generate_template_tags():
    raw_tags = "{custom:tag}"
    tags = Tag.generate_template_tags(raw_tags, "manufacturer1", "device1")
    assert len(tags) == 3
    assert any(t.key == "target" and t.value == "manufacturer1" for t in tags)
    assert any(t.key == "target" and t.value == "device1" for t in tags)
    assert any(t.key == "custom" and t.value == "tag" for t in tags)


def test_generate_template_tags_no_raw_tags():
    tags = Tag.generate_template_tags("", "manufacturer1", "device1")
    assert len(tags) == 2
    assert all(t.key == "target" for t in tags)
    assert any(t.value == "manufacturer1" for t in tags)
    assert any(t.value == "device1" for t in tags)


def test_generate_yaml_dict():
    tag = Tag("Key", "Value")
    yaml_dict = tag.generate_yaml_dict()
    assert yaml_dict == {"tag": "key", "value": "value"}


@pytest.mark.parametrize(
    "key,value,expected_key,expected_value",
    [
        ("Normal", "Value", "normal", "value"),
        ("UPPER CASE", "UPPER VALUE", "upper_case", "upper_value"),
        ("  spaced  ", "  spaced value  ", "spaced", "spaced_value"),
    ],
)
def test_tag_various_inputs(key, value, expected_key, expected_value):
    tag = Tag(key, value)
    assert tag.key == expected_key
    assert tag.value == expected_value
