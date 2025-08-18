"""Represent the loader to load records as a lending graph from the data file as required.
"""

from . import graph
from .exr import ExchangeRates
from .config import *

from typing import List, Optional
import pandas as pd
from pathlib import Path


class DataFormat:
    def __init__(self,
                 col_creditor=DEFAULT_COL_CREDITOR,
                 col_debtor=DEFAULT_COL_DEBTOR,
                 col_tot_amount=DEFAULT_COL_TOT_AMOUNT,
                 col_currency=DEFAULT_COL_CURRENCY,
                 separator=DEFAULT_SEP,  # separator for multiple names
                 all_selector=DEFAULT_ALL_SELECTOR,
                 ) -> None:
        self.col_creditor = col_creditor
        self.col_debtor = col_debtor
        self.col_tot_amount = col_tot_amount
        self.col_currency = col_currency
        self.separator = separator
        self.all_selector = all_selector

    @classmethod
    def from_args(cls, args):
        return cls(
            args.col_creditor,
            args.col_debtor,
            args.col_tot_amount,
            args.col_currency,
            args.separator,
            args.all_selector,
        )
    
    @staticmethod
    def auto_detect_column(df_columns: List[str], aliases: List[str]) -> Optional[str]:
        """Auto-detect column name from DataFrame columns using aliases.
        
        Args:
            df_columns: List of column names from DataFrame
            aliases: List of possible aliases for this column type
        
        Returns:
            The actual column name from df_columns if found, None otherwise.
            Returns the original case from df_columns.
        """
        # Create a mapping from lowercase to original column names
        column_map = {col.lower(): col for col in df_columns}
        
        # Check each alias (case-insensitive)
        for alias in aliases:
            if alias.lower() in column_map:
                return column_map[alias.lower()]
        
        return None
    
    @classmethod
    def from_args_with_auto_detect(cls, args, df: pd.DataFrame):
        """Create DataFormat with auto-detection support.
        
        Args:
            args: Command line arguments
            df: DataFrame to detect columns from
        
        Returns:
            DataFormat instance with detected or specified column names
        """
        # Creditor column: user specified > auto-detect > default
        col_creditor = args.col_creditor
        if col_creditor == DEFAULT_COL_CREDITOR:  # User didn't specify
            detected = cls.auto_detect_column(df.columns.tolist(), CREDITOR_ALIASES)
            if detected:
                print(f"✓ Auto-detected creditor column: '{detected}'")
                col_creditor = detected
            else:
                # Keep the default, will fail later if column doesn't exist
                col_creditor = DEFAULT_COL_CREDITOR
        
        # Debtor column: user specified > auto-detect > default
        col_debtor = args.col_debtor
        if col_debtor == DEFAULT_COL_DEBTOR:  # User didn't specify
            detected = cls.auto_detect_column(df.columns.tolist(), DEBTOR_ALIASES)
            if detected:
                print(f"✓ Auto-detected debtor column: '{detected}'")
                col_debtor = detected
            else:
                col_debtor = DEFAULT_COL_DEBTOR
        
        # Amount column: user specified > auto-detect > default
        col_tot_amount = args.col_tot_amount
        if col_tot_amount == DEFAULT_COL_TOT_AMOUNT:  # User didn't specify
            detected = cls.auto_detect_column(df.columns.tolist(), AMOUNT_ALIASES)
            if detected:
                print(f"✓ Auto-detected amount column: '{detected}'")
                col_tot_amount = detected
            else:
                col_tot_amount = DEFAULT_COL_TOT_AMOUNT
        
        # Currency column: user specified > auto-detect > default
        col_currency = args.col_currency
        if col_currency == DEFAULT_COL_CURRENCY:  # User didn't specify
            detected = cls.auto_detect_column(df.columns.tolist(), CURRENCY_ALIASES)
            if detected:
                print(f"✓ Auto-detected currency column: '{detected}'")
                col_currency = detected
            else:
                col_currency = DEFAULT_COL_CURRENCY
        
        return cls(
            col_creditor=col_creditor,
            col_debtor=col_debtor,
            col_tot_amount=col_tot_amount,
            col_currency=col_currency,
            separator=args.separator,
            all_selector=args.all_selector,
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
        exrs: ExchangeRates = None,
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
        
        
        self._metacoln_std_tot_amount = f"Total Amount"
        if exrs is not None:
            self._metacoln_std_tot_amount += f" ({exrs.std_currency})"
            self._exrs = exrs
            self._df[self._metacoln_std_tot_amount] = self._df.apply(
                lambda row: exrs.to_std(row[cfg.col_currency], row[cfg.col_tot_amount]),
                axis=1,
            )
        else:
            print("No exchange rates provided. Run in the currency-agnostic way.")
            self._df[self._metacoln_std_tot_amount] = self._df[cfg.col_tot_amount]
        
        def _split_names(s_names: str, splitter: str = DEFAULT_SEP) -> List[str]:
            names = [name.strip() for name in s_names.split(splitter)]
            return names
        
        # Helper function to check if a value is an "all" selector
        def is_all_selector(value: str) -> bool:
            return value.lower().strip() in [sel.lower() for sel in ALL_SELECTOR_ALIASES]
        
        # Collect all members
        self._members = set()
        for index, row in self._df.iterrows():
            if not is_all_selector(row[self._cfg.col_creditor]):
                creditor = _split_names(row[self._cfg.col_creditor], cfg.separator)
                if len(creditor) > 1: # Currently only support single creditor
                    raise ValueError("Currently only support single creditor. "
                                     "Please specify only one creditor in each record.")
                self._members.update(creditor)
            if not is_all_selector(row[self._cfg.col_debtor]):
                self._members.update(
                    _split_names(row[self._cfg.col_debtor], self._cfg.separator)
                )

        # Create lending graph
        self._g = graph.LendingGraph()
        for index, row in self._df.iterrows():
            creditor = row[self._cfg.col_creditor].strip()
            if is_all_selector(row[self._cfg.col_debtor]):
                debtors = self._members.copy()
            else:
                debtors = _split_names(row[self._cfg.col_debtor])
            
            pp_amount = row[self._metacoln_std_tot_amount] / len(debtors)
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
    
    def get_preprocessed_data(self):
        return self._df
