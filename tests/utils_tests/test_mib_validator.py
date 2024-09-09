from unittest.mock import patch

import pandas as pd
import pytest

from src.utils.mib_validator import MIBValidator, UnmatchedDataError


@pytest.fixture
def sample_excel_data():
    return {
        "SNMP Items": pd.DataFrame(
            {"OID": [".1.2.3", ".1.2.4", ".1.2.5"], "Name": ["Item1", "Item2", "Item3"]}
        ),
        "SNMP Traps": pd.DataFrame(
            {"OID": [".1.3.1", ".1.3.2"], "Name": ["Trap1", "Trap2"]}
        ),
        "Template Information": pd.DataFrame(
            {
                "Group": ["Template/Networking"],
                "Manufacturer": ["CISCO"],
                "Device": ["Catalyst"],
                "Model": ["9300"],
                "Macros": [""],
                "Tags": [""],
            }
        ),
        "MIB Data": pd.DataFrame(
            {
                "OID": [".1.2.3", ".1.2.4", ".1.2.5", ".1.3.1", ".1.3.2"],
                "Name": ["Item1", "Item2", "Item3", "Trap1", "Trap2"],
                "Type": [
                    "INTEGER",
                    "STRING",
                    "INTEGER",
                    "NOTIFICATION-TYPE",
                    "NOTIFICATION-TYPE",
                ],
            }
        ),
    }


@pytest.fixture
def mock_excel_file(sample_excel_data):
    with patch("pandas.ExcelFile") as mock_excel:
        mock_excel.return_value.sheet_names = list(sample_excel_data.keys())
        mock_excel.return_value.parse.side_effect = (
            lambda sheet_name: sample_excel_data[sheet_name]
        )
        yield mock_excel


def test_extract_from_excel(mock_excel_file, sample_excel_data):
    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.side_effect = (
            lambda file, sheet_name, **kwargs: sample_excel_data[sheet_name]
        )
        result = MIBValidator.extract_from_excel("dummy.xlsx")

    assert len(result) == 4
    snmp_items, snmp_traps, template_info, discovery_rules = result

    assert len(snmp_items) == 3
    assert len(snmp_traps) == 2
    assert template_info == {
        "Group": "Template/Networking",
        "Manufacturer": "CISCO",
        "Device": "Catalyst",
        "Model": "9300",
        "Macros": "",
        "Tags": "",
    }
    assert len(discovery_rules) == 0  # No discovery rules in this sample data

    # Verify that ExcelFile was called with the correct filename
    mock_excel_file.assert_called_once_with("dummy.xlsx")

    # Verify that read_excel was called for each sheet
    assert mock_read_excel.call_count == len(sample_excel_data)


def test_preprocess_and_validate_success():
    input_data = [
        {"OID": ".1.2.3", "Name": "Item1"},
        {"OID": ".1.2.4", "Name": "Item2"},
    ]
    mib_data = [
        {"OID": ".1.2.3", "Name": "Item1", "Type": "INTEGER"},
        {"OID": ".1.2.4", "Name": "Item2", "Type": "STRING"},
    ]

    result = MIBValidator._preprocess_and_validate(input_data, mib_data, "SNMP Items")
    assert len(result) == 2
    assert all(item in result for item in mib_data)


def test_preprocess_and_validate_unmatched_data():
    input_data = [
        {"OID": ".1.2.3", "Name": "Item1"},
        {"OID": ".1.2.5", "Name": "Item3"},
    ]
    mib_data = [{"OID": ".1.2.3", "Name": "Item1", "Type": "INTEGER"}]

    with pytest.raises(UnmatchedDataError):
        MIBValidator._preprocess_and_validate(input_data, mib_data, "SNMP Items")


def test_preprocess_input_data():
    input_data = [
        {"OID": ".1.2.3", "Name": "Item1"},
        {"OID": ".1.2.3", "Name": "Item2"},  # Duplicate OID
        {"OID": ".1.2.4", "Name": "Item2"},  # Duplicate Name
        {"OID": None, "Name": None},  # Null entry
    ]

    oid_dict, name_dict, null_entries = MIBValidator._preprocess_input_data(input_data)

    assert len(oid_dict) == 1
    assert len(name_dict) == 1
    assert len(null_entries) == 1


def test_create_mib_dictionaries():
    mib_data = [
        {"OID": ".1.2.3", "Name": "Item1", "Type": "INTEGER"},
        {"OID": ".1.2.4", "Name": "Item2", "Type": "STRING"},
    ]

    mib_oid_dict, mib_name_dict = MIBValidator._create_mib_dictionaries(mib_data)

    assert len(mib_oid_dict) == 2
    assert len(mib_name_dict) == 2
    assert ".1.2.3" in mib_oid_dict
    assert "Item1" in mib_name_dict


def test_match_entries():
    input_data = [
        {"OID": ".1.2.3", "Name": "Item1"},
        {"OID": ".1.2.5", "Name": "Item3"},
    ]
    mib_oid_dict = {".1.2.3": {"OID": ".1.2.3", "Name": "Item1", "Type": "INTEGER"}}
    mib_name_dict = {"Item1": {"OID": ".1.2.3", "Name": "Item1", "Type": "INTEGER"}}

    matched, unmatched = MIBValidator._match_entries(
        input_data, mib_oid_dict, mib_name_dict
    )

    assert len(matched) == 1
    assert len(unmatched) == 1


def test_collect_discovery_rule_tables():
    mib_data = [
        {"OID": ".1.2.3", "Name": "Table1", "Type": "SEQUENCE OF"},
        {"OID": ".1.2.3.1", "Name": "Entry1", "Type": "INTEGER"},
        {"OID": ".1.2.3.2", "Name": "Entry2", "Type": "STRING"},
        {"OID": ".1.2.4", "Name": "OtherItem", "Type": "INTEGER"},
    ]

    discovery_rules = MIBValidator._collect_discovery_rule_tables(mib_data)

    assert len(discovery_rules) == 1
    assert ".1.2.3" in discovery_rules
    assert len(discovery_rules[".1.2.3"]) == 3


@pytest.mark.parametrize(
    "matched,unmatched,null,expected_output",
    [
        (
            [{"OID": ".1.2.3", "Name": "Item1"}],
            [],
            [],
            "[1] Validated SNMP Items entries\n[0] Missing SNMP Items entries\n[0] Null entries\n",
        ),
        (
            [{"OID": ".1.2.3", "Name": "Item1"}],
            [{"OID": ".1.2.4", "Name": "Item2"}],
            [{"OID": None, "Name": None}],
            "[1] Validated SNMP Items entries\n[1] Missing SNMP Items entries\n[1] Null entries\n"
            "The following SNMP Items entries were missing from the MIB file:\n"
            "  - Item2 (OID: .1.2.4)\n",
        ),
    ],
)
def test_print_results(capsys, matched, unmatched, null, expected_output):
    MIBValidator._print_results(matched, unmatched, null, "SNMP Items")
    captured = capsys.readouterr()
    assert captured.out == expected_output
