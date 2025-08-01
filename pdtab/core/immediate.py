"""
Immediate Tabulation Module
==========================

This module implements immediate tabulation functionality,
replicating Stata's tabi command for creating tables from
direct data input.
"""

import pandas as pd
import numpy as np
from typing import Union, Dict, Any, List
import warnings
import re

from ..stats.tests import run_all_tests
from .oneway import TabulationResult


class ImmediateTabulator:
    """
    Immediate tabulation class.
    
    Implements functionality equivalent to Stata's tabi command,
    which creates tabulation from immediately supplied data rather
    than from variables in a dataset.
    """
    
    def __init__(self, table_data: Union[str, List, np.ndarray], **options):
        """
        Initialize immediate tabulator.
        
        Parameters
        ----------
        table_data : str, list, or array-like
            Input table data. Can be:
            - String in Stata format: "30 18 \\ 38 14" for 2x2 table
            - 2D list: [[30, 18], [38, 14]]
            - 2D numpy array
        **options : dict
            Tabulation options
        """
        self.table_data = table_data
        self.options = options
        
        # Parse the input data
        self.observed = self._parse_table_data(table_data)
        
    def _parse_table_data(self, data: Union[str, List, np.ndarray]) -> np.ndarray:
        """
        Parse various formats of table data into numpy array.
        
        Parameters
        ----------
        data : str, list, or array-like
            Input table data
            
        Returns
        -------
        ndarray
            Parsed table as 2D numpy array
        """
        if isinstance(data, str):
            # Parse Stata-style string format
            return self._parse_string_format(data)
        elif isinstance(data, (list, tuple)):
            # Convert list to numpy array
            return np.array(data, dtype=float)
        elif isinstance(data, np.ndarray):
            # Already a numpy array
            return data.astype(float)
        else:
            raise ValueError("table_data must be string, list, or numpy array")
    
    def _parse_string_format(self, data_str: str) -> np.ndarray:
        """
        Parse Stata-style string format for table data.
        
        Examples:
        - "30 18 \\ 38 14" -> [[30, 18], [38, 14]]
        - "30 18 38 \\ 13 7 22" -> [[30, 18, 38], [13, 7, 22]]
        
        Parameters
        ----------
        data_str : str
            String representation of table
            
        Returns
        -------
        ndarray
            Parsed table
        """
        # Split by backslash (row separator)
        rows = re.split(r'\\+', data_str.strip())
        
        table = []
        for row_str in rows:
            # Split each row by whitespace
            row_values = row_str.strip().split()
            if row_values:  # Skip empty rows
                try:
                    row = [float(val) for val in row_values]
                    table.append(row)
                except ValueError as e:
                    raise ValueError(f"Invalid numeric value in table data: {e}")
        
        if not table:
            raise ValueError("No valid data found in string")
        
        # Check that all rows have the same length
        row_lengths = [len(row) for row in table]
        if len(set(row_lengths)) > 1:
            raise ValueError("All rows must have the same number of columns")
        
        return np.array(table, dtype=float)
    
    def compute(self) -> TabulationResult:
        """
        Compute the immediate tabulation.
        
        Returns
        -------
        TabulationResult
            Object containing tabulation results
        """
        # Validate the table
        if self.observed.size == 0:
            raise ValueError("Table data cannot be empty")
        
        if len(self.observed.shape) != 2:
            raise ValueError("Table data must be 2-dimensional")
        
        if np.any(self.observed < 0):
            raise ValueError("Table frequencies cannot be negative")
        
        # Create basic frequency table
        display_table = self._create_display_table()
        
        # Compute statistical tests
        statistics = self._compute_statistics()
        
        # Store options for display
        display_options = self.options.copy()
        display_options['immediate_table'] = True
        
        return TabulationResult(display_table, statistics=statistics, options=display_options)
    
    def _create_display_table(self) -> pd.DataFrame:
        """
        Create the display table from observed frequencies.
        
        Returns
        -------
        DataFrame
            Formatted display table
        """
        rows, cols = self.observed.shape
        
        # Create row and column labels
        row_labels = [f"row{i+1}" if i < rows-1 else "Total" for i in range(rows)]
        col_labels = [f"col{j+1}" if j < cols-1 else "Total" for j in range(cols)]
        
        # For 2x2 tables, use simple numbering
        if rows == 2 and cols == 2:
            row_labels = ['1', '2']
            col_labels = ['1', '2']
        
        # Create DataFrame
        display_table = pd.DataFrame(
            self.observed,
            index=row_labels,
            columns=col_labels
        )
        
        # Add marginals if not already present
        if rows > 1 and cols > 1:
            # Add row totals
            if 'Total' not in display_table.columns:
                display_table['Total'] = display_table.sum(axis=1)
            
            # Add column totals
            if 'Total' not in display_table.index:
                col_totals = display_table.sum(axis=0)
                total_row = pd.Series(col_totals, name='Total')
                display_table = pd.concat([display_table, total_row.to_frame().T])
        
        return display_table
    
    def _compute_statistics(self) -> Dict[str, Any]:
        """
        Compute statistical tests for immediate tabulation.
        
        Returns
        -------
        dict
            Dictionary of statistical results
        """
        # For immediate tables, we typically want at least Fisher's exact for 2x2
        # and chi-square for larger tables
        
        # Default tests based on table size
        if self.observed.shape == (2, 2) and not any(
            self.options.get(opt, False) for opt in ['chi2', 'exact', 'lrchi2', 'V', 'gamma', 'taub']
        ):
            # Default to Fisher's exact for 2x2 tables
            test_options = {'exact': True}
        else:
            # Use specified options or default to chi-square for larger tables
            test_options = {
                'chi2': self.options.get('chi2', False),
                'exact': self.options.get('exact', False),
                'lrchi2': self.options.get('lrchi2', False),
                'V': self.options.get('V', False),
                'gamma': self.options.get('gamma', False),
                'taub': self.options.get('taub', False)
            }
            
            # If no tests specified and not 2x2, default to chi-square
            if not any(test_options.values()) and self.observed.shape != (2, 2):
                test_options['chi2'] = True
        
        # Run statistical tests
        try:
            statistics = run_all_tests(self.observed, **test_options)
        except Exception as e:
            warnings.warn(f"Error computing statistics: {str(e)}")
            statistics = {}
        
        return statistics


def tabi(table_data: Union[str, List, np.ndarray], **options) -> TabulationResult:
    """
    Create tabulation from immediate data.
    
    This function replicates Stata's tabi command functionality.
    
    Parameters
    ----------
    table_data : str, list, or array-like
        Input table data in various formats:
        - String: "30 18 \\ 38 14" (Stata format)
        - List: [[30, 18], [38, 14]]
        - Array: numpy array of frequencies
    **options : dict
        Statistical test and display options:
        - chi2 : bool, compute Pearson's chi-square
        - exact : bool, compute Fisher's exact test
        - lrchi2 : bool, compute likelihood-ratio chi-square
        - V : bool, compute Cramér's V
        - gamma : bool, compute Goodman and Kruskal's gamma
        - taub : bool, compute Kendall's tau-b
        - replace : bool, replace current data with table (not implemented)
        
    Returns
    -------
    TabulationResult
        Object containing tabulation results
        
    Examples
    --------
    >>> import pdtab
    >>> 
    >>> # 2x2 table with Fisher's exact test (default)
    >>> result = pdtab.tabi("30 18 \\ 38 14")
    >>> print(result)
    >>>
    >>> # 2x3 table with chi-square test
    >>> result = pdtab.tabi("30 18 38 \\ 13 7 22", chi2=True)
    >>> print(result)
    >>>
    >>> # Using list format with all tests
    >>> table = [[30, 18], [38, 14]]
    >>> result = pdtab.tabi(table, chi2=True, exact=True, V=True)
    >>> print(result)
    """
    tabulator = ImmediateTabulator(table_data, **options)
    return tabulator.compute()
