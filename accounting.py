import pandas as pd
from pathlib import Path


if __name__ == '__main__':
    file_path = 'Seoul24.csv'
    
    df = pd.read_csv(file_path)
    
    print(df)