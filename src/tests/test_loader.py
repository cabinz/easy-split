from test_common import TEST_CSV_FP, TEST_XLSX_FP, TEST_NOSUFFIX_FP

from easysplit import Loader, DataFormat
from easysplit.exr import ExchangeRates

ldr1 = Loader(TEST_CSV_FP)
print("Successfully loaded CSV file.")

exrs2 = ExchangeRates("HKD")
exrs2.add_rate("KRW", "HKD", 0.0057715)
ldr2 = Loader(TEST_XLSX_FP, exrs=exrs2)
print("Successfully loaded XLSX file with exchange rates.")

try:
    ldr3 = Loader(TEST_NOSUFFIX_FP)
except ValueError as e:
    if "no suffix" in str(e).lower():
        print("Successfully capture input file with no suffix.")
    else:
        raise e
