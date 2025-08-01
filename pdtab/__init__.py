"""
pdtab: Pandas-based Tabulation Library
=====================================

A comprehensive Python library that replicates Stata's tabulate functionality using pandas.

Main Functions:
--------------
- tabulate: Main tabulation function for one-way and two-way tables
- tab1: One-way tabulations for multiple variables  
- tab2: All possible two-way tabulations
- tabi: Immediate tabulation from supplied data
"""

__version__ = "0.1.1"
__author__ = "Bryce Wang"
__email__ = "brycew6m@stanford.edu"

# Import main functions to top level
from .core.oneway import OneWayTabulator
from .core.twoway import TwoWayTabulator  
from .core.summarize import SummarizeTabulator
from .utils.data_processing import validate_data, process_weights

def tabulate(varname1, varname2=None, data=None, weights=None, **options):
    """
    Create frequency tables with optional statistical tests and measures of association.
    
    This is the main tabulation function that replicates Stata's tabulate command.
    For one variable, creates a one-way frequency table. For two variables, creates
    a two-way crosstabulation with optional statistical tests.
    
    Parameters
    ----------
    varname1 : str or array-like
        First variable name (if data provided) or array of values
    varname2 : str or array-like, optional
        Second variable name (if data provided) or array of values  
        If provided, creates two-way table
    data : pandas.DataFrame, optional
        Input dataset. If not provided, varname1 and varname2 should be arrays
    weights : str or array-like, optional
        Weight variable name (if data provided) or array of weights
    **options : dict
        Additional options controlling table display and statistics
        
        One-way options:
        - missing : bool, treat missing values as valid category
        - sort : bool, sort table by frequency (descending)
        - plot : bool, create bar chart of frequencies
        - nolabel : bool, show numeric codes instead of labels
        - nofreq : bool, suppress frequency display
        - generate : str, create indicator variables with given prefix
        - subpop : str or array-like, restrict to subpopulation
        
        Two-way options:
        - chi2 : bool, report Pearson's chi-square test
        - exact : bool, report Fisher's exact test
        - gamma : bool, report Goodman and Kruskal's gamma
        - lrchi2 : bool, report likelihood-ratio chi-square
        - taub : bool, report Kendall's tau-b
        - V : bool, report Cramér's V
        - row : bool, show row percentages
        - column : bool, show column percentages  
        - cell : bool, show cell percentages
        - expected : bool, show expected frequencies
        - nofreq : bool, suppress frequency display
        - missing : bool, treat missing values as valid categories
        - wrap : bool, do not break wide tables
        - nolabel : bool, show numeric codes instead of labels
        
        Summary options (when summarize specified):
        - summarize : str, variable to summarize
        - means : bool, show means (default True)
        - standard : bool, show standard deviations (default True)  
        - freq : bool, show frequencies (default True)
        - obs : bool, show number of observations
        
    Returns
    -------
    TabulationResult
        Object containing the tabulation results with methods for display and export
        
    Examples
    --------
    >>> import pandas as pd
    >>> import pdtab
    >>> 
    >>> # Create sample data
    >>> df = pd.DataFrame({
    ...     'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
    ...     'education': ['High School', 'College', 'College', 'High School', 'Graduate'],
    ...     'income': [35000, 45000, 55000, 40000, 75000]
    ... })
    >>>
    >>> # One-way tabulation
    >>> result = pdtab.tabulate('gender', data=df)
    >>> print(result)
    >>>
    >>> # Two-way tabulation with chi-square test
    >>> result = pdtab.tabulate('gender', 'education', data=df, chi2=True)
    >>> print(result)
    >>>
    >>> # Summary tabulation  
    >>> result = pdtab.tabulate('gender', data=df, summarize='income')
    >>> print(result)
    """
    
    # Validate and process input data
    df, var1, var2, wts = validate_data(varname1, varname2, data, weights)
    
    # Check if this is a summary tabulation
    if 'summarize' in options:
        tabulator = SummarizeTabulator(df, var1, var2, weights=wts, **options)
    elif var2 is not None:
        # Two-way tabulation
        tabulator = TwoWayTabulator(df, var1, var2, weights=wts, **options)
    else:
        # One-way tabulation
        tabulator = OneWayTabulator(df, var1, weights=wts, **options)
    
    return tabulator.compute()


def tab1(varlist, data=None, weights=None, **options):
    """
    Create one-way tabulations for multiple variables.
    
    Equivalent to running tabulate separately for each variable in varlist.
    
    Parameters
    ----------
    varlist : list of str or list of array-like
        List of variable names (if data provided) or list of arrays
    data : pandas.DataFrame, optional
        Input dataset
    weights : str or array-like, optional  
        Weight variable name or array of weights
    **options : dict
        Options passed to each tabulate call (see tabulate documentation)
        
    Returns
    -------
    dict
        Dictionary mapping variable names to TabulationResult objects
        
    Examples
    --------
    >>> results = pdtab.tab1(['gender', 'education'], data=df)
    >>> for var, result in results.items():
    ...     print(f"\\n{var}:")
    ...     print(result)
    """
    results = {}
    for var in varlist:
        results[var] = tabulate(var, data=data, weights=weights, **options)
    return results


def tab2(varlist, data=None, weights=None, **options):
    """
    Create all possible two-way tabulations from a list of variables.
    
    Creates a two-way tabulation for every pair of variables in varlist.
    
    Parameters
    ---------- 
    varlist : list of str or list of array-like
        List of variable names (if data provided) or list of arrays
    data : pandas.DataFrame, optional
        Input dataset
    weights : str or array-like, optional
        Weight variable name or array of weights  
    **options : dict
        Options passed to each tabulate call (see tabulate documentation)
        
    Returns
    -------
    dict
        Dictionary mapping variable pair tuples to TabulationResult objects
        
    Examples
    --------
    >>> results = pdtab.tab2(['gender', 'education', 'region'], data=df)
    >>> for pair, result in results.items():
    ...     print(f"\\n{pair[0]} x {pair[1]}:")
    ...     print(result)
    """
    results = {}
    for i in range(len(varlist)):
        for j in range(i + 1, len(varlist)):
            var1, var2 = varlist[i], varlist[j] 
            results[(var1, var2)] = tabulate(var1, var2, data=data, weights=weights, **options)
    return results


def tabi(table_data, **options):
    """
    Create tabulation from immediate data.
    
    Takes table data directly rather than computing from variables.
    Useful for quick analysis of pre-tabulated data.
    
    Parameters
    ----------
    table_data : array-like or str
        For 2x2 tables: can be string like "30 18 \\ 38 14" 
        For general tables: 2D array or nested list
    **options : dict
        Options for statistical tests and display (see tabulate documentation)
        
    Returns
    -------
    TabulationResult
        Object containing the tabulation results
        
    Examples
    --------
    >>> # 2x2 table from string
    >>> result = pdtab.tabi("30 18 \\ 38 14", exact=True)
    >>> print(result)
    >>>
    >>> # General table from array
    >>> table = [[30, 18, 10], [38, 14, 5]]
    >>> result = pdtab.tabi(table, chi2=True)
    >>> print(result)
    """
    from .core.immediate import ImmediateTabulator
    tabulator = ImmediateTabulator(table_data, **options)
    return tabulator.compute()


# Export main functions
__all__ = [
    'tabulate',
    'tab1', 
    'tab2',
    'tabi',
    'OneWayTabulator',
    'TwoWayTabulator', 
    'SummarizeTabulator'
]
