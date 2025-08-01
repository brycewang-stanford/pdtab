"""
Data Processing Utilities for pdtab
===================================

This module contains utility functions for data validation, processing, and preparation
for tabulation operations.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, Tuple, Any


def validate_data(varname1: Union[str, np.ndarray, pd.Series], 
                  varname2: Optional[Union[str, np.ndarray, pd.Series]] = None,
                  data: Optional[pd.DataFrame] = None,
                  weights: Optional[Union[str, np.ndarray, pd.Series]] = None) -> Tuple[pd.DataFrame, str, Optional[str], Optional[np.ndarray]]:
    """
    Validate and prepare input data for tabulation.
    
    Parameters
    ----------
    varname1 : str or array-like
        First variable name or data
    varname2 : str or array-like, optional
        Second variable name or data
    data : DataFrame, optional
        Input dataset
    weights : str or array-like, optional
        Weight variable name or weights
        
    Returns
    -------
    tuple
        (DataFrame, var1_name, var2_name, weights_array)
    """
    
    if data is not None:
        # Working with DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")
            
        df = data.copy()
        
        # Validate variable names exist in data
        if isinstance(varname1, str):
            if varname1 not in df.columns:
                raise ValueError(f"Variable '{varname1}' not found in data")
            var1_name = varname1
        else:
            raise ValueError("When data is provided, varname1 must be a column name (string)")
            
        var2_name = None
        if varname2 is not None:
            if isinstance(varname2, str):
                if varname2 not in df.columns:
                    raise ValueError(f"Variable '{varname2}' not found in data")
                var2_name = varname2
            else:
                raise ValueError("When data is provided, varname2 must be a column name (string)")
        
        # Process weights
        weights_array = None
        if weights is not None:
            if isinstance(weights, str):
                if weights not in df.columns:
                    raise ValueError(f"Weight variable '{weights}' not found in data")
                weights_array = df[weights].values
            else:
                weights_array = np.asarray(weights)
                if len(weights_array) != len(df):
                    raise ValueError("Length of weights must match length of data")
                    
    else:
        # Working with arrays directly
        var1_data = np.asarray(varname1)
        var1_name = 'var1'
        
        df = pd.DataFrame({var1_name: var1_data})
        
        var2_name = None
        if varname2 is not None:
            var2_data = np.asarray(varname2)
            if len(var2_data) != len(var1_data):
                raise ValueError("varname1 and varname2 must have the same length")
            var2_name = 'var2'
            df[var2_name] = var2_data
            
        # Process weights
        weights_array = None
        if weights is not None:
            weights_array = np.asarray(weights)
            if len(weights_array) != len(df):
                raise ValueError("Length of weights must match length of data")
    
    return df, var1_name, var2_name, weights_array


def process_weights(weights: Optional[np.ndarray], 
                   weight_type: str = 'frequency') -> Optional[np.ndarray]:
    """
    Process and validate weight arrays.
    
    Parameters
    ----------
    weights : array-like, optional
        Weight values
    weight_type : str
        Type of weights: 'frequency', 'analytic', or 'importance'
        
    Returns
    -------
    array-like or None
        Processed weights
    """
    if weights is None:
        return None
        
    weights = np.asarray(weights)
    
    # Check for negative weights
    if np.any(weights < 0):
        raise ValueError("Weights cannot be negative")
        
    # Check for NaN weights
    if np.any(np.isnan(weights)):
        raise ValueError("Weights cannot contain NaN values")
        
    if weight_type == 'frequency':
        # Frequency weights should be non-negative integers or close to integers
        if not np.allclose(weights, np.round(weights)):
            import warnings
            warnings.warn("Frequency weights should be integers. Non-integer weights will be used as-is.")
            
    elif weight_type in ['analytic', 'importance']:
        # These can be any positive real numbers
        pass
    else:
        raise ValueError("weight_type must be 'frequency', 'analytic', or 'importance'")
        
    return weights


def handle_missing_values(data: pd.DataFrame, 
                         variables: list,
                         missing: bool = False,
                         weights: Optional[np.ndarray] = None) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
    """
    Handle missing values in data according to missing option.
    
    Parameters
    ----------
    data : DataFrame
        Input data
    variables : list
        List of variable names to check for missing values
    missing : bool
        If True, treat missing values as valid categories
        If False, exclude observations with missing values
    weights : array-like, optional
        Weight array to filter along with data
        
    Returns
    -------
    tuple
        (filtered_data, filtered_weights)
    """
    df = data.copy()
    
    if not missing:
        # Exclude observations with missing values in any of the variables
        mask = df[variables].notna().all(axis=1)
        df = df[mask]
        
        if weights is not None:
            weights = weights[mask]
            
    else:
        # Convert missing values to a special category
        for var in variables:
            if df[var].dtype == 'object' or pd.api.types.is_categorical_dtype(df[var]):
                # For string/categorical variables, use "." as missing indicator (like Stata)
                df[var] = df[var].fillna(".")
            else:
                # For numeric variables, keep as NaN or convert to string representation
                df[var] = df[var].astype(str).replace('nan', '.')
                
    return df, weights


def prepare_categorical_data(series: pd.Series, 
                           nolabel: bool = False,
                           sort_values: bool = False) -> Tuple[pd.Series, dict]:
    """
    Prepare categorical data for tabulation.
    
    Parameters
    ----------
    series : Series
        Input data series
    nolabel : bool
        If True, use numeric codes instead of labels
    sort_values : bool
        If True, sort by values
        
    Returns
    -------
    tuple
        (processed_series, value_labels_dict)
    """
    # Handle categorical data
    if pd.api.types.is_categorical_dtype(series):
        if nolabel:
            # Use category codes
            processed = series.cat.codes
            # Create mapping from codes to labels
            labels = dict(enumerate(series.cat.categories))
        else:
            # Use category labels
            processed = series
            labels = {i: cat for i, cat in enumerate(series.cat.categories)}
    else:
        # Non-categorical data
        processed = series
        unique_vals = series.dropna().unique()
        if sort_values:
            unique_vals = sorted(unique_vals)
        labels = {val: str(val) for val in unique_vals}
    
    return processed, labels


def create_crosstab(data: pd.DataFrame,
                   var1: str,
                   var2: str,
                   weights: Optional[np.ndarray] = None,
                   normalize: Optional[str] = None) -> pd.DataFrame:
    """
    Create crosstabulation with optional weights and normalization.
    
    Parameters
    ----------
    data : DataFrame
        Input data
    var1 : str
        Row variable name
    var2 : str
        Column variable name  
    weights : array-like, optional
        Weights for observations
    normalize : str, optional
        Normalization method: 'index' (rows), 'columns', 'all', or None
        
    Returns
    -------
    DataFrame
        Crosstabulation table
    """
    if weights is not None:
        # Add weights to data temporarily
        data_with_weights = data.copy()
        data_with_weights['__weights__'] = weights
        
        # Create weighted crosstab
        crosstab = pd.crosstab(
            data_with_weights[var1],
            data_with_weights[var2], 
            values=data_with_weights['__weights__'],
            aggfunc='sum',
            normalize=normalize
        )
    else:
        # Unweighted crosstab
        crosstab = pd.crosstab(
            data[var1],
            data[var2],
            normalize=normalize
        )
        
    return crosstab


def compute_percentages(crosstab: pd.DataFrame,
                       row: bool = False,
                       column: bool = False, 
                       cell: bool = False) -> dict:
    """
    Compute various percentage tables from crosstab.
    
    Parameters
    ----------
    crosstab : DataFrame
        Input crosstabulation
    row : bool
        Compute row percentages
    column : bool  
        Compute column percentages
    cell : bool
        Compute cell percentages
        
    Returns
    -------
    dict
        Dictionary with percentage tables
    """
    percentages = {}
    
    if row:
        percentages['row'] = crosstab.div(crosstab.sum(axis=1), axis=0) * 100
        
    if column:
        percentages['column'] = crosstab.div(crosstab.sum(axis=0), axis=1) * 100
        
    if cell:
        percentages['cell'] = crosstab / crosstab.sum().sum() * 100
        
    return percentages


def format_number(value: float, 
                 decimal_places: int = 2,
                 missing_char: str = ".") -> str:
    """
    Format numbers for display in tables.
    
    Parameters
    ----------
    value : float
        Value to format
    decimal_places : int
        Number of decimal places
    missing_char : str
        Character to use for missing values
        
    Returns
    -------
    str
        Formatted string
    """
    if pd.isna(value):
        return missing_char
    elif value == 0:
        return "0"
    else:
        return f"{value:.{decimal_places}f}"


def create_summary_stats(data: pd.DataFrame,
                        groupby_vars: list,
                        summary_var: str,
                        weights: Optional[np.ndarray] = None,
                        stats: list = ['mean', 'std', 'count']) -> pd.DataFrame:
    """
    Create summary statistics table grouped by categorical variables.
    
    Parameters
    ----------
    data : DataFrame
        Input data
    groupby_vars : list
        Variables to group by
    summary_var : str
        Variable to summarize
    weights : array-like, optional
        Observation weights
    stats : list
        Statistics to compute
        
    Returns
    -------
    DataFrame
        Summary statistics table
    """
    if weights is not None:
        # Weighted statistics are more complex
        df_with_weights = data.copy()
        df_with_weights['__weights__'] = weights
        
        # Group by the categorical variables
        grouped = df_with_weights.groupby(groupby_vars)
        
        results = []
        for name, group in grouped:
            w = group['__weights__']
            x = group[summary_var].dropna()
            w = w[group[summary_var].notna()]
            
            if len(x) == 0:
                continue
                
            stats_dict = {'group': name if isinstance(name, tuple) else (name,)}
            
            if 'mean' in stats:
                stats_dict['mean'] = np.average(x, weights=w)
            if 'std' in stats:
                # Weighted standard deviation
                mean_val = np.average(x, weights=w)
                stats_dict['std'] = np.sqrt(np.average((x - mean_val)**2, weights=w))
            if 'count' in stats:
                stats_dict['count'] = len(x)
            if 'sum_weights' in stats:
                stats_dict['sum_weights'] = w.sum()
                
            results.append(stats_dict)
            
        return pd.DataFrame(results)
    else:
        # Unweighted statistics using pandas
        grouped = data.groupby(groupby_vars)[summary_var]
        
        result_dict = {}
        if 'mean' in stats:
            result_dict['mean'] = grouped.mean()
        if 'std' in stats:
            result_dict['std'] = grouped.std()
        if 'count' in stats:
            result_dict['count'] = grouped.count()
            
        return pd.DataFrame(result_dict)
