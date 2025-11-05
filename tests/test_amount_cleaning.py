"""Test amount cleaning functionality for comma-formatted numbers."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from easysplit.loader import Loader, DataFormat


class TestAmountCleaning:
    """Test cases for cleaning amount values with comma thousand separators."""

    def test_amount_with_commas(self):
        """Test that amounts with commas are properly cleaned."""
        # Create test data with comma-formatted amounts
        # Note: Amounts with commas must be quoted in CSV format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Creditor,Debtor,Amount,Currency\n")
            f.write('Alice,Bob,"2,900.00",USD\n')
            f.write('Bob,Charlie,"1,500.50",USD\n')
            temp_path = f.name

        try:
            loader = Loader(temp_path)
            df = loader.get_data()

            # Check that amounts are numeric (not strings)
            assert pd.api.types.is_numeric_dtype(df['Amount'])

            # Check the actual values
            assert df.loc[0, 'Amount'] == 2900.00
            assert df.loc[1, 'Amount'] == 1500.50
        finally:
            os.unlink(temp_path)

    def test_mixed_format_amounts(self):
        """Test handling of mixed formats (some with commas, some without)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Creditor,Debtor,Amount,Currency\n")
            f.write('Alice,Bob,"2,900.00",USD\n')  # With comma
            f.write("Bob,Charlie,1500.50,USD\n")  # Without comma
            f.write('Charlie,Alice,"10,000",USD\n')  # With comma, integer
            f.write("Alice,Charlie,999.99,USD\n")  # Without comma
            temp_path = f.name

        try:
            loader = Loader(temp_path)
            df = loader.get_data()

            # Check all amounts are numeric
            assert pd.api.types.is_numeric_dtype(df['Amount'])

            # Check values
            assert df.loc[0, 'Amount'] == 2900.00
            assert df.loc[1, 'Amount'] == 1500.50
            assert df.loc[2, 'Amount'] == 10000
            assert df.loc[3, 'Amount'] == 999.99
        finally:
            os.unlink(temp_path)

    def test_large_numbers_with_commas(self):
        """Test large numbers with multiple comma separators."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Creditor,Debtor,Amount,Currency\n")
            f.write('Alice,Bob,"1,234,567.89",USD\n')
            f.write('Bob,Charlie,"999,999.99",USD\n')
            temp_path = f.name

        try:
            loader = Loader(temp_path)
            df = loader.get_data()

            # Check all amounts are numeric
            assert pd.api.types.is_numeric_dtype(df['Amount'])

            # Check values
            assert df.loc[0, 'Amount'] == 1234567.89
            assert df.loc[1, 'Amount'] == 999999.99
        finally:
            os.unlink(temp_path)

    def test_backward_compatibility_no_commas(self):
        """Test that amounts without commas still work (backward compatibility)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Creditor,Debtor,Amount,Currency\n")
            f.write("Alice,Bob,2900.00,USD\n")
            f.write("Bob,Charlie,1500.50,USD\n")
            temp_path = f.name

        try:
            loader = Loader(temp_path)
            df = loader.get_data()

            # Check all amounts are numeric
            assert pd.api.types.is_numeric_dtype(df['Amount'])

            # Check values
            assert df.loc[0, 'Amount'] == 2900.00
            assert df.loc[1, 'Amount'] == 1500.50
        finally:
            os.unlink(temp_path)

    def test_invalid_amount_raises_error(self):
        """Test that invalid amount values raise appropriate error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Creditor,Debtor,Amount,Currency\n")
            f.write("Alice,Bob,2900.00,USD\n")
            f.write("Bob,Charlie,invalid,USD\n")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid amount values found"):
                loader = Loader(temp_path)
        finally:
            os.unlink(temp_path)

    def test_integer_amounts_with_commas(self):
        """Test integer amounts with comma separators."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Creditor,Debtor,Amount,Currency\n")
            f.write('Alice,Bob,"2,900",USD\n')
            f.write('Bob,Charlie,"10,000",USD\n')
            temp_path = f.name

        try:
            loader = Loader(temp_path)
            df = loader.get_data()

            # Check all amounts are numeric
            assert pd.api.types.is_numeric_dtype(df['Amount'])

            # Check values
            assert df.loc[0, 'Amount'] == 2900
            assert df.loc[1, 'Amount'] == 10000
        finally:
            os.unlink(temp_path)

    def test_amount_cleaning_with_excel(self):
        """Test amount cleaning works with Excel files."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xlsx', delete=False) as f:
            temp_path = f.name

            # Create DataFrame with comma-formatted amounts (as strings)
            df = pd.DataFrame({
                'Creditor': ['Alice', 'Bob'],
                'Debtor': ['Bob', 'Charlie'],
                'Amount': ['2,900.00', '1,500.50'],
                'Currency': ['USD', 'USD']
            })
            df.to_excel(temp_path, index=False)

        try:
            loader = Loader(temp_path)
            loaded_df = loader.get_data()

            # Check all amounts are numeric
            assert pd.api.types.is_numeric_dtype(loaded_df['Amount'])

            # Check values
            assert loaded_df.loc[0, 'Amount'] == 2900.00
            assert loaded_df.loc[1, 'Amount'] == 1500.50
        finally:
            os.unlink(temp_path)

    def test_custom_column_name_with_commas(self):
        """Test amount cleaning works with custom column names."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("From,To,Value,Curr\n")
            f.write('Alice,Bob,"2,900.00",USD\n')
            f.write('Bob,Charlie,"1,500.50",USD\n')
            temp_path = f.name

        try:
            cfg = DataFormat(
                col_creditor='From',
                col_debtor='To',
                col_tot_amount='Value',
                col_currency='Curr'
            )
            loader = Loader(temp_path, cfg=cfg)
            df = loader.get_data()

            # Check all amounts are numeric
            assert pd.api.types.is_numeric_dtype(df['Value'])

            # Check values
            assert df.loc[0, 'Value'] == 2900.00
            assert df.loc[1, 'Value'] == 1500.50
        finally:
            os.unlink(temp_path)
