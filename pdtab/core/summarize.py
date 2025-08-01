"""
Summary Tabulation Module
========================

This module implements summary tabulation functionality,
replicating Stata's tabulate with summarize() option.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import warnings

from ..utils.data_processing import (
    handle_missing_values,
    prepare_categorical_data,
    create_summary_stats,
    format_number
)
from .oneway import TabulationResult


class SummarizeTabulator:
    """
    Summary tabulation class.
    
    Implements functionality equivalent to Stata's tabulate with summarize() option.
    Creates tables of means, standard deviations, and frequencies broken down
    by categorical variables.
    """
    
    def __init__(self, data: pd.DataFrame,
                 variable1: str,
                 variable2: Optional[str] = None,
                 weights: Optional[np.ndarray] = None,
                 **options):
        """
        Initialize summary tabulator.
        
        Parameters
        ----------
        data : DataFrame
            Input dataset
        variable1 : str
            First categorical variable (rows)
        variable2 : str, optional
            Second categorical variable (columns)
        weights : array-like, optional
            Observation weights
        **options : dict
            Tabulation options including 'summarize' variable
        """
        self.data = data.copy()
        self.variable1 = variable1
        self.variable2 = variable2
        self.weights = weights
        self.options = options
        
        # Validate inputs
        variables = [variable1]
        if variable2 is not None:
            variables.append(variable2)
            
        for var in variables:
            if var not in data.columns:
                raise ValueError(f"Variable '{var}' not found in data")
        
        # Check for summarize variable
        if 'summarize' not in options:
            raise ValueError("summarize option is required")
            
        self.summarize_var = options['summarize']
        if self.summarize_var not in data.columns:
            raise ValueError(f"Summarize variable '{self.summarize_var}' not found in data")
            
        if weights is not None and len(weights) != len(data):
            raise ValueError("Length of weights must match data length")
    
    def compute(self) -> TabulationResult:
        """
        Compute the summary tabulation.
        
        Returns
        -------
        TabulationResult
            Object containing tabulation results
        """
        # Handle missing values
        variables = [self.variable1]
        if self.variable2 is not None:
            variables.append(self.variable2)
        variables.append(self.summarize_var)  # Include summary variable
        
        data, weights = handle_missing_values(
            self.data,
            variables,
            missing=self.options.get('missing', False),
            weights=self.weights
        )
        
        if len(data) == 0:
            warnings.warn("No observations remain after handling missing values")
            empty_table = pd.DataFrame()
            return TabulationResult(empty_table, options=self.options)
        
        # Determine what statistics to include
        stats_to_compute = self._get_statistics_list()
        
        # Compute summary statistics
        if self.variable2 is None:
            # One-way summary
            summary_table = self._compute_oneway_summary(data, weights, stats_to_compute)
        else:
            # Two-way summary
            summary_table = self._compute_twoway_summary(data, weights, stats_to_compute)
        
        # Store options for display
        display_options = self.options.copy()
        display_options['summarize_label'] = self.summarize_var
        display_options['variable1_label'] = self.variable1
        if self.variable2:
            display_options['variable2_label'] = self.variable2
        
        return TabulationResult(summary_table, options=display_options)
    
    def _get_statistics_list(self) -> List[str]:
        """
        Determine which statistics to compute based on options.
        
        Returns
        -------
        list
            List of statistics to compute
        """
        # Default is to show all statistics
        default_stats = ['mean', 'std', 'count']
        
        # Check which statistics are explicitly requested or suppressed
        stats = []
        
        if not self.options.get('nomeans', False) and \
           (not any(opt in self.options for opt in ['means', 'standard', 'freq', 'obs']) or 
            self.options.get('means', False)):
            stats.append('mean')
        
        if not self.options.get('nostandard', False) and \
           (not any(opt in self.options for opt in ['means', 'standard', 'freq', 'obs']) or 
            self.options.get('standard', False)):
            stats.append('std')
        
        if not self.options.get('nofreq', False) and \
           (not any(opt in self.options for opt in ['means', 'standard', 'freq', 'obs']) or 
            self.options.get('freq', False)):
            stats.append('count')
        
        # Handle obs (number of observations) - same as count unless weighted
        if not self.options.get('noobs', False) and \
           self.options.get('obs', False) and \
           self.weights is not None:
            stats.append('obs')
        
        # If no specific options given, use defaults
        if not stats:
            stats = default_stats
        
        return stats
    
    def _compute_oneway_summary(self, data: pd.DataFrame,
                               weights: Optional[np.ndarray],
                               stats: List[str]) -> pd.DataFrame:
        """
        Compute one-way summary statistics.
        
        Parameters
        ----------
        data : DataFrame
            Input data
        weights : array-like, optional
            Observation weights
        stats : list
            Statistics to compute
            
        Returns
        -------
        DataFrame
            Summary statistics table
        """
        # Prepare categorical data
        series1, labels1 = prepare_categorical_data(
            data[self.variable1],
            nolabel=self.options.get('nolabel', False)
        )
        
        # Create summary statistics
        summary_df = create_summary_stats(
            data.assign(**{self.variable1: series1}),
            [self.variable1],
            self.summarize_var,
            weights=weights,
            stats=stats
        )
        
        # Format results
        result_table = pd.DataFrame(index=summary_df[self.variable1].unique())
        
        if 'mean' in stats:
            result_table['Mean'] = summary_df.set_index(self.variable1)['mean']
        if 'std' in stats:
            result_table['Std. Dev.'] = summary_df.set_index(self.variable1)['std']
        if 'count' in stats:
            result_table['Freq.'] = summary_df.set_index(self.variable1)['count']
        
        # Add total row
        total_stats = {}
        summary_var_data = data[self.summarize_var].dropna()
        
        if weights is not None:
            weights_clean = weights[data[self.summarize_var].notna()]
            if 'mean' in stats:
                total_stats['Mean'] = np.average(summary_var_data, weights=weights_clean)
            if 'std' in stats:
                mean_val = np.average(summary_var_data, weights=weights_clean)
                total_stats['Std. Dev.'] = np.sqrt(np.average((summary_var_data - mean_val)**2, weights=weights_clean))
            if 'count' in stats:
                total_stats['Freq.'] = len(summary_var_data)
        else:
            if 'mean' in stats:
                total_stats['Mean'] = summary_var_data.mean()
            if 'std' in stats:
                total_stats['Std. Dev.'] = summary_var_data.std()
            if 'count' in stats:
                total_stats['Freq.'] = len(summary_var_data)
        
        total_row = pd.Series(total_stats, name='Total')
        result_table = pd.concat([result_table, total_row.to_frame().T])
        
        return result_table
    
    def _compute_twoway_summary(self, data: pd.DataFrame,
                               weights: Optional[np.ndarray],
                               stats: List[str]) -> pd.DataFrame:
        """
        Compute two-way summary statistics.
        
        Parameters
        ----------
        data : DataFrame
            Input data
        weights : array-like, optional
            Observation weights
        stats : list
            Statistics to compute
            
        Returns
        -------
        DataFrame
            Summary statistics table
        """
        # Prepare categorical data
        series1, labels1 = prepare_categorical_data(
            data[self.variable1],
            nolabel=self.options.get('nolabel', False)
        )
        
        series2, labels2 = prepare_categorical_data(
            data[self.variable2],
            nolabel=self.options.get('nolabel', False)
        )
        
        # Create summary statistics
        summary_df = create_summary_stats(
            data.assign(**{self.variable1: series1, self.variable2: series2}),
            [self.variable1, self.variable2],
            self.summarize_var,
            weights=weights,
            stats=stats
        )
        
        # Reshape to two-way table format
        # This is simplified - full implementation would create proper two-way layout
        pivot_tables = {}
        
        if 'mean' in stats:
            if len(summary_df) > 0:
                pivot_tables['Mean'] = summary_df.pivot(
                    index=self.variable1, 
                    columns=self.variable2, 
                    values='mean'
                )
        
        if 'std' in stats:
            if len(summary_df) > 0:
                pivot_tables['Std. Dev.'] = summary_df.pivot(
                    index=self.variable1,
                    columns=self.variable2,
                    values='std'
                )
        
        if 'count' in stats:
            if len(summary_df) > 0:
                pivot_tables['Freq.'] = summary_df.pivot(
                    index=self.variable1,
                    columns=self.variable2,
                    values='count'
                )
        
        # For now, return the first available table
        # Full implementation would create a properly formatted multi-panel table
        if pivot_tables:
            return list(pivot_tables.values())[0].fillna(0)
        else:
            return pd.DataFrame()


def create_summary_tabulation(data: pd.DataFrame,
                             variable1: str,
                             variable2: Optional[str] = None,
                             summarize_var: str = None,
                             weights: Optional[np.ndarray] = None,
                             **options) -> TabulationResult:
    """
    Create summary tabulation.
    
    Convenience function for creating summary tabulations.
    
    Parameters
    ----------
    data : DataFrame
        Input dataset
    variable1 : str
        First categorical variable
    variable2 : str, optional
        Second categorical variable
    summarize_var : str
        Variable to summarize
    weights : array-like, optional
        Observation weights
    **options : dict
        Additional options
        
    Returns
    -------
    TabulationResult
        Summary tabulation results
    """
    options['summarize'] = summarize_var
    tabulator = SummarizeTabulator(data, variable1, variable2, weights=weights, **options)
    return tabulator.compute()
