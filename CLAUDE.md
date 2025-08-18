# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EasySplit is a Python-based bill splitting tool designed for group trips. It processes payment records from data sheets (.xlsx, .csv, .tsv) and generates an optimized repayment scheme with the minimum number of transactions. The tool supports multiple currencies with exchange rate conversion.

## Key Commands

### Installation
```bash
# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_auto_detect.py -v

# Run integration tests
uv run pytest tests/test_integration.py -v
```

### Running the CLI tool
```bash
# Basic usage with auto-detection (detects Payer/Payee or Creditor/Debtor columns)
splitbill \
    --file "path/to/data.xlsx" \
    --standard_currency "HKD" \
    --exchange_rate "KRW/HKD=0.0057715"

# With custom column names (overrides auto-detection)
splitbill \
    --file "path/to/data.xlsx" \
    --col_creditor "From" \
    --col_debtor "To" \
    --col_tot_amount "Value" \
    --standard_currency "CNY" \
    --exchange_rate "HKD/CNY=0.9177"

# Validate data without processing
splitbill \
    --file "path/to/data.xlsx" \
    --standard_currency "USD" \
    --validate-only
```

### Development
```bash
# Install in editable mode for development
uv pip install -e .

# Run the module directly with uv
uv run python -m easysplit --file "samples/sample_data.csv" --standard_currency "HKD"

# Run sample script
uv run bash samples/run.sh
```

## Architecture

### Core Components

1. **CLI Entry Point** (`src/easysplit/__main__.py`)
   - Parses command-line arguments
   - Coordinates data loading, graph processing, and result output
   - Handles exchange rate registration

2. **Data Loading** (`src/easysplit/loader.py`)
   - `Loader` class: Loads and preprocesses transaction data from spreadsheets
   - `DataFormat` class: Encapsulates column naming and data format configuration
     - Auto-detects column names (Payer/Payee or Creditor/Debtor)
     - Case-insensitive column detection
     - Supports mixed column combinations (e.g., Payer + Debtor)
   - Supports CSV, TSV, and Excel formats
   - Handles member extraction and transaction normalization

3. **Graph Processing** (`src/easysplit/graph.py`)
   - `LendingGraph` class: Represents lending relationships as a directed weighted graph
   - Implements graph simplification algorithm to minimize transactions
   - Tracks net cash flows for each participant
   - `simplest_equiv()` function: Core algorithm for finding optimal repayment scheme

4. **Exchange Rates** (`src/easysplit/exr.py`)
   - `ExchangeRates` class: Manages currency conversion
   - Supports multiple exchange rate pairs
   - Converts all amounts to a standard currency for settlement

5. **Configuration** (`src/easysplit/config.py`)
   - Column name aliases for auto-detection
   - All selector aliases ("all", "*", "ALL", "All")
   - Default column names and separators
   - Configurable via CLI arguments

6. **Data Validation** (`src/easysplit/validator.py`)
   - Validates data structure and required columns
   - Checks for missing or invalid values
   - Validates currency exchange rates
   - Provides helpful error messages with column name suggestions

### Data Flow

1. User provides spreadsheet with transaction records (Creditor, Debtor, Amount, Currency)
2. Loader reads and preprocesses data, expanding "all" selector to actual members
3. Exchange rates convert all amounts to standard currency
4. Graph structure captures all lending relationships
5. Simplification algorithm reduces to minimum transactions
6. Results displayed and optionally exported to CSV

### Key Implementation Details

- **Auto-detection**: The system automatically detects column names from predefined aliases
  - Creditor columns: "Creditor", "Payer"
  - Debtor columns: "Debtor", "Payee"
  - Amount columns: "Amount", "Total"
  - Currency columns: "Currency", "Curr"
- **All selector flexibility**: Supports multiple formats ("all", "*", "ALL", "All") for indicating all members
- The graph simplification algorithm works by matching creditors and debtors to minimize the total number of transactions
- Members can be specified individually or using an "all" selector
- Multiple people can be listed in a single cell, separated by comma (customizable separator)
- The system maintains floating-point tolerance (ABS_TOL = 1e-02) for amount comparisons

## Important Notes

- The `tests/` directory contains pytest unit and integration tests
- The `src/tests/` directory contains manual debugging scripts (not formal tests)
- The project uses Python 3.10+ features
- All currency conversions are applied before graph simplification
- The tool is read-only on input files and only writes to specified output paths
- Column name detection is case-insensitive and prioritizes user-specified values over auto-detection