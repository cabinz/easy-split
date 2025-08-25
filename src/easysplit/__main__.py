"""CLI entry of the package."""

from .config import *
from .loader import Loader, DataFormat
from .exr import ExchangeRates
from .formatter import format_transaction_table
from .validator import DataValidator, ValidationResult
from . import graph

import argparse
import pandas as pd
from pathlib import Path
import sys

SPLIT_LN = "=" * 20


def main():
    parser = argparse.ArgumentParser(
        'SplitBill',
        description="Process some integers."
    )

    parser.add_argument(
        "--file",
        help="Path to the data file.", required=True
    )
    parser.add_argument(
        "--col_creditor",
        default=DEFAULT_COL_CREDITOR,
        help=f'Column name for creditors in the sheet. Default as "{DEFAULT_COL_CREDITOR}".',
    )
    parser.add_argument(
        "--col_debtor",
        default=DEFAULT_COL_DEBTOR,
        help=f'Column name for debtors in the sheet. Default as "{DEFAULT_COL_DEBTOR}".',
    )
    parser.add_argument(
        "--col_tot_amount",
        default=DEFAULT_COL_TOT_AMOUNT,
        help=f"Column name for total lending amount (from the creditor) in the sheet. Default as '{DEFAULT_COL_TOT_AMOUNT}'",
    )
    parser.add_argument(
        "--col_currency",
        default=DEFAULT_COL_CURRENCY,
        help=f"Column name for transation currency. Default as '{DEFAULT_COL_CURRENCY}'",
    )

    parser.add_argument(
        "--separator", 
        default=DEFAULT_SEP, 
        help=f"Separator for splitting names in a cell. Default as comma '{DEFAULT_SEP}'."
    )
    parser.add_argument(
        "--all_selector", 
        default=DEFAULT_ALL_SELECTOR, 
        help=f"String specifying all members memtioned in the data. Default as '{DEFAULT_ALL_SELECTOR}'."
    )
    
    parser.add_argument(
        "--standard_currency",
        type=str,
        help='The currency for settlement (ie., to be displayed in results). eg., "HKD".',
    )
    parser.add_argument(
        "--exchange_rate",
        type=str,
        action="append",
        help="Exchange rate. BASE/QUOTE=x means 1 BASE is converted to x QUOTE. eg., USD/HKD=7.8",
    )
    
    parser.add_argument(
        "--result_dump_path",
        type=str,
        help='File path to dump the output sheet. eg. "path/to/out.csv".',
    )
    parser.add_argument(
        "--details_dump_path",
        type=str,
        help='File path to dump the detailed preprocessed record sheet. eg. "path/to/details.csv".',
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the input data without processing.",
    )

    args = parser.parse_args()
    
    ########################################
    # Load data file for validation
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)
    
    # Determine file type and load
    SUPPORT_FTYPES = {
        ".csv": lambda x: pd.read_csv(x),
        ".tsv": lambda x: pd.read_csv(x, sep="\t"),
        ".xlsx": lambda x: pd.read_excel(x),
    }
    
    file_type = file_path.suffix
    if file_type not in SUPPORT_FTYPES:
        print(f"Error: Unsupported file format {file_type}. Supported formats: {', '.join(SUPPORT_FTYPES.keys())}")
        sys.exit(1)
    
    df = SUPPORT_FTYPES[file_type](file_path)
    
    # Setup exchange rates
    exrs = None
    if args.standard_currency:
        print(f"Standard currency for results: {args.standard_currency}")
        exrs = ExchangeRates(args.standard_currency)
        if args.exchange_rate:
            for s in args.exchange_rate: # s = 'BASE/QUOTE=x'
                base_quote, rate = s.split("=")
                base, quote = base_quote.split("/")
                exrs.add_rate(base, quote, float(rate))
                print(f"Registered exchange rate {base}/{quote} = {rate}")
    
    # Create DataFormat with auto-detection
    data_format = DataFormat.from_args_with_auto_detect(args, df)
    
    # Validate data
    validator = DataValidator(df, data_format, exrs)
    validation_result = validator.validate()
    
    if validation_result.has_errors() or validation_result.has_warnings():
        validation_result.print_summary()
        if validation_result.has_errors():
            print("\nData validation failed. Please fix the errors above.")
            sys.exit(1)
    else:
        print("✓ Data validation passed.")
    
    # If validate-only flag is set, exit after validation
    if args.validate_only:
        sys.exit(0)
    
    print("")  # Empty line for separation
    
    # Continue with normal processing
    loader = Loader(
        args.file,
        data_format,
        exrs
    )

    print(f"Members:", ", ".join(loader.get_members()))
    print(SPLIT_LN)

    g = loader.get_graph()
    creditors, debtors = [], []
    for name, net_out in g.net_out_flow.items():
        if net_out > 0:
            creditors.append((name, net_out))
        else:
            debtors.append((name, -net_out))

    print("Creditors:")
    for name, amount in creditors:
        print(
            "\t{}: {}{:.2f}".format(
                name,
                args.standard_currency if args.standard_currency is not None
                     else "",
                amount,
            )
        )
    print("Debtors")
    for name, amount in debtors:
        print(
            "\t{}: {}{:.2f}".format(
                name,
                args.standard_currency if args.standard_currency is not None 
                    else "",
                amount,
            )
        )
    print(SPLIT_LN)

    equiv = graph.simplest_equiv(g)
    coln_amount = (f"Amount ({args.standard_currency})" if args.standard_currency is not None 
                    else "Amount")
    dumped_df = equiv.dump(col_amount=coln_amount)

    # Display transaction count in the title
    transaction_count = len(dumped_df)
    print(f"Simplest bill splitting scheme: (with {transaction_count} transaction{'s' if transaction_count != 1 else ''})")
    
    # Format and display the table
    if not dumped_df.empty:
        formatted_table = format_transaction_table(dumped_df, args.standard_currency)
        print(formatted_table)
    else:
        print("No transactions needed - everyone is settled!")

    if args.result_dump_path is not None:
        dumped_df.to_csv(args.result_dump_path)
        print(f"Results are dumped to {args.result_dump_path}")
    if args.details_dump_path is not None:
        loader.get_preprocessed_data().to_csv(args.details_dump_path)
        print(f"Proprocessing details are dumped to {args.details_dump_path}")