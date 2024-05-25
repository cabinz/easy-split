import pandas as pd
from typing import List
from collections import defaultdict
import math

COL_LENDER = "Payer"
COL_DEBTOR = "Pay for"
COL_PP = "Amount (pp.)"
COL_AMOUNT = "Amount (KWR)"
COL_AMOUNT_HKD = "Amount (HKD)"
KRW2HKD = 0.0057715
MEMBERS = {"Cathy", "Cabin", "Vivian", "Alan"}


class LendingGraph:
    """A direct weighted graph, where weights are the lending flows."""

    def __init__(self) -> None:
        self._adj_lt = defaultdict(lambda: defaultdict(float))

    def vis(self) -> None:
        for lender in self._adj_lt.keys():
            for debtor, amount in self._adj_lt[lender].items():
                print(f"{lender} --{amount}--> {debtor}")

    def get_nodes(self) -> List[str]:
        lt = list(self._adj_lt.keys())
        for lender in self._adj_lt.keys():
            lt.extend(list(self._adj_lt[lender].keys()))
        return list(set(lt))

    def add_edge(self, lender, debtor, amount) -> None:
        assert (
            lender != debtor
        ), f"Lender and debtor ({lender}) should not be the same one!"
        self._adj_lt[lender][debtor] += amount
        if math.isclose(self._adj_lt[lender][debtor], 0.0):
            self.remove_edge(lender, debtor)

    def has_edge(self, lender, debtor) -> bool:
        return lender in self._adj_lt and debtor in self._adj_lt[lender]

    def get_edge(self, lender, debtor) -> float:
        assert self.has_edge(lender, debtor)
        return self._adj_lt[lender][debtor]

    def get_flow(self, lender, debtor) -> float:
        return self._adj_lt[lender][debtor] if self.has_edge(lender, debtor) else 0.0

    def remove_edge(self, lender, debtor) -> float:
        amount = self.get_edge(lender, debtor)
        self._adj_lt[lender].pop(debtor, None)
        return amount

    def get_childs(self, node) -> List[str]:
        return list(self._adj_lt[node].keys()) if node in self._adj_lt else []

    def _get_ring(self, curr_node, adj_lt, path):  # DFS
        if curr_node in path:
            # print(f"DFS is now at {path}, end here.")
            return path if curr_node == path[0] else None

        path.append(curr_node)
        # print(f"DFS is now at {path}")
        childs = self.get_childs(curr_node)
        test_s = [f"{c}({self.get_edge(curr_node, c)})" for c in childs]
        # print(f"chlids from {curr_node}: {test_s}")
        for nxt in childs:
            ring = self._get_ring(nxt, adj_lt, path)
            if ring:
                return ring
        path.pop()
        return None

    def _break_ring(self, ring):
        min_weight = float("inf")
        for i in range(len(ring)):
            lender, debtor = ring[i], ring[(i + 1) % len(ring)]
            min_weight = min(min_weight, self.get_edge(lender, debtor))
            # print(f"new_min_weight: L[{lender}]-D[{debtor}] W[{min_weight}]")
        for i in range(len(ring)):
            lender, debtor = ring[i], ring[(i + 1) % len(ring)]
            self.add_edge(lender, debtor, -min_weight)
            # print(f"add_edge: L[{lender}]-D[{debtor}] A[{-min_weight}]")

    def break_rings(self):
        for node in self.get_nodes():
            # print(f"break rings start from: {node}")
            while True:
                ring = self._get_ring(node, self._adj_lt, path=[])
                # print(f"_get_ring: {ring}")
                if ring is None:
                    break
                # print("B4 break ring:")
                self.vis()
                self._break_ring(ring)
                # print("Aft break ring:")
                self.vis()
                # break

    def dump(self) -> pd.DataFrame:
        data_types = {
            COL_LENDER: "object",  # 'object' is typically used for strings
            COL_DEBTOR: "object",
            COL_AMOUNT: "float64",  # 'float64' for floating point numbers
            COL_AMOUNT_HKD: "float64",
        }

        # Create an empty DataFrame
        df = pd.DataFrame(columns=data_types.keys()).astype(data_types)

        nodes = self.get_nodes()

        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                i2j = self.get_flow(nodes[i], nodes[j])
                j2i = self.get_flow(nodes[j], nodes[i])
                lender = nodes[i] if i2j > j2i else nodes[j]
                debtor = nodes[j] if i2j > j2i else nodes[i]
                amount = math.fabs(i2j - j2i)
                if not math.isclose(amount, 0.0):
                    amount_hkd = amount * KRW2HKD
                    new_row = pd.DataFrame(
                        [[lender, debtor, amount, amount_hkd]], columns=df.columns
                    )
                    df = pd.concat([df, new_row], ignore_index=True)
        return df


def split_names(s_names: str, splitter: str = ",") -> List[str]:
    names = [name.strip() for name in s_names.split(splitter)]
    return names


if __name__ == "__main__":
    file_path = "data/test_cyc.csv"
    df = pd.read_csv(file_path)
    g = LendingGraph()

    for index, row in df.iterrows():
        lender = row[COL_LENDER]
        if row[COL_DEBTOR].lower() == "all":
            debtors = MEMBERS.copy()
            debtors.remove(lender)
        else:
            debtors = split_names(row[COL_DEBTOR])

        for debtor in debtors:
            # print(f"Go: L={lender}, D={debtor}, A={row[COL_PP]}")
            g.add_edge(lender, debtor, row[COL_PP])

    g.break_rings()
    d = g.dump()
    print(d)

    # to_file = 'out/Korea24_net.csv'
    # d.to_csv(to_file)
