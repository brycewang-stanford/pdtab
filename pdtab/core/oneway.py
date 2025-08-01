"""
One-way Tabulation Module
========================

This module implements one-way frequency tabulation functionality,
replicating Stata's one-way tabulate command.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Union
import warnings

from ..utils.data_processing import (
    handle_missing_values,
    prepare_categorical_data,
    format_number
)


class TabulationResult:
    """
    Container for tabulation results with display and export capabilities.
    """
    
    def __init__(self, table: pd.DataFrame, 
                 statistics: Optional[Dict] = None,
                 options: Optional[Dict] = None):
        self.table = table
        self.statistics = statistics or {}
        self.options = options or {}
        
    def __str__(self) -> str:
        """String representation of the tabulation result."""
        return self._format_output()
        
    def __repr__(self) -> str:
        """Representation of the tabulation result."""
        return f"TabulationResult(shape={self.table.shape})"
        
    def _format_output(self) -> str:
        """Format the output in Stata-like style."""
        lines = []
        
        # Table header
        if 'variable_label' in self.options:
            lines.append(f"\n{self.options['variable_label']}")
        
        # Format the main table
        if hasattr(self.table, 'index'):
            # Create formatted table
            formatted_table = []
            
            # Header
            headers = [''] + list(self.table.columns)
            formatted_table.append(headers)
            
            # Data rows
            for idx, row in self.table.iterrows():
                row_data = [str(idx)] + [format_number(val) if isinstance(val, (int, float)) else str(val) 
                                        for val in row.values]
                formatted_table.append(row_data)
            
            # Calculate column widths
            col_widths = []
            for col_idx in range(len(headers)):
                max_width = max(len(str(formatted_table[row_idx][col_idx])) 
                              for row_idx in range(len(formatted_table)))
                col_widths.append(max(max_width, 8))  # Minimum width of 8
            
            # Format and add rows
            for row_idx, row_data in enumerate(formatted_table):
                if row_idx == 0:
                    # Header row
                    line = "  ".join(data.rjust(width) for data, width in zip(row_data, col_widths))
                    lines.append(line)
                    lines.append("-" * len(line))  # Separator line
                else:
                    # Data rows
                    line = "  ".join(data.rjust(width) for data, width in zip(row_data, col_widths))
                    lines.append(line)
            
            # Add total line if present
            if 'Total' in self.table.index or self.table.index.name == 'Total':
                lines.append("-" * len(lines[-1]))
        
        # Add statistics if present
        if self.statistics:
            lines.append("")
            for stat_name, stat_value in self.statistics.items():
                if isinstance(stat_value, dict):
                    for sub_name, sub_value in stat_value.items():
                        lines.append(f"{stat_name}_{sub_name}: {format_number(sub_value)}")
                else:
                    lines.append(f"{stat_name}: {format_number(stat_value)}")
        
        return "\n".join(lines)
        
    def to_dict(self) -> Dict:
        """Export results as dictionary."""
        return {
            'table': self.table.to_dict(),
            'statistics': self.statistics,
            'options': self.options
        }
        
    def to_html(self) -> str:
        """Export as HTML table."""
        html = self.table.to_html()
        if self.statistics:
            html += "<br><b>Statistics:</b><br>"
            for name, value in self.statistics.items():
                html += f"{name}: {value}<br>"
        return html


class OneWayTabulator:
    """
    One-way frequency tabulation class.
    
    Implements functionality equivalent to Stata's one-way tabulate command.
    """
    
    def __init__(self, data: pd.DataFrame, 
                 variable: str,
                 weights: Optional[np.ndarray] = None,
                 **options):
        """
        Initialize one-way tabulator.
        
        Parameters
        ----------
        data : DataFrame
            Input dataset
        variable : str
            Variable name to tabulate
        weights : array-like, optional
            Observation weights
        **options : dict
            Tabulation options
        """
        self.data = data.copy()
        self.variable = variable
        self.weights = weights
        self.options = options
        
        # Validate inputs
        if variable not in data.columns:
            raise ValueError(f"Variable '{variable}' not found in data")
            
        if weights is not None and len(weights) != len(data):
            raise ValueError("Length of weights must match data length")
    
    def compute(self) -> TabulationResult:
        """
        Compute the one-way tabulation.
        
        Returns
        -------
        TabulationResult
            Object containing tabulation results
        """
        # Handle missing values
        data, weights = handle_missing_values(
            self.data, 
            [self.variable],
            missing=self.options.get('missing', False),
            weights=self.weights
        )
        
        if len(data) == 0:
            warnings.warn("No observations remain after handling missing values")
            empty_table = pd.DataFrame(columns=['Freq', 'Percent', 'Cum'])
            return TabulationResult(empty_table, options=self.options)
        
        # Prepare categorical data
        series, labels = prepare_categorical_data(
            data[self.variable],
            nolabel=self.options.get('nolabel', False),
            sort_values=False  # We'll handle sorting separately
        )
        
        # Compute frequency table
        if weights is not None:
            # Weighted frequencies
            freq_table = pd.Series(weights, index=series).groupby(level=0).sum()
        else:
            # Unweighted frequencies
            freq_table = series.value_counts(sort=False)
        
        # Sort if requested
        if self.options.get('sort', False):
            freq_table = freq_table.sort_values(ascending=False)
        else:
            # Sort by index (category values)
            freq_table = freq_table.sort_index()
        
        # Calculate percentages
        total_freq = freq_table.sum()
        percent = (freq_table / total_freq * 100) if total_freq > 0 else freq_table * 0
        cumulative = percent.cumsum()
        
        # Create result table
        result_table = pd.DataFrame({
            'Freq': freq_table,
            'Percent': percent,
            'Cum': cumulative
        })
        
        # Add total row
        total_row = pd.Series({
            'Freq': total_freq,
            'Percent': 100.0,
            'Cum': 100.0
        }, name='Total')
        result_table = pd.concat([result_table, total_row.to_frame().T])
        
        # Apply display options
        if self.options.get('nofreq', False):
            result_table = result_table.drop(columns=['Freq'])
        
        # Store options for display
        display_options = self.options.copy()
        display_options['variable_label'] = self.variable
        
        # Generate indicator variables if requested
        if 'generate' in self.options:
            self._generate_indicators(data, series, labels)
        
        return TabulationResult(result_table, options=display_options)
    
    def _generate_indicators(self, data: pd.DataFrame, 
                           series: pd.Series, 
                           labels: Dict) -> None:
        """
        Generate indicator variables for each category.
        
        Parameters
        ----------
        data : DataFrame
            Input data
        series : Series
            Categorical series
        labels : dict
            Value labels mapping
        """
        stub_name = self.options['generate']
        unique_values = series.dropna().unique()
        
        for i, value in enumerate(sorted(unique_values), 1):
            var_name = f"{stub_name}{i}"
            indicator = (series == value).astype(int)
            
            # Add to original data (this would be done in calling context)
            # For now, we just store the information
            label = labels.get(value, str(value))
            self.options[f'generated_{var_name}'] = {
                'values': indicator,
                'label': f"{self.variable}=={label}"
            }


def tab1(varlist, data=None, weights=None, **options):
    """
    Create one-way tabulations for multiple variables.
    
    Parameters
    ----------
    varlist : list
        List of variable names
    data : DataFrame
        Input dataset
    weights : array-like, optional
        Observation weights
    **options : dict
        Options passed to each tabulation
        
    Returns
    -------
    dict
        Dictionary mapping variable names to TabulationResult objects
    """
    results = {}
    
    for var in varlist:
        try:
            tabulator = OneWayTabulator(data, var, weights=weights, **options)
            results[var] = tabulator.compute()
        except Exception as e:
            warnings.warn(f"Error tabulating variable '{var}': {str(e)}")
            results[var] = None
    
    return results
