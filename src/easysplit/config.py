"""Default configuration values for data format of records and the framework."""

# Column name aliases for auto-detection (in priority order)
CREDITOR_ALIASES = ["Creditor", "Payer"]
DEBTOR_ALIASES = ["Debtor", "Payee"]
AMOUNT_ALIASES = ["Amount", "Total"]
CURRENCY_ALIASES = ["Currency", "Curr"]

# All selector aliases (for indicating all members)
ALL_SELECTOR_ALIASES = ["all", "*", "ALL", "All"]

# Default column names (used when auto-detection fails)
DEFAULT_COL_CREDITOR = "Creditor"
DEFAULT_COL_DEBTOR = "Debtor"
DEFAULT_COL_TOT_AMOUNT = "Amount"
DEFAULT_COL_CURRENCY = "Currency"
DEFAULT_SEP = ","
DEFAULT_ALL_SELECTOR = "all"
