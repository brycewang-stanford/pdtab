"""
Two-way Tabulation Module
========================

This module implements two-way frequency tabulation functionality,
replicating Stata's two-way tabulate command with statistical tests
and measures of association.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
import warnings

from ..utils.data_processing import (
    handle_missing_values,
    prepare_categorical_data,
    create_crosstab,
    compute_percentages,
    format_number
)
from ..stats.tests import run_all_tests
from .oneway import TabulationResult


class TwoWayTabulator:
    """
    Two-way frequency tabulation class.
    
    Implements functionality equivalent to Stata's two-way tabulate command
    including statistical tests and measures of association.
    """
    
    def __init__(self, data: pd.DataFrame,
                 variable1: str,
                 variable2: str, 
                 weights: Optional[np.ndarray] = None,
                 **options):
        """
        Initialize two-way tabulator.
        
        Parameters
        ----------
        data : DataFrame
            Input dataset
        variable1 : str
            First variable name (rows)
        variable2 : str
            Second variable name (columns)
        weights : array-like, optional
            Observation weights
        **options : dict
            Tabulation options
        """
        self.data = data.copy()
        self.variable1 = variable1
        self.variable2 = variable2
        self.weights = weights
        self.options = options
        
        # Validate inputs
        for var in [variable1, variable2]:
            if var not in data.columns:
                raise ValueError(f"Variable '{var}' not found in data")
                
        if weights is not None and len(weights) != len(data):
            raise ValueError("Length of weights must match data length")
    
    def compute(self) -> TabulationResult:
        """
        Compute the two-way tabulation.
        
        Returns
        -------
        TabulationResult
            Object containing tabulation results
        """
        # Handle missing values
        data, weights = handle_missing_values(
            self.data,
            [self.variable1, self.variable2],
            missing=self.options.get('missing', False),
            weights=self.weights
        )
        
        if len(data) == 0:
            warnings.warn("No observations remain after handling missing values")
            empty_table = pd.DataFrame()
            return TabulationResult(empty_table, options=self.options)
        
        # Prepare categorical data
        series1, labels1 = prepare_categorical_data(
            data[self.variable1],
            nolabel=self.options.get('nolabel', False)
        )
        
        series2, labels2 = prepare_categorical_data(
            data[self.variable2],
            nolabel=self.options.get('nolabel', False)
        )
        
        # Create basic crosstab
        crosstab = create_crosstab(
            pd.DataFrame({self.variable1: series1, self.variable2: series2}),
            self.variable1,
            self.variable2,
            weights=weights
        )
        
        # Fill missing combinations with 0
        crosstab = crosstab.fillna(0)
        
        # Compute percentages if requested
        percentages = compute_percentages(
            crosstab,
            row=self.options.get('row', False),
            column=self.options.get('column', False),
            cell=self.options.get('cell', False)
        )
        
        # Create display table
        display_table = self._create_display_table(crosstab, percentages)
        
        # Compute statistical tests
        statistics = self._compute_statistics(crosstab)
        
        # Store options for display
        display_options = self.options.copy()
        display_options['variable1_label'] = self.variable1
        display_options['variable2_label'] = self.variable2
        
        return TabulationResult(display_table, statistics=statistics, options=display_options)
    
    def _create_display_table(self, crosstab: pd.DataFrame, 
                            percentages: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create the formatted display table with frequencies and percentages.
        
        Parameters
        ----------
        crosstab : DataFrame
            Basic crosstabulation
        percentages : dict
            Dictionary of percentage tables
            
        Returns
        -------
        DataFrame
            Formatted display table
        """
        # Determine what to display in each cell
        display_components = []
        
        # Always include frequencies unless nofreq is specified
        if not self.options.get('nofreq', False):
            display_components.append('freq')
        
        # Add percentages as requested
        if self.options.get('row', False):
            display_components.append('row')
        if self.options.get('column', False):
            display_components.append('column')
        if self.options.get('cell', False):
            display_components.append('cell')
        
        # If multiple components, create multi-line cells
        if len(display_components) > 1:
            return self._create_multiline_table(crosstab, percentages, display_components)
        else:
            # Single component table
            if display_components == ['freq']:
                display_table = crosstab.copy()
            elif 'row' in display_components:
                display_table = percentages['row']
            elif 'column' in display_components:
                display_table = percentages['column']
            elif 'cell' in display_components:
                display_table = percentages['cell']
            else:
                display_table = crosstab.copy()
        
        # Add marginals (totals)
        display_table = self._add_marginals(display_table, crosstab, percentages)
        
        return display_table
    
    def _create_multiline_table(self, crosstab: pd.DataFrame,
                               percentages: Dict[str, pd.DataFrame],
                               components: list) -> pd.DataFrame:
        """
        Create table with multiple statistics per cell.
        
        Parameters
        ----------
        crosstab : DataFrame
            Basic frequencies
        percentages : dict
            Percentage tables
        components : list
            List of components to include
            
        Returns
        -------
        DataFrame
            Multi-line table with combined statistics
        """
        # For now, create a simplified version
        # In a full implementation, this would create properly formatted multi-line cells
        result = crosstab.copy().astype(str)
        
        for i, row in crosstab.iterrows():
            for j, col in enumerate(crosstab.columns):
                cell_parts = []
                
                if 'freq' in components:
                    cell_parts.append(f"{crosstab.loc[i, col]:.0f}")
                
                if 'row' in components and 'row' in percentages:
                    cell_parts.append(f"{percentages['row'].loc[i, col]:.2f}")
                
                if 'column' in components and 'column' in percentages:
                    cell_parts.append(f"{percentages['column'].loc[i, col]:.2f}")
                
                if 'cell' in components and 'cell' in percentages:
                    cell_parts.append(f"{percentages['cell'].loc[i, col]:.2f}")
                
                result.loc[i, col] = '\n'.join(cell_parts)
        
        return result
    
    def _add_marginals(self, display_table: pd.DataFrame,
                      crosstab: pd.DataFrame,
                      percentages: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Add row and column totals to the display table.
        
        Parameters
        ----------
        display_table : DataFrame
            Main display table
        crosstab : DataFrame
            Frequency crosstab for calculating totals
        percentages : dict
            Percentage tables
            
        Returns
        -------
        DataFrame
            Table with marginals added
        """
        # Add row totals
        row_totals = crosstab.sum(axis=1)
        display_table['Total'] = row_totals
        
        # Add column totals
        col_totals = crosstab.sum(axis=0)
        total_row = col_totals.to_frame().T
        total_row.index = ['Total']
        
        # Add grand total
        grand_total = crosstab.sum().sum()
        total_row['Total'] = grand_total
        
        # Combine
        result = pd.concat([display_table, total_row])
        
        return result
    
    def _compute_statistics(self, crosstab: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute statistical tests and measures of association.
        
        Parameters
        ----------
        crosstab : DataFrame
            Frequency crosstabulation
            
        Returns
        -------
        dict
            Dictionary of statistical results
        """
        # Convert to numpy array for statistical functions
        observed = crosstab.values
        
        # Determine which tests to run based on options
        test_options = {
            'chi2': self.options.get('chi2', False),
            'exact': self.options.get('exact', False),
            'lrchi2': self.options.get('lrchi2', False),
            'V': self.options.get('V', False),
            'gamma': self.options.get('gamma', False),
            'taub': self.options.get('taub', False)
        }
        
        # Run tests if any are requested
        if any(test_options.values()):
            try:
                statistics = run_all_tests(observed, **test_options)
            except Exception as e:
                warnings.warn(f"Error computing statistics: {str(e)}")
                statistics = {}
        else:
            statistics = {}
        
        # Add cell contributions if requested
        if self.options.get('cchi2', False):
            from ..stats.tests import cell_contributions_chi2
            statistics['cchi2'] = cell_contributions_chi2(observed)
        
        if self.options.get('clrchi2', False):
            from ..stats.tests import cell_contributions_lr_chi2  
            statistics['clrchi2'] = cell_contributions_lr_chi2(observed)
        
        if self.options.get('expected', False):
            from ..stats.tests import expected_frequencies
            statistics['expected'] = expected_frequencies(observed)
        
        return statistics


def tab2(varlist, data=None, weights=None, **options):
    """
    Create all possible two-way tabulations from a list of variables.
    
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
        Dictionary mapping variable pairs to TabulationResult objects
    """
    results = {}
    
    # Generate all unique pairs
    for i in range(len(varlist)):
        for j in range(i + 1, len(varlist)):
            var1, var2 = varlist[i], varlist[j]
            
            # Skip if firstonly is specified and first variable not involved
            if options.get('firstonly', False) and i > 0:
                continue
            
            try:
                tabulator = TwoWayTabulator(data, var1, var2, weights=weights, **options)
                results[(var1, var2)] = tabulator.compute()
            except Exception as e:
                warnings.warn(f"Error tabulating variables '{var1}' x '{var2}': {str(e)}")
                results[(var1, var2)] = None
    
    return results
