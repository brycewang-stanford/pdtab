"""
Visualization Module for pdtab
=============================

This module provides plotting functionality for tabulation results,
replicating the plot option from Stata's tabulate command.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, Any, Tuple
import warnings


def plot_oneway_frequencies(table: pd.DataFrame,
                           variable_name: str = "Variable",
                           title: Optional[str] = None,
                           figsize: Tuple[int, int] = (10, 6),
                           style: str = 'stata') -> plt.Figure:
    """
    Create a bar chart of one-way frequencies.
    
    Parameters
    ----------
    table : DataFrame
        Frequency table with 'Freq' column
    variable_name : str
        Name of the variable for labeling
    title : str, optional
        Plot title
    figsize : tuple
        Figure size (width, height)
    style : str
        Plot style ('stata', 'seaborn', 'matplotlib')
        
    Returns
    -------
    Figure
        Matplotlib figure object
    """
    # Set style
    if style == 'stata':
        plt.style.use('default')
        # Configure Stata-like appearance
        plt.rcParams.update({
            'axes.grid': True,
            'grid.alpha': 0.3,
            'axes.axisbelow': True,
            'font.size': 10
        })
    elif style == 'seaborn':
        sns.set_style("whitegrid")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Extract frequencies, excluding Total row if present
    freq_data = table[table.index != 'Total'].copy()
    
    if 'Freq' in freq_data.columns:
        frequencies = freq_data['Freq']
    else:
        # Use first numeric column if no 'Freq' column
        numeric_cols = freq_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            frequencies = freq_data[numeric_cols[0]]
        else:
            warnings.warn("No numeric data found for plotting")
            return fig
    
    # Create bar chart
    bars = ax.bar(range(len(frequencies)), frequencies.values)
    
    # Customize appearance
    ax.set_xlabel(variable_name)
    ax.set_ylabel('Frequency')
    ax.set_title(title or f'Frequency Distribution of {variable_name}')
    
    # Set x-axis labels
    ax.set_xticks(range(len(frequencies)))
    ax.set_xticklabels(frequencies.index, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, frequencies.values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01 * max(frequencies),
                f'{value:.0f}', ha='center', va='bottom')
    
    # Style the plot
    if style == 'stata':
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_twoway_heatmap(crosstab: pd.DataFrame,
                       var1_name: str = "Variable 1",
                       var2_name: str = "Variable 2", 
                       title: Optional[str] = None,
                       figsize: Tuple[int, int] = (10, 8),
                       annot: bool = True,
                       cmap: str = 'Blues') -> plt.Figure:
    """
    Create a heatmap visualization of two-way crosstabulation.
    
    Parameters
    ----------
    crosstab : DataFrame
        Crosstabulation table
    var1_name : str
        Name of first variable (rows)
    var2_name : str
        Name of second variable (columns)
    title : str, optional
        Plot title
    figsize : tuple
        Figure size
    annot : bool
        Whether to annotate cells with values
    cmap : str
        Colormap for heatmap
        
    Returns
    -------
    Figure
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Remove Total rows/columns for cleaner visualization
    plot_data = crosstab.copy()
    if 'Total' in plot_data.index:
        plot_data = plot_data.drop('Total')
    if 'Total' in plot_data.columns:
        plot_data = plot_data.drop('Total', axis=1)
    
    # Create heatmap
    sns.heatmap(plot_data, 
                annot=annot, 
                fmt='.0f' if annot else '',
                cmap=cmap,
                ax=ax,
                cbar_kws={'label': 'Frequency'})
    
    # Customize labels
    ax.set_xlabel(var2_name)
    ax.set_ylabel(var1_name)
    ax.set_title(title or f'{var1_name} by {var2_name}')
    
    # Rotate labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    return fig


def plot_grouped_bars(crosstab: pd.DataFrame,
                     var1_name: str = "Variable 1",
                     var2_name: str = "Variable 2",
                     title: Optional[str] = None,
                     figsize: Tuple[int, int] = (12, 6),
                     kind: str = 'grouped') -> plt.Figure:
    """
    Create grouped or stacked bar chart for two-way tabulation.
    
    Parameters
    ----------
    crosstab : DataFrame
        Crosstabulation table
    var1_name : str
        Name of first variable
    var2_name : str
        Name of second variable  
    title : str, optional
        Plot title
    figsize : tuple
        Figure size
    kind : str
        Type of bar chart ('grouped' or 'stacked')
        
    Returns
    -------
    Figure
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Remove Total rows/columns
    plot_data = crosstab.copy()
    if 'Total' in plot_data.index:
        plot_data = plot_data.drop('Total')
    if 'Total' in plot_data.columns:
        plot_data = plot_data.drop('Total', axis=1)
    
    # Create bar chart
    if kind == 'grouped':
        plot_data.plot(kind='bar', ax=ax, width=0.8)
    else:  # stacked
        plot_data.plot(kind='bar', stacked=True, ax=ax, width=0.8)
    
    # Customize appearance
    ax.set_xlabel(var1_name)
    ax.set_ylabel('Frequency')
    ax.set_title(title or f'{var1_name} by {var2_name}')
    ax.legend(title=var2_name, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Rotate x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_association_measures(statistics: Dict[str, Any],
                             figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Create visualization of association measures.
    
    Parameters
    ----------
    statistics : dict
        Dictionary of statistical results
    figsize : tuple
        Figure size
        
    Returns
    -------
    Figure
        Matplotlib figure object
    """
    # Extract association measures
    measures = {}
    
    if 'cramers_v' in statistics:
        measures["Cramér's V"] = statistics['cramers_v']
    
    if 'gamma' in statistics and isinstance(statistics['gamma'], dict):
        measures["Gamma"] = statistics['gamma'].get('statistic', np.nan)
    
    if 'taub' in statistics and isinstance(statistics['taub'], dict):
        measures["Kendall's τb"] = statistics['taub'].get('statistic', np.nan)
    
    if not measures:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, 'No association measures available', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Association Measures')
        return fig
    
    # Create bar chart of measures
    fig, ax = plt.subplots(figsize=figsize)
    
    names = list(measures.keys())
    values = list(measures.values())
    
    bars = ax.bar(names, values)
    
    # Color bars based on strength of association
    for bar, value in zip(bars, values):
        if abs(value) < 0.1:
            bar.set_color('lightblue')
        elif abs(value) < 0.3:
            bar.set_color('orange') 
        else:
            bar.set_color('red')
    
    ax.set_ylabel('Measure Value')
    ax.set_title('Measures of Association')
    ax.set_ylim(-1, 1)
    
    # Add horizontal line at 0
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.02 * np.sign(height),
                f'{value:.3f}', ha='center', va='bottom' if height >= 0 else 'top')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig


def create_tabulation_plots(result, plot_type: str = 'auto', **kwargs) -> plt.Figure:
    """
    Create plots from tabulation results.
    
    Parameters
    ----------
    result : TabulationResult
        Tabulation result object
    plot_type : str
        Type of plot ('auto', 'bar', 'heatmap', 'grouped', 'stacked', 'association')
    **kwargs : dict
        Additional plotting arguments
        
    Returns
    -------
    Figure
        Matplotlib figure object
    """
    table = result.table
    options = result.options
    statistics = result.statistics
    
    # Determine appropriate plot type
    if plot_type == 'auto':
        if len(table.index) <= 1 or len(table.columns) <= 1:
            plot_type = 'bar'
        elif statistics:
            plot_type = 'heatmap'
        else:
            plot_type = 'bar'
    
    # Extract variable names
    var1_name = options.get('variable1_label', 'Variable 1')
    var2_name = options.get('variable2_label', 'Variable 2')
    
    if plot_type == 'bar':
        return plot_oneway_frequencies(table, var1_name, **kwargs)
    elif plot_type == 'heatmap':
        return plot_twoway_heatmap(table, var1_name, var2_name, **kwargs)
    elif plot_type in ['grouped', 'stacked']:
        return plot_grouped_bars(table, var1_name, var2_name, kind=plot_type, **kwargs)
    elif plot_type == 'association':
        return plot_association_measures(statistics, **kwargs)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")


def save_plot(fig: plt.Figure, filename: str, dpi: int = 300, **kwargs):
    """
    Save plot to file.
    
    Parameters
    ----------
    fig : Figure
        Matplotlib figure
    filename : str
        Output filename
    dpi : int
        Resolution for raster formats
    **kwargs : dict
        Additional arguments for savefig
    """
    fig.savefig(filename, dpi=dpi, bbox_inches='tight', **kwargs)
    print(f"Plot saved to {filename}")
