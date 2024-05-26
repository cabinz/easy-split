import pandas as pd
from pathlib import Path
import graph
from typing import List

"""Represent the loader to load records as a lending graph from the data file as required.
"""


def split_names(s_names: str, splitter: str = ",") -> List[str]:
    names = [name.strip() for name in s_names.split(splitter)]
    return names


class Loader:
    def __init__(
        self,
        data_file: str,
        col_lender: str,
        col_debtor: str,
        col_pp_amount: str,
        separator: str = ",",
    ) -> None:
        data_file = Path(data_file)
        assert data_file.exists(), f"The given path {data_file} does NOT exist"
        assert data_file.is_file(), f"The given path {data_file} is NOT a path"
        assert data_file.suffix == ".csv", f"Unsupported format {data_file.suffix}"

        self._data_file = data_file
        self._col_lender = col_lender
        self._col_debtor = col_debtor
        self._col_pp = col_pp_amount
        self._separator = separator

        self._df = pd.read_csv(self._data_file)

        self._members = set()
        for index, row in self._df.iterrows():
            if row[self._col_lender].lower() != "all":
                self._members.update(
                    split_names(row[self._col_lender], self._separator)
                )
            if row[self._col_debtor].lower() != "all":
                self._members.update(
                    split_names(row[self._col_debtor], self._separator)
                )

        self._g = graph.LendingGraph()
        for index, row in self._df.iterrows():
            lender = row[self._col_lender]
            if row[self._col_debtor].lower() == "all":
                debtors = self._members.copy()
                debtors.remove(lender)
            else:
                debtors = split_names(row[self._col_debtor])

            for debtor in debtors:
                # print(f"Go: L={lender}, D={debtor}, A={row[COL_PP]}")
                self._g.add_edge(lender, debtor, row[self._col_pp])

    def get_graph(self):
        return self._g

    def get_data(self):
        return self._df

    def get_members(self):
        return self._members


if __name__ == "__main__":
    file_path = "data/test_cyc.csv"

    loader = Loader(
        file_path,
        col_lender="Payer",
        col_debtor="Pay for",
        col_pp_amount="Amount (pp.)",
    )
    print(f"Members: {loader.get_members()}")

    g = loader.get_graph()
    g.vis()

    df = loader.get_data()
    print(df)
