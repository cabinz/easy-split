# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EasySplit is a Python-based bill splitting tool designed for group trips. It processes payment records from data sheets (.xlsx, .csv, .tsv) and generates an optimized repayment scheme with the minimum number of transactions. The tool supports multiple currencies with exchange rate conversion.

## Key Commands

### Installation
```bash
pip install .
```

### Running the CLI tool
```bash
# Basic usage with exchange rates
splitbill \
    --file "path/to/data.xlsx" \
    --standard_currency "HKD" \
    --exchange_rate "KRW/HKD=0.0057715"

# With custom column names
splitbill \
    --file "path/to/data.xlsx" \
    --col_creditor "Payer" \
    --col_debtor "Payee" \
    --standard_currency "CNY" \
    --exchange_rate "HKD/CNY=0.9177"
```

### Development
```bash
# Install in editable mode for development
pip install -e .

# Run the module directly
python -m easysplit --file "samples/sample_data.xlsx" --standard_currency "HKD"
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
   - Default column names and separators
   - Configurable via CLI arguments

### Data Flow

1. User provides spreadsheet with transaction records (Creditor, Debtor, Amount, Currency)
2. Loader reads and preprocesses data, expanding "all" selector to actual members
3. Exchange rates convert all amounts to standard currency
4. Graph structure captures all lending relationships
5. Simplification algorithm reduces to minimum transactions
6. Results displayed and optionally exported to CSV

### Key Implementation Details

- The graph simplification algorithm works by matching creditors and debtors to minimize the total number of transactions
- Members can be specified individually or using an "all" selector (default: "all", customizable)
- Multiple people can be listed in a single cell, separated by comma (customizable separator)
- The system maintains floating-point tolerance (ABS_TOL = 1e-02) for amount comparisons

## Important Notes

- The `src/tests/` directory contains manual debugging scripts, not formal unit tests
- The project uses Python 3.10+ features
- All currency conversions are applied before graph simplification
- The tool is read-only on input files and only writes to specified output paths