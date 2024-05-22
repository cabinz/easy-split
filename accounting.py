import pandas as pd
from pathlib import Path
from typing import List
from collections import defaultdict
import math

COL_LENDER = 'Payer'
COL_DEBTOR = 'Pay for'
COL_PP = 'Amount (pp.)'
COL_AMOUNT = 'Amount (KWR)'
COL_AMOUNT_HKD = 'Amount (HKD)'
KRW2HKD = 0.0057715
MEMBERS = {'Cathy', 'Cabin', 'Vivian', 'Alan'}


class LendingGraph:
    """A direct weighted graph, where weights are the lending flows.
    """
    def __init__(self) -> None:
        self._adj_lt = defaultdict(lambda: defaultdict(float))
        
    def add_edge(self, lender, debtor, amount) -> None:
        self._adj_lt[lender][debtor] += amount
        
    def add_edges(self, lender, debtors, pp_amount) -> None:
        for debtor in debtors:
            self.add_edge(lender, debtor, pp_amount)
            
    def get_edge(self, lender, debtor) -> float:
        if lender not in self._adj_lt or debtor not in self._adj_lt[lender]:
            return .0
        else:
            return self._adj_lt[lender][debtor]
    
    def dump(self) -> pd.DataFrame:
        data_types = {
            COL_LENDER: 'object',   # 'object' is typically used for strings
            COL_DEBTOR: 'object', 
            COL_AMOUNT: 'float64',  # 'float64' for floating point numbers
            COL_AMOUNT_HKD: 'float64',
        }

        # Create an empty DataFrame
        df = pd.DataFrame(columns=data_types.keys()).astype(data_types)
        
        visited_edges = set()
        
        def mark_as_vis(name1, name2):
            visited_edges.add(f'{name1}-{name2}')
            
        def has_visited(name1, name2):
            comb1, comb2 = f'{name1}-{name2}', f'{name2}-{name1}'
            if comb1 in visited_edges or comb2 in visited_edges:
                return True
            else:
                False
        
        for a in self._adj_lt.keys():
            for b in self._adj_lt[a].keys():
                if has_visited(a, b):
                    continue
                
                a2b = g.get_edge(a, b)
                b2a = g.get_edge(b, a)
                lender = a if a2b > b2a else b
                debtor = b if a2b > b2a else a
                amount = math.fabs(a2b - b2a)
                if not math.isclose(amount, .0):
                    amount_hkd = amount * KRW2HKD
                    new_row = pd.DataFrame([[lender, debtor, amount, amount_hkd]], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
                    
                mark_as_vis(a, b)
        return df


def split_names(s_names: str, splitter: str=',') -> List[str]:
    names = [name.strip() for name in s_names.split(splitter)]
    return names


if __name__ == '__main__':
    file_path = 'data/Seoul-24.csv'
    # file_path = 'data/test.csv'
    df = pd.read_csv(file_path)
    g = LendingGraph()
    
    for index, row in df.iterrows():
        lender = row[COL_LENDER] 
        if row[COL_DEBTOR].lower() == 'all':
            debtors = MEMBERS.copy()
            debtors.remove(lender)
        else:
            debtors = split_names(row[COL_DEBTOR]) 
        
        for debtor in debtors:
            # print(f"Go: L={lender}, D={debtor}, A={row[COL_PP]}")
            g.add_edge(lender, debtor, row[COL_PP])
      
    d = g.dump()
    print(d)
    
    to_file = 'out/Seoul24_flow.csv'
    d.to_csv(to_file)