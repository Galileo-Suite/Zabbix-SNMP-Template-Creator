# Zabbix SNMP Template Generator

This project is a Python-based tool designed to generate Zabbix templates for SNMP-enabled devices. It automates the process of creating Zabbix templates by extracting information from Excel files containing MIB (Management Information Base) data. It creates the SNMP Traps and SNMP Items specified in their respective sheets, as well as creating Discovery Rules and Item Prototypes from the MIB data. See sample_template_file.xlsx for details.

## Project Goal

The main objective of this script is to streamline the creation of Zabbix templates for SNMP monitoring. It takes MIB information stored in a structured Excel file and converts it into a Zabbix-compatible YAML template. This automation significantly reduces the time and effort required to set up SNMP monitoring for various devices in Zabbix.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.

The features currently on my radar as of 08/12/2024 include:
- [ ] Creating time based anomaly Triggers for numeric Items
- [ ] Creating time based anomaly Trigger Prototypes for numeric Items
- [ ] More robust Discovery Rule creation
- [ ] Creating sub-Discovery Rules when the oids over-flow the snmp_oid field

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- A configured Excel sheet to pull data from.

* The 'MIB Data' sheet from this was produced by exporting MIB data as a CSV from the free MIB Browser application, and then adding it to the sample document.

## Installation

1. Clone this repository to your local machine:

   ```
   git clone https://github.com/Galileo-Suite/Zabbix-SNMP-Template-Creator.git
   cd Zabbix-SNMP-Template-Creator
   ```

2. Install the required dependencies using the `requirements.txt` file:
   ```
   pip install -r requirements.txt
   ```

- If this doesn't work, try installing them individually:
  ```
  pip install {package-name}
  ```

## Usage

To run the program, use the following command:

```
python main.py <path_to_excel_file>
```

Replace `<path_to_excel_file>` with the path to your Excel file containing the MIB information.

For example:

```
python main.py ./sample_template_file.xlsx
```

## Input File Specifications

The input Excel file should contain the following sheets:

1. **Template Information**: Contains general information about the template.
2. **SNMP Traps**: Contains information about SNMP traps to be monitored.
3. **SNMP Items**: Contains information about SNMP items to be monitored.
4. **MIB Data**: Contains the MIB information for the device.

Each sheet should have the following columns:

- **SNMP Items** and **SNMP Traps**:

  - OID
  - Name

- **Template Information**:

  - Group
  - Macros
  - Manufacturer
  - Model
  - Tags
  - Device

- **MIB Data**:
  - MIB Module
  - OID
  - Name
  - Description
  - Type

Ensure that your Excel file follows this structure for the script to work correctly.

## Output

The script generates a YAML file containing the Zabbix template. The output file will be saved in the `./created_templates/` directory with a name format of:

```
YYYYMMDD_HHMMSS <Template Name> Template.yaml
```

## Troubleshooting

If you encounter any issues:

1. Ensure that your Excel file follows the required structure.
2. Check that all required columns are present in each sheet.
3. Verify that you have installed all dependencies from the `requirements.txt` file.
4. Make sure you're using a compatible version of Python (3.7+).

If problems persist, please open an issue in the GitHub repository with a detailed description of the error and the steps to reproduce it.

## License

[MIT License](LICENSE)
