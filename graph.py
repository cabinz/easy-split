import pandas as pd
from typing import List
from collections import defaultdict
import math

from utils.logger import get_logger


logger = get_logger(__name__)


class LendingGraph:
    """A direct weighted graph, where weights are the lending flows."""

    def __init__(self, log=logger) -> None:
        self._adj_lt = defaultdict(lambda: defaultdict(float))
        self.net_out_flow = defaultdict(float)
        self.log = logger

    def vis(self) -> None:
        for lender in self._adj_lt.keys():
            for debtor, amount in self._adj_lt[lender].items():
                print(f"{lender} --{amount:.2f}--> {debtor}")

    def get_nodes(self) -> List[str]:
        lt = set(self._adj_lt.keys())
        for lender in self._adj_lt.keys():
            lt.update(list(self._adj_lt[lender].keys()))
        return list(set(lt))

    def add_edge(self, lender, debtor, amount) -> None:
        assert (
            lender != debtor
        ), f"Lender and debtor ({lender}) should not be the same one!"
        self._adj_lt[lender][debtor] += amount
        self.net_out_flow[lender] += amount
        self.net_out_flow[debtor] -= amount
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
        self.net_out_flow[lender] -= amount
        self.net_out_flow[debtor] += amount
        return amount

    def get_childs(self, node) -> List[str]:
        return list(self._adj_lt[node].keys()) if node in self._adj_lt else []

    def _get_ring(self, curr_node, adj_lt, path):  # DFS
        if curr_node in path:
            self.log.debug(f"DFS is now at {path}, end here.")
            return path if curr_node == path[0] else None

        path.append(curr_node)
        self.log.debug(f"DFS is now at {path}")
        childs = self.get_childs(curr_node)
        test_s = [f"{c}({self.get_edge(curr_node, c)})" for c in childs]
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
            self.log.debug(f"  new_min_weight: L[{lender}]-D[{debtor}] W[{min_weight}]")
        for i in range(len(ring)):
            lender, debtor = ring[i], ring[(i + 1) % len(ring)]
            self.add_edge(lender, debtor, -min_weight)
            self.log.debug(
                f"    add_edge: L[{lender}]-D[{debtor}] dA[{-min_weight}] A[{self.get_flow(lender, debtor)}]"
            )

    def break_rings(self):
        # Note that this may result in different new graph depending on the order of rings found.
        for node in self.get_nodes():
            self.log.debug(f"break rings start from: {node}")
            while True:
                ring = self._get_ring(node, self._adj_lt, path=[])
                if ring is None:
                    break
                self._break_ring(ring)

    def dump(
        self,
        col_lender: str = "Lender",
        col_debtor: str = "Debtor",
        col_amount: str = "Amount",
    ) -> pd.DataFrame:
        # Create an empty DataFrame
        data_types = {
            col_lender: "object",  # 'object' is typically used for strings
            col_debtor: "object",
            col_amount: "float64",  # 'float64' for floating point numbers
        }
        df = pd.DataFrame(columns=data_types.keys()).astype(data_types)

        for lender in self._adj_lt:
            for debtor in self._adj_lt[lender]:
                amount = self.get_flow(lender, debtor)
                new_row = pd.DataFrame([[lender, debtor, amount]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)

        return df


def simplest_equiv(g: LendingGraph) -> LendingGraph:
    equiv_g = LendingGraph()

    def _reduce_match(out_flow, in_flow):
        # TODO: This is a low-efficient impl with two nested-loops incurring O(2N^2)
        um_out, um_in = [], []
        for lender, out_f in out_flow:
            matched = False
            for i, (debtor, in_f) in enumerate(in_flow):
                if math.isclose(out_f, in_f):
                    equiv_g.add_edge(lender, debtor, out_f)
                    del in_flow[i]
                    matched = True
                    break
            if not matched:
                um_out.append([lender, out_f])

        for debtor, in_f in in_flow:
            matched = False
            for i, (lender, out_f) in enumerate(out_flow):
                if math.isclose(out_f, in_f):
                    equiv_g.add_edge(lender, debtor, out_f)
                    del out_flow[i]
                    matched = True
                    break
            if not matched:
                um_in.append([debtor, in_f])

        return um_out, um_in

    unmatched_out, unmatched_in = [], []
    for node in g.get_nodes():
        net_out = g.net_out_flow[node]
        if net_out > 0:
            unmatched_out.append([node, net_out])
        elif net_out < 0:
            unmatched_in.append([node, -net_out])

    unmatched_out, unmatched_in = _reduce_match(unmatched_out, unmatched_in)

    while unmatched_in and unmatched_out:
        max_out = max(unmatched_out, key=lambda x: x[1])
        max_in = max(unmatched_in, key=lambda x: x[1])
        flow = min(max_out[1], max_in[1])
        equiv_g.add_edge(lender=max_out[0], debtor=max_in[0], amount=flow)
        if max_out[1] <= max_in[1]:
            max_in[1] -= flow
            unmatched_out.remove(max_out)
        else:
            max_out[1] -= flow
            unmatched_in.remove(max_in)
        unmatched_out, unmatched_in = _reduce_match(unmatched_out, unmatched_in)

    assert (
        len(unmatched_in) == 0 and len(unmatched_out) == 0
    ), f"in remained = {unmatched_in}, out remained = {unmatched_out}"

    return equiv_g


if __name__ == "__main__":
    pass
