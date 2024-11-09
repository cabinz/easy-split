from test_common import TEST_CSV_FP, TEST_XLSX_FP, TEST_NOSUFFIX_FP

from easysplit import Loader, DataFormat

ldr1 = Loader(TEST_CSV_FP)
print("Successfully loaded CSV file.")

ldr2 = Loader(TEST_XLSX_FP)
print("Successfully loaded XLSX file.")

try:
    ldr3 = Loader(TEST_NOSUFFIX_FP)
except ValueError as e:
    if "no suffix" in str(e).lower():
        print("Successfully capture input file with no suffix.")
    else:
        raise e
