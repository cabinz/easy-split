# Easy Trip Split
EasyTripSplit ("the Splitter") is a python script tool for splitting bill in a group trip.

During a trip, bills are often paid collectively by one person in the group and then split among all members (or some of the members) later on. These bills can accumulate and become difficult to manually track and calculate, especially the one paying (and being paid for) could be different every time. However, settling the bills immediately after each transaction can also be cumbersome.

The Splitter tool takes the payment records from the CSV file, and **generates the simplest scheme for paying off everyone's bills with the least number of transactions**. 

With the Splitter, anyone in the group can contribute to paying the bill, eliminating the need to split the bill immediately as long as the payment is accurately recorded in a sheet. This feature is particularly beneficial during group trips to locations with different local currencies, as any group member can assist in paying, and the repayment can be done in the home currency.

The payment history should be recorded in a CSV file, which can be easily created using tools like MS Excel or Apple Numbers on mobile devices.


## Dependencies
- `Python >= 3.10`
- `pandas` for reading CSV files

Install Pandas using the following command:
```
pip install pandas
```

## Usage

The recording sheet table could be like the [sample file](samples/sample_data.csv).
![](docs/sample_input.png)

Actually, the splitter only requires three columns in the red box, the rest of the content (such as date, item names) are only for the convenience of checking the records: 
- `Creditor` (person who paid the bill)
- `Debtor` (ppl. who owe money)
- `Amount (pp.)` (amount of money owed per person)

Run the Splitter with
```shell
cd easy-trip-split
python run.py --file "samples/sample_data.csv" --primary_currency "KR₩"   --secondary_currency "HK$"  --exchange_rate 0.0057715
```

The results provided by the Splitter:
```shell
Members: Cabin, Cathy, Alan, Vivian
====================
Creditors:
        Alan: KR₩185029.17 (HK$1067.90)
Debtors
        Cabin: KR₩720.84 (HK$4.16)
        Cathy: KR₩113037.50 (HK$652.40)
        Vivian: KR₩71270.83 (HK$411.34)
====================
Simplest bill splitting scheme:
  Creditor  Debtor  Amount (KR₩)  Amount (HK$)
0     Alan   Cabin        720.84          4.16
1     Alan   Cathy     113037.50        652.40
2     Alan  Vivian      71270.83        411.34
```

There are more parameters support customization in the commandline arguments:
```shell
options:
  -h, --help            show this help message and exit
  --file FILE           Path to the data file.
  --col_creditor COL_CREDITOR
                        Column name for creditors in the sheet. Default as "Creditor".
  --col_debtor COL_DEBTOR
                        Column name for debtors in the sheet. Default as "Debtor".
  --col_pp_amount COL_PP_AMOUNT
                        Column name for per-person lending amount in the sheet.
  --sep SEP             Separator for input data. Default as comma (CSV file)
  --primary_currency PRIMARY_CURRENCY
                        The currency name for computation. eg. "KR₩".
  --secondary_currency SECONDARY_CURRENCY
                        The currency name to be converted to by the given exchange rate. eg. "HK$".
  --exchange_rate EXCHANGE_RATE
                        Conversion rate from primary to secondary currency. eg. 5.7715e-3 since 1HKD is 0.0057715KRW
  --dump_path DUMP_PATH
                        File path to dump the output sheet. eg. "path/to/out.csv".
```
