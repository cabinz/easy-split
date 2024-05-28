from loader import Loader
import graph
import argparse

SPLIT_LN = "=" * 20

parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument("--file", help="Path to the data file.", required=True)
parser.add_argument(
    "--col_creditor",
    default="Creditor",
    help='Column name for creditors in the sheet. Default as "Creditor".',
)
parser.add_argument(
    "--col_debtor",
    default="Debtor",
    help='Column name for debtors in the sheet. Default as "Debtor".',
)
parser.add_argument(
    "--col_pp_amount",
    default="Amount (pp.)",
    help="Column name for per-person lending amount in the sheet.",
)

parser.add_argument(
    "--sep", default=",", help="Separator for input data. Default as comma (CSV file)"
)
parser.add_argument(
    "--primary_currency",
    type=str,
    help='The currency name for computation. eg. "HK$".',
)
parser.add_argument(
    "--secondary_currency",
    type=str,
    help='The currency name to be converted to by the given exchange rate. eg. "KRW".',
)
parser.add_argument(
    "--exchange_rate",
    type=float,
    help="Conversion rate from primary to secondary currency. eg. 5.7715e-3",
)
parser.add_argument(
    "--dump_path",
    type=str,
    help='File path to dump the output sheet. eg. "path/to/out.csv".',
)

args = parser.parse_args()
col_amount = (
    "Amount"
    if not hasattr(args, "primary_currency")
    else f"Amount ({args.primary_currency})"
)
col_2nd_amount = (
    None
    if not hasattr(args, "secondary_currency")
    else f"Amount ({args.secondary_currency})"
)


loader = Loader(
    args.file,
    col_creditor=args.col_creditor,
    col_debtor=args.col_debtor,
    col_pp_amount=args.col_pp_amount,
    separator=args.sep,
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
        "\t{}: {}{:.2f}{}".format(
            name,
            args.primary_currency if hasattr(args, "primary_currency") else "",
            amount,
            (
                f" ({args.secondary_currency}{amount * args.exchange_rate:.2f})"
                if hasattr(args, "secondary_currency")
                else ""
            ),
        )
    )
print("Debtors")
for name, amount in debtors:
    print(
        "\t{}: {}{:.2f}{}".format(
            name,
            args.primary_currency if hasattr(args, "primary_currency") else "",
            amount,
            (
                f" ({args.secondary_currency}{amount * args.exchange_rate:.2f})"
                if hasattr(args, "secondary_currency")
                else ""
            ),
        )
    )
print(SPLIT_LN)

equiv = graph.simplest_equiv(g)
dumped_df = equiv.dump(col_amount=col_amount)
if col_2nd_amount:
    dumped_df[col_2nd_amount] = round(dumped_df[col_amount] * args.exchange_rate, 2)

print("Simplest bill splitting scheme:")
print(dumped_df)

if hasattr(args, "dump_path"):
    dumped_df.to_csv(args.dump_path)
    print(SPLIT_LN)
    print(f"Results are dumped to {args.dump_path}")
