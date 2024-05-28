from loader import Loader
import graph

COL_LENDER = "Payer"
COL_DEBTOR = "Pay for"
COL_PP = "Amount (pp.)"
SEP = ","
COL_AMOUNT = "Amount (KWR)"
COL_AMOUNT_HKD = "Amount (HKD)"
KRW2HKD = 0.0057715

data_file = "data/Total-Details.csv"
dumped_file = "out/Korea24_net.csv"

ldr = Loader(
    data_file,
    col_lender=COL_LENDER,
    col_debtor=COL_DEBTOR,
    col_pp_amount=COL_PP,
    separator=SEP,
)

print(f"Members:", ", ".join(ldr.get_members()))

g = ldr.get_graph()
lenders, debtors = [], []
for name, net_out in g.net_out_flow.items():
    if net_out > 0:
        lenders.append((name, net_out))
    else:
        debtors.append((name, -net_out))
print("Lenders:")
for name, amount in lenders:
    print(f"  {name}: {amount:.2f}")
print("Debtors")
for name, amount in debtors:
    print(f"  {name}: {amount:.2f}")

equiv = graph.simplest_equiv(g)
dumped_df = equiv.dump(col_amount=COL_AMOUNT)
dumped_df[COL_AMOUNT_HKD] = round(dumped_df[COL_AMOUNT] * KRW2HKD, 2)

print("EQUIV:")
print(dumped_df)

# dumped_df.to_csv(dumped_file)
