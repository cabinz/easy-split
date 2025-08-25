"""
Table formatter for displaying transaction results.
"""

import pandas as pd
import unicodedata


def get_display_width(text):
    """
    Calculate the display width of a string.
    Chinese characters and other wide characters count as 2, others as 1.
    """
    if text is None:
        return 0
    
    width = 0
    for char in str(text):
        # Check if character is East Asian Wide or Fullwidth
        if unicodedata.east_asian_width(char) in ['W', 'F']:
            width += 2
        else:
            width += 1
    return width


def pad_string(text, target_width, align='left'):
    """
    Pad a string to target display width, considering wide characters.
    
    Args:
        text: String to pad
        target_width: Target display width
        align: 'left', 'right', or 'center'
    """
    text = str(text) if text is not None else ''
    current_width = get_display_width(text)
    padding_needed = target_width - current_width
    
    if padding_needed <= 0:
        return text
    
    if align == 'left':
        return text + ' ' * padding_needed
    elif align == 'right':
        return ' ' * padding_needed + text
    else:  # center
        left_pad = padding_needed // 2
        right_pad = padding_needed - left_pad
        return ' ' * left_pad + text + ' ' * right_pad


def format_transaction_table(df, currency=None):
    """
    Format transaction DataFrame into a beautiful table string.
    
    Args:
        df: DataFrame with columns [Creditor, Debtor, Amount]
        currency: Optional currency code to display
    
    Returns:
        Formatted table string
    """
    if df.empty:
        return "No transactions needed - everyone is settled!"
    
    # Get column names from DataFrame
    col_creditor = df.columns[0]
    col_debtor = df.columns[1]
    col_amount = df.columns[2]
    
    # Prepare data with Transaction ID
    rows = []
    for idx, row in df.iterrows():
        transaction_id = idx + 1  # Start from 1 instead of 0
        creditor = str(row[col_creditor])
        debtor = str(row[col_debtor])
        # Format amount with thousand separators
        amount = f"{row[col_amount]:,.2f}"
        rows.append((transaction_id, creditor, debtor, amount))
    
    # Calculate column widths
    # Minimum widths for headers
    width_id = max(2, max(len(str(r[0])) for r in rows))  # "#" header is 1 char
    width_creditor = max(get_display_width("Creditor"), 
                        max(get_display_width(r[1]) for r in rows))
    width_debtor = max(get_display_width("Debtor"), 
                      max(get_display_width(r[2]) for r in rows))
    width_amount = max(get_display_width(col_amount), 
                      max(get_display_width(r[3]) for r in rows))
    
    # Add some padding
    width_id = max(3, width_id + 2)
    width_creditor += 2
    width_debtor += 2
    width_amount += 2
    width_arrow = 5  # Fixed width for arrow column
    
    # Box drawing characters
    top_left = "╔"
    top_right = "╗"
    bottom_left = "╚"
    bottom_right = "╝"
    horizontal = "═"
    vertical = "║"
    cross = "╬"
    t_down = "╦"
    t_up = "╩"
    t_right = "╠"
    t_left = "╣"
    
    # Build the table
    lines = []
    
    # Top border
    top_border = (top_left + 
                 horizontal * width_id + t_down +
                 horizontal * width_creditor + t_down +
                 horizontal * width_arrow + t_down +
                 horizontal * width_debtor + t_down +
                 horizontal * width_amount + top_right)
    lines.append(top_border)
    
    # Header row
    header = (vertical + 
             pad_string("#", width_id, 'center') + vertical +
             pad_string("Creditor", width_creditor, 'center') + vertical +
             pad_string("", width_arrow, 'center') + vertical +
             pad_string("Debtor", width_debtor, 'center') + vertical +
             pad_string(col_amount, width_amount, 'center') + vertical)
    lines.append(header)
    
    # Header separator
    header_sep = (t_right + 
                 horizontal * width_id + cross +
                 horizontal * width_creditor + cross +
                 horizontal * width_arrow + cross +
                 horizontal * width_debtor + cross +
                 horizontal * width_amount + t_left)
    lines.append(header_sep)
    
    # Data rows
    for transaction_id, creditor, debtor, amount in rows:
        data_row = (vertical + 
                   pad_string(str(transaction_id), width_id, 'center') + vertical +
                   pad_string(creditor, width_creditor, 'center') + vertical +
                   pad_string("<--", width_arrow, 'center') + vertical +
                   pad_string(debtor, width_debtor, 'center') + vertical +
                   pad_string(amount, width_amount, 'right') + vertical)
        lines.append(data_row)
    
    # Bottom border
    bottom_border = (bottom_left + 
                    horizontal * width_id + t_up +
                    horizontal * width_creditor + t_up +
                    horizontal * width_arrow + t_up +
                    horizontal * width_debtor + t_up +
                    horizontal * width_amount + bottom_right)
    lines.append(bottom_border)
    
    return '\n'.join(lines)