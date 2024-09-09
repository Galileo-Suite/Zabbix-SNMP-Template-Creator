from types import SimpleNamespace

SNMP_ITEM = SimpleNamespace(HISTORY="90d", TRENDS="365d", DELAY="1h", TYPE="SNMP_AGENT")

SNMP_TRAP = SimpleNamespace(
    HISTORY="90d",
    DELAY="0m",
    TRENDS="0",
    TRIGGER=SimpleNamespace(PRIORITY="INFO", TYPE="MULTIPLE", CLOSE="YES"),
    TYPE="SNMP_TRAP",
    VALUE_TYPE="LOG",
)

SNMP_WALK_ITEM = SimpleNamespace(
    HISTORY="0d", TRENDS="0", DELAY="1m", TYPE="SNMP_AGENT", VALUE_TYPE="TEXT"
)

ITEM_PROTOTYPE = SimpleNamespace(
    HISTORY="90d", TRENDS="365d", DELAY="1h", TYPE="DEPENDENT", VALUE_TYPE="TEXT"
)

DISCOVERY_RULE = SimpleNamespace(TYPE="DEPENDENT")
