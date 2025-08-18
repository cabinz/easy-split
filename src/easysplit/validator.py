"""Data validation module for EasySplit."""

from dataclasses import dataclass
from typing import List, Optional, Set
from enum import Enum
import pandas as pd
from pathlib import Path

from .config import *
from .exr import ExchangeRates


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationError:
    """Represents a single validation error or warning."""
    row: Optional[int]  # Row number (1-indexed for user display), None for general errors
    column: Optional[str]  # Column name
    message: str
    severity: Severity
    
    def __str__(self):
        prefix = "✗" if self.severity == Severity.ERROR else "⚠"
        if self.row:
            if self.column:
                return f"  {prefix} Row {self.row}, Column '{self.column}': {self.message}"
            return f"  {prefix} Row {self.row}: {self.message}"
        return f"  {prefix} {self.message}"


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def add_error(self, row: Optional[int], column: Optional[str], message: str):
        self.errors.append(ValidationError(row, column, message, Severity.ERROR))
    
    def add_warning(self, row: Optional[int], column: Optional[str], message: str):
        self.warnings.append(ValidationError(row, column, message, Severity.WARNING))
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def get_all_issues(self) -> List[ValidationError]:
        return self.errors + self.warnings
    
    def print_summary(self):
        """Print validation results summary."""
        if not self.has_errors() and not self.has_warnings():
            print("✓ Data validation passed. No issues found.")
            return
        
        print("\nValidation Errors Found:")
        for error in self.errors:
            print(error)
        for warning in self.warnings:
            print(warning)
        
        print(f"\nFound {len(self.errors)} error(s) and {len(self.warnings)} warning(s).")
        if self.has_errors():
            print("Please fix errors before processing.")


class DataValidator:
    """Validates input data for EasySplit."""
    
    def __init__(self, 
                 df: pd.DataFrame,
                 data_format: 'DataFormat',
                 exrs: Optional[ExchangeRates] = None):
        self.df = df
        self.cfg = data_format
        self.exrs = exrs
        self.result = ValidationResult()
        self.members: Set[str] = set()
    
    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        self.validate_structure()
        if self.result.has_errors():
            return self.result
        
        self.validate_required_fields()
        self.validate_amounts()
        self.validate_currencies()
        self.validate_members()
        
        return self.result
    
    def validate_structure(self):
        """Check if required columns exist."""
        required_columns = [
            self.cfg.col_creditor,
            self.cfg.col_debtor, 
            self.cfg.col_tot_amount
        ]
        
        if self.exrs:
            required_columns.append(self.cfg.col_currency)
        
        missing_columns = []
        for col in required_columns:
            if col not in self.df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            # Provide helpful suggestions based on what's missing
            suggestions = []
            if self.cfg.col_creditor in missing_columns:
                suggestions.append(f"creditor column (looked for: {', '.join(CREDITOR_ALIASES)})")
            if self.cfg.col_debtor in missing_columns:
                suggestions.append(f"debtor column (looked for: {', '.join(DEBTOR_ALIASES)})")
            if self.cfg.col_tot_amount in missing_columns:
                suggestions.append(f"amount column (looked for: {', '.join(AMOUNT_ALIASES)})")
            if self.exrs and self.cfg.col_currency in missing_columns:
                suggestions.append(f"currency column (looked for: {', '.join(CURRENCY_ALIASES)})")
            
            self.result.add_error(
                None, None,
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Could not auto-detect: {', '.join(suggestions)}. "
                f"Please specify column names using CLI arguments."
            )
    
    def validate_required_fields(self):
        """Check for empty or missing values in required fields."""
        for idx, row in self.df.iterrows():
            row_num = idx + 2  # +1 for 0-index, +1 for header row
            
            # Check creditor
            creditor = row[self.cfg.col_creditor]
            if pd.isna(creditor) or str(creditor).strip() == "":
                self.result.add_error(
                    row_num, self.cfg.col_creditor,
                    "Creditor cannot be empty"
                )
            
            # Check debtor
            debtor = row[self.cfg.col_debtor]
            if pd.isna(debtor) or str(debtor).strip() == "":
                self.result.add_error(
                    row_num, self.cfg.col_debtor,
                    f"Debtor cannot be empty (did you mean '{self.cfg.all_selector}'?)"
                )
            
            # Check amount
            amount = row[self.cfg.col_tot_amount]
            if pd.isna(amount):
                self.result.add_error(
                    row_num, self.cfg.col_tot_amount,
                    "Amount cannot be empty"
                )
    
    def validate_amounts(self):
        """Validate that amounts are positive numbers."""
        for idx, row in self.df.iterrows():
            row_num = idx + 2
            amount = row[self.cfg.col_tot_amount]
            
            if pd.notna(amount):
                try:
                    amount_float = float(amount)
                    if amount_float < 0:
                        self.result.add_error(
                            row_num, self.cfg.col_tot_amount,
                            f"Amount cannot be negative: {amount_float}"
                        )
                    elif amount_float == 0:
                        self.result.add_warning(
                            row_num, self.cfg.col_tot_amount,
                            "Amount is 0 (transaction will be ignored)"
                        )
                except (ValueError, TypeError):
                    self.result.add_error(
                        row_num, self.cfg.col_tot_amount,
                        f"Invalid amount value: {amount}"
                    )
    
    def validate_currencies(self):
        """Check currency values and exchange rates."""
        if not self.exrs:
            return
        
        # Collect all currencies used
        currencies_used = set()
        
        for idx, row in self.df.iterrows():
            row_num = idx + 2
            currency = row[self.cfg.col_currency]
            
            if pd.isna(currency) or str(currency).strip() == "":
                self.result.add_error(
                    row_num, self.cfg.col_currency,
                    "Currency cannot be empty when standard currency is specified"
                )
            else:
                currency_str = str(currency).strip().upper()
                currencies_used.add(currency_str)
                
                # Check if exchange rate exists for this currency
                if currency_str != self.exrs.std_currency:
                    try:
                        self.exrs.get_rate(currency_str, self.exrs.std_currency)
                    except ValueError:
                        self.result.add_error(
                            row_num, self.cfg.col_currency,
                            f"Currency '{currency_str}' has no exchange rate to standard currency '{self.exrs.std_currency}'"
                        )
        
        # Report missing exchange rates summary
        if self.result.has_errors():
            missing_currencies = set()
            for error in self.result.errors:
                if "has no exchange rate" in error.message:
                    # Extract currency from error message
                    parts = error.message.split("'")
                    if len(parts) >= 2:
                        missing_currencies.add(parts[1])
            
            if missing_currencies:
                rates_needed = [f"{curr}/{self.exrs.std_currency}" for curr in missing_currencies]
                self.result.add_error(
                    None, None,
                    f"Missing exchange rates: {', '.join(rates_needed)}"
                )
    
    def validate_members(self):
        """Validate creditor and debtor fields."""
        # Helper to check if value is an "all" selector
        def is_all_selector(value: str) -> bool:
            return value.lower().strip() in [sel.lower() for sel in ALL_SELECTOR_ALIASES]
        
        # First pass: collect all members
        for idx, row in self.df.iterrows():
            creditor = str(row[self.cfg.col_creditor]).strip()
            debtor = str(row[self.cfg.col_debtor]).strip()
            
            if not is_all_selector(creditor):
                # Check for multiple creditors
                creditor_list = [c.strip() for c in creditor.split(self.cfg.separator)]
                if len(creditor_list) > 1:
                    self.result.add_error(
                        idx + 2, self.cfg.col_creditor,
                        "Multiple creditors not supported. Please specify only one creditor per transaction"
                    )
                else:
                    self.members.add(creditor_list[0])
            
            if not is_all_selector(debtor):
                debtor_list = [d.strip() for d in debtor.split(self.cfg.separator)]
                self.members.update(debtor_list)
        
        # Second pass: validate "all" usage
        for idx, row in self.df.iterrows():
            row_num = idx + 2
            creditor = str(row[self.cfg.col_creditor]).strip()
            debtor = str(row[self.cfg.col_debtor]).strip()
            
            # Check if any "all" selector is used as creditor
            if is_all_selector(creditor):
                self.result.add_error(
                    row_num, self.cfg.col_creditor,
                    f"'{creditor}' (all selector) cannot be used as creditor"
                )
            
            # Check if "all" is used when member list is empty
            if is_all_selector(debtor) and len(self.members) == 0:
                self.result.add_error(
                    row_num, self.cfg.col_debtor,
                    f"'{debtor}' (all selector) used but no members found in data"
                )
            
            # Validate member names aren't empty after splitting
            if not is_all_selector(debtor):
                debtor_list = [d.strip() for d in debtor.split(self.cfg.separator)]
                for d in debtor_list:
                    if d == "":
                        self.result.add_error(
                            row_num, self.cfg.col_debtor,
                            f"Empty member name after splitting with '{self.cfg.separator}'"
                        )