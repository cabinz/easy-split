"""Represent the loader to load records as a lending graph from the data file as required.
"""

from . import graph
from .config import *

from typing import List
import pandas as pd
from pathlib import Path


class DataFormat:
    def __init__(self,
                 col_creditor=DEFAULT_COL_CREDITOR,
                 col_debtor=DEFAULT_COL_DEBTOR,
                 col_tot_amount=DEFAULT_COL_TOT_AMOUNT,
                 separator=DEFAULT_SEP,  # separator for multiple names
                 all_selector=DEFAULT_ALL_SELECTOR,
                 ) -> None:
        self.col_creditor = col_creditor
        self.col_debtor = col_debtor
        self.col_tot_amount = col_tot_amount
        self.separator = separator
        self.all_selector = all_selector

    @classmethod
    def from_args(cls, args):
        return cls(
            args.col_creditor,
            args.col_debtor,
            args.col_tot_amount,
            args.separator,
            args.all_selector,
        )



SUPPORT_FTYPES = {
    ".csv": lambda x: pd.read_csv(x),
    ".tsv": lambda x: pd.read_csv(x, sep="\t"),
    ".xlsx": lambda x: pd.read_excel(x),
}


class Loader:
    def __init__(
        self,
        file_path: str,
        cfg: DataFormat = DataFormat(),
    ) -> None:
        file_path = Path(file_path)
        assert file_path.exists(), f"The given path {file_path} does NOT exist"
        assert file_path.is_file(), f"The given path {file_path} is NOT a path"

        file_type = 'No Suffix' if file_path.suffix == '' else file_path.suffix
        if file_type not in SUPPORT_FTYPES:
            raise ValueError("Unsupported format: {}. Only support files in format: {}. " 
                             "Please specify correct file path with supported format suffix.".format(
                file_type,
                ', '.join(SUPPORT_FTYPES.keys()),
            ))

        self._file_path = file_path
        self._df = SUPPORT_FTYPES[self._file_path.suffix](self._file_path)
        self._cfg = cfg
        
        def _split_names(s_names: str, splitter: str = DEFAULT_SEP) -> List[str]:
            names = [name.strip() for name in s_names.split(splitter)]
            return names
        
        # Collect all members
        self._members = set()
        for index, row in self._df.iterrows():
            if row[self._cfg.col_creditor].lower().strip() != self._cfg.all_selector:
                creditor = _split_names(row[self._cfg.col_creditor], cfg.separator)
                if len(creditor) > 1: # Currently only support single creditor
                    raise ValueError("Currently only support single creditor. "
                                     "Please specify only one creditor in each record.")
                self._members.update(creditor)
            if row[self._cfg.col_debtor].lower().strip() != self._cfg.all_selector:
                self._members.update(
                    _split_names(row[self._cfg.col_debtor], self._cfg.separator)
                )

        # Create lending graph
        self._g = graph.LendingGraph()
        for index, row in self._df.iterrows():
            creditor = row[self._cfg.col_creditor].strip()
            if row[self._cfg.col_debtor].lower().strip() == self._cfg.all_selector:
                debtors = self._members.copy()
            else:
                debtors = _split_names(row[self._cfg.col_debtor])
            
            pp_amount = row[self._cfg.col_tot_amount] / len(debtors)
            if creditor in debtors:  # TODO: unnecessary, self-loop and be eliminated in the graph
                debtors.remove(creditor)
            for debtor in debtors:
                self._g.add_edge(creditor, debtor, pp_amount)

    def get_graph(self):
        return self._g

    def get_data(self):
        return self._df

    def get_members(self):
        return self._members
