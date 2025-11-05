"""Default configuration values for data format of records and the framework."""

DEFAULT_SEP = ","

# Column name aliases for auto-detection (in priority order)
CREDITOR_ALIASES = [
    "Creditor", "Payer", "From", "Paid By",
    "付款人",
]
DEFAULT_COL_CREDITOR = CREDITOR_ALIASES[0]

DEBTOR_ALIASES = [
    "Debtor", "Payee", "To", "Split With",
    "参与人",
]
DEFAULT_COL_DEBTOR = DEBTOR_ALIASES[0]

AMOUNT_ALIASES = [
    "Amount", "Total", "Value", "Cost",
    "金额", "总额",
]
DEFAULT_COL_TOT_AMOUNT = AMOUNT_ALIASES[0]

CURRENCY_ALIASES = [
    "Currency", "Curr", "CCY",
    "货币", "币种",
]
DEFAULT_COL_CURRENCY = CURRENCY_ALIASES[0]

# All selector aliases (for indicating all members)
ALL_SELECTOR_ALIASES = [
    "all", "*", "ALL", "All",
    "所有", "所有人",
]
DEFAULT_ALL_SELECTOR = ALL_SELECTOR_ALIASES[0]
