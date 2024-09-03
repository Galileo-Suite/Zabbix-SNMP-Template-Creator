import pandas as pd
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class UnmatchedDataError(Exception):
    """Raised when there is unmatched data after validation."""
    pass

class MIBValidator:
    """
    A class for validating and extracting data from Excel files containing MIB information.
    """

    @classmethod
    def extract_from_excel(cls, excel_file: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
        """
        Extract and validate data from an Excel file.
        This is a factory method that separates the creation of the Template object from its source.
        Here we parse the necessary data from Excel. Later, we could do so from a json object, a database, etc.

        Args:
            excel_file (str): Path to the Excel file.

        Returns:
            Tuple containing:
            - List of preprocessed SNMP items
            - List of preprocessed SNMP traps
            - Template information dictionary
            - Dictionary of discovery rule tables
        """
        excel_data = pd.ExcelFile(excel_file)
        all_sheets_data = {}
        
        na_values = ['nan', 'NaN', 'N/A', '']
        
        for sheet_name in excel_data.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, na_values=na_values)
            df = df.where(pd.notnull(df), None)
            sheet_data = df.to_dict('records')
            all_sheets_data[sheet_name] = sheet_data
        
        snmp_items_json_list = all_sheets_data.get("SNMP Items", [])
        snmp_traps_json_list = all_sheets_data.get("SNMP Traps", [])
        template_info = all_sheets_data.get("Template Information", [])
        template_info_json = template_info[0] if template_info else {}
        
        mib_sheet_name = next((sheet for sheet in all_sheets_data.keys() if "MIB" in sheet), None)
        mib_data_json_list = all_sheets_data.get(mib_sheet_name, [])

        preprocessed_snmp_items = cls._preprocess_and_validate(snmp_items_json_list, mib_data_json_list, "SNMP Items")
        preprocessed_snmp_traps = cls._preprocess_and_validate(snmp_traps_json_list, mib_data_json_list, "SNMP Traps")
        discovery_rule_tables = cls._collect_discovery_rule_tables(mib_data_json_list)

        return preprocessed_snmp_items, preprocessed_snmp_traps, template_info_json, discovery_rule_tables

    @classmethod
    def _preprocess_and_validate(cls, input_data: List[Dict[str, Any]], mib_data: List[Dict[str, Any]], entity_type: str) -> List[Dict[str, Any]]:
        """
        Preprocess and validate input data against MIB data.

        Args:
            input_data (List[Dict[str, Any]]): List of input data dictionaries.
            mib_data (List[Dict[str, Any]]): List of MIB data dictionaries.
            entity_type (str): Type of entity being validated (e.g., "SNMP Items", "SNMP Traps").

        Returns:
            List[Dict[str, Any]]: List of validated and preprocessed data.

        Raises:
            UnmatchedDataError: If there are unmatched entries after validation.
        """
        oid_dict, name_dict, null_entries = cls._preprocess_input_data(input_data)
        mib_oid_dict, mib_name_dict = cls._create_mib_dictionaries(mib_data)
        matched_data, unmatched_data = cls._match_entries(input_data, mib_oid_dict, mib_name_dict)

        cls._print_results(matched_data, unmatched_data, null_entries, entity_type)

        if unmatched_data:
            raise UnmatchedDataError(f"Validation failed: {len(unmatched_data)} unmatched entries found for {entity_type}.\n\t{unmatched_data}\nCheck source document for invalid entries.")

        return matched_data

    @staticmethod
    def _preprocess_input_data(input_data):
        """
        Preprocess input data to handle duplicates and null entries.

        Args:
            input_data (List[Dict[str, Any]]): List of input data dictionaries.

        Returns:
            Tuple containing:
            - Dictionary of entries keyed by OID
            - Dictionary of entries keyed by Name
            - List of null entries
        """
        oid_count = defaultdict(list)
        name_count = defaultdict(list)
        oid_dict = {}
        name_dict = {}
        null_entries = []
        
        # First pass: count occurrences and store indices
        for index, entry in enumerate(input_data):
            oid, name = entry.get('OID'), entry.get('Name')
            if oid:
                oid_count[oid].append(index)
            if name:
                name_count[name].append(index)
        
        # Second pass: categorize entries and handle duplicates
        for index, entry in enumerate(input_data):
            oid, name = entry.get('OID'), entry.get('Name')
            
            if not oid and not name:
                null_entries.append(entry)
                continue

            entry_copy = entry.copy()

            if oid and len(oid_count[oid]) > 1:
                for dup_index in oid_count[oid]:
                    input_data[dup_index]['OID'] = None
                entry_copy['OID'] = None

            if name and len(name_count[name]) > 1:
                for dup_index in name_count[name]:
                    input_data[dup_index]['Name'] = None
                entry_copy['Name'] = None

            if entry_copy['OID']:
                oid_dict[oid] = entry_copy
            if entry_copy['Name']:
                name_dict[name] = entry_copy

        return oid_dict, name_dict, null_entries

    @staticmethod
    def _create_mib_dictionaries(mib_data: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Create dictionaries of MIB data keyed by OID and Name.

        Args:
            mib_data (List[Dict[str, Any]]): List of MIB data dictionaries.

        Returns:
            Tuple containing:
            - Dictionary of MIB entries keyed by OID
            - Dictionary of MIB entries keyed by Name
        """
        mib_oid_dict = {entry['OID']: entry for entry in mib_data if 'OID' in entry}
        mib_name_dict = {entry['Name']: entry for entry in mib_data if 'Name' in entry}
        return mib_oid_dict, mib_name_dict

    @staticmethod
    def _match_entries(input_data: List[Dict[str, Any]], mib_oid_dict: Dict[str, Dict[str, Any]], mib_name_dict: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Match input entries against MIB data.

        Args:
            input_data (List[Dict[str, Any]]): List of input data dictionaries.
            mib_oid_dict (Dict[str, Dict[str, Any]]): Dictionary of MIB entries keyed by OID.
            mib_name_dict (Dict[str, Dict[str, Any]]): Dictionary of MIB entries keyed by Name.

        Returns:
            Tuple containing:
            - List of matched entries
            - List of unmatched entries
        """
        matched_data = []
        unmatched_data = []

        for entry in input_data:
            oid, name = entry.get('OID'), entry.get('Name')
            
            if not oid and not name:
                unmatched_data.append(entry)
                continue

            matched = False

            if oid and oid in mib_oid_dict:
                matched_data.append(mib_oid_dict[oid])
                matched = True
            elif name and name in mib_name_dict:
                matched_data.append(mib_name_dict[name])
                matched = True

            if not matched:
                unmatched_data.append(entry)

        return matched_data, unmatched_data

    @staticmethod
    def _collect_discovery_rule_tables(mib_data_json_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect discovery rule tables from MIB data.

        Args:
            mib_data_json_list (List[Dict[str, Any]]): List of MIB data dictionaries.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary of discovery rule tables keyed by OID.
        """
        # Sort the list of dictionaries by OID
        mib_sorted_by_oid = sorted(mib_data_json_list, key=lambda x: x['OID'])
        
        discovery_rule_tables = {}
        current_rule = None
        
        for entry in mib_sorted_by_oid:
            if 'Table' in entry['Name'] and 'SEQUENCE OF' in entry['Type']:
                # We've found the beginning entry to create a Discovery Rule
                if current_rule:
                    # Save the previous rule if it exists
                    discovery_rule_tables[current_rule['OID']] = current_rule['entries']
                
                # Start a new rule
                current_rule = {'OID': entry['OID'], 'entries': [entry]}
            elif current_rule and entry['OID'].startswith(current_rule['OID']):
                current_rule['entries'].append(entry)
            else:
                if current_rule:
                    # Save the previous rule if it exists
                    discovery_rule_tables[current_rule['OID']] = current_rule['entries']
                    current_rule = None
        
        # Make sure we add the last rule if it exists
        if current_rule:
            discovery_rule_tables[current_rule['OID']] = current_rule['entries']
        
        print(f'[{len(discovery_rule_tables)}] Discovery Rules found.')
        return discovery_rule_tables

    @staticmethod
    def _print_results(matched_data: List[Dict[str, Any]], unmatched_data: List[Dict[str, Any]], null_entries: List[Dict[str, Any]], entity_type: str) -> None:
        """
        Print validation results.

        Args:
            matched_data (List[Dict[str, Any]]): List of matched entries.
            unmatched_data (List[Dict[str, Any]]): List of unmatched entries.
            null_entries (List[Dict[str, Any]]): List of null entries.
            entity_type (str): Type of entity being validated (e.g., "SNMP Items", "SNMP Traps").
        """
        print(f"[{len(matched_data)}] Validated {entity_type} entries")
        print(f"[{len(unmatched_data)}] Missing {entity_type} entries")
        print(f"[{len(null_entries)}] Null entries")

        if unmatched_data:
            print(f"The following {entity_type} entries were missing from the MIB file:")
            for entry in unmatched_data:
                print(f"  - {entry.get('Name', 'N/A')} (OID: {entry.get('OID', 'N/A')})")