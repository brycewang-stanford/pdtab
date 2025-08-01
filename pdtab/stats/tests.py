"""
Statistical Tests and Measures for pdtab
========================================

This module implements statistical tests and measures of association 
used in tabulation analysis, including chi-square tests, Fisher's exact test,
and various measures of association.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import comb
from typing import Tuple, Optional, Dict, Any
import warnings


def pearson_chi2(observed: np.ndarray) -> Tuple[float, float, int]:
    """
    Compute Pearson's chi-square test for independence.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    tuple
        (chi2_statistic, p_value, degrees_of_freedom)
    """
    observed = np.asarray(observed)
    
    # Calculate expected frequencies
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    total = observed.sum()
    
    expected = np.outer(row_totals, col_totals) / total
    
    # Avoid division by zero
    mask = expected > 0
    chi2_stat = ((observed - expected) ** 2 / expected)[mask].sum()
    
    # Degrees of freedom
    df = (observed.shape[0] - 1) * (observed.shape[1] - 1)
    
    # P-value
    p_value = 1 - stats.chi2.cdf(chi2_stat, df)
    
    return chi2_stat, p_value, df


def likelihood_ratio_chi2(observed: np.ndarray) -> Tuple[float, float, int]:
    """
    Compute likelihood-ratio chi-square test.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    tuple
        (lr_chi2_statistic, p_value, degrees_of_freedom)
    """
    observed = np.asarray(observed)
    
    # Calculate expected frequencies
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0) 
    total = observed.sum()
    
    expected = np.outer(row_totals, col_totals) / total
    
    # Likelihood ratio statistic
    # G^2 = 2 * sum(observed * ln(observed/expected))
    mask = (observed > 0) & (expected > 0)
    lr_stat = 2 * (observed[mask] * np.log(observed[mask] / expected[mask])).sum()
    
    # Degrees of freedom
    df = (observed.shape[0] - 1) * (observed.shape[1] - 1)
    
    # P-value
    p_value = 1 - stats.chi2.cdf(lr_stat, df)
    
    return lr_stat, p_value, df


def fisher_exact_test(observed: np.ndarray) -> Dict[str, float]:
    """
    Compute Fisher's exact test.
    
    For 2x2 tables, provides both one-sided and two-sided p-values.
    For larger tables, provides an approximate p-value.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    dict
        Dictionary with p-values and other statistics
    """
    observed = np.asarray(observed)
    
    if observed.shape == (2, 2):
        # Standard 2x2 Fisher's exact test
        odds_ratio, p_value = stats.fisher_exact(observed, alternative='two-sided')
        _, p_value_one_sided = stats.fisher_exact(observed, alternative='greater')
        
        return {
            'p_value': p_value,
            'p_value_one_sided': p_value_one_sided,
            'odds_ratio': odds_ratio
        }
    else:
        # For r x c tables, use chi2_contingency with Monte Carlo simulation
        # This is an approximation since exact Fisher's test for r x c is computationally intensive
        try:
            _, p_value, _, _ = stats.chi2_contingency(observed)
            warnings.warn("Fisher's exact test for r×c tables uses chi-square approximation")
            return {'p_value': p_value}
        except Exception:
            return {'p_value': np.nan}


def cramers_v(observed: np.ndarray) -> float:
    """
    Compute Cramér's V measure of association.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    float
        Cramér's V statistic
    """
    observed = np.asarray(observed)
    
    if observed.shape == (2, 2):
        # For 2x2 tables, use the signed version
        n11, n12 = observed[0, :]
        n21, n22 = observed[1, :]
        
        n1_dot = n11 + n12
        n2_dot = n21 + n22  
        n_dot1 = n11 + n21
        n_dot2 = n12 + n22
        n = observed.sum()
        
        numerator = n11 * n22 - n12 * n21
        denominator = np.sqrt(n1_dot * n2_dot * n_dot1 * n_dot2)
        
        if denominator == 0:
            return 0.0
            
        return numerator / denominator
    else:
        # For larger tables, use standard Cramér's V
        chi2_stat, _, _ = pearson_chi2(observed)
        n = observed.sum()
        min_dim = min(observed.shape[0] - 1, observed.shape[1] - 1)
        
        if n == 0 or min_dim == 0:
            return 0.0
            
        return np.sqrt(chi2_stat / (n * min_dim))


def goodman_kruskal_gamma(observed: np.ndarray) -> Tuple[float, float]:
    """
    Compute Goodman and Kruskal's gamma with asymptotic standard error.
    
    Gamma is appropriate only when both variables are ordinal.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    tuple
        (gamma, asymptotic_standard_error)
    """
    observed = np.asarray(observed)
    
    # Calculate concordant and discordant pairs
    concordant = 0
    discordant = 0
    
    rows, cols = observed.shape
    
    for i in range(rows):
        for j in range(cols):
            nij = observed[i, j]
            
            # Count concordant pairs (both variables increase together)
            for k in range(i + 1, rows):
                for l in range(j + 1, cols):
                    concordant += nij * observed[k, l]
                    
            # Count discordant pairs (one increases, other decreases)
            for k in range(i + 1, rows):
                for l in range(j):
                    discordant += nij * observed[k, l]
    
    # Double the counts (since we only counted each pair once)
    P = 2 * concordant
    Q = 2 * discordant
    
    if P + Q == 0:
        return 0.0, 0.0
        
    gamma = (P - Q) / (P + Q)
    
    # Asymptotic variance calculation (simplified)
    # Full calculation would require more complex sums
    n = observed.sum()
    if n > 0 and (P + Q) > 0:
        # Approximate standard error
        ase = np.sqrt(16 * n / ((P + Q) ** 2))
    else:
        ase = 0.0
    
    return gamma, ase


def kendall_tau_b(observed: np.ndarray) -> Tuple[float, float]:
    """
    Compute Kendall's tau-b with asymptotic standard error.
    
    Tau-b is appropriate only when both variables are ordinal.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    tuple
        (tau_b, asymptotic_standard_error)
    """
    observed = np.asarray(observed)
    
    # Calculate concordant and discordant pairs (same as gamma)
    concordant = 0
    discordant = 0
    
    rows, cols = observed.shape
    
    for i in range(rows):
        for j in range(cols):
            nij = observed[i, j]
            
            # Count concordant pairs
            for k in range(i + 1, rows):
                for l in range(j + 1, cols):
                    concordant += nij * observed[k, l]
                    
            # Count discordant pairs  
            for k in range(i + 1, rows):
                for l in range(j):
                    discordant += nij * observed[k, l]
    
    P = 2 * concordant
    Q = 2 * discordant
    
    # Calculate ties
    n = observed.sum()
    row_ties = sum((observed.sum(axis=1) ** 2).sum()) - n
    col_ties = sum((observed.sum(axis=0) ** 2).sum()) - n
    
    # Tau-b calculation
    denominator = np.sqrt((n**2 - row_ties) * (n**2 - col_ties))
    
    if denominator == 0:
        return 0.0, 0.0
        
    tau_b = (P - Q) / denominator
    
    # Approximate asymptotic standard error
    if n > 0:
        ase = np.sqrt(4 * n / (9 * (n - 1)))
    else:
        ase = 0.0
    
    return tau_b, ase


def cell_contributions_chi2(observed: np.ndarray) -> np.ndarray:
    """
    Compute each cell's contribution to Pearson's chi-square.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    ndarray
        Array of cell contributions to chi-square
    """
    observed = np.asarray(observed)
    
    # Calculate expected frequencies
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    total = observed.sum()
    
    expected = np.outer(row_totals, col_totals) / total
    
    # Cell contributions
    contributions = (observed - expected) ** 2 / expected
    
    # Handle division by zero
    contributions[expected == 0] = 0
    
    return contributions


def cell_contributions_lr_chi2(observed: np.ndarray) -> np.ndarray:
    """
    Compute each cell's contribution to likelihood-ratio chi-square.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    ndarray
        Array of cell contributions to LR chi-square
    """
    observed = np.asarray(observed)
    
    # Calculate expected frequencies
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    total = observed.sum()
    
    expected = np.outer(row_totals, col_totals) / total
    
    # LR contributions: 2 * observed * ln(observed/expected)
    contributions = np.zeros_like(observed, dtype=float)
    
    mask = (observed > 0) & (expected > 0)
    contributions[mask] = 2 * observed[mask] * np.log(observed[mask] / expected[mask])
    
    return contributions


def expected_frequencies(observed: np.ndarray) -> np.ndarray:
    """
    Compute expected frequencies under independence assumption.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
        
    Returns
    -------
    ndarray
        Expected frequencies
    """
    observed = np.asarray(observed)
    
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    total = observed.sum()
    
    expected = np.outer(row_totals, col_totals) / total
    
    return expected


def run_all_tests(observed: np.ndarray, 
                  chi2: bool = False,
                  exact: bool = False,
                  lrchi2: bool = False,
                  V: bool = False,
                  gamma: bool = False,
                  taub: bool = False) -> Dict[str, Any]:
    """
    Run multiple statistical tests on a contingency table.
    
    Parameters
    ----------
    observed : array-like
        Observed frequencies in contingency table
    chi2 : bool
        Run Pearson's chi-square test
    exact : bool
        Run Fisher's exact test
    lrchi2 : bool
        Run likelihood-ratio chi-square test
    V : bool
        Compute Cramér's V
    gamma : bool
        Compute Goodman and Kruskal's gamma
    taub : bool
        Compute Kendall's tau-b
        
    Returns
    -------
    dict
        Dictionary containing all requested test results
    """
    results = {}
    observed = np.asarray(observed)
    
    if chi2:
        chi2_stat, chi2_p, chi2_df = pearson_chi2(observed)
        results['chi2'] = {
            'statistic': chi2_stat,
            'p_value': chi2_p,
            'df': chi2_df
        }
    
    if exact:
        fisher_results = fisher_exact_test(observed)
        results['exact'] = fisher_results
    
    if lrchi2:
        lr_stat, lr_p, lr_df = likelihood_ratio_chi2(observed)
        results['lrchi2'] = {
            'statistic': lr_stat,
            'p_value': lr_p,
            'df': lr_df
        }
    
    if V:
        cramers_v_stat = cramers_v(observed)
        results['cramers_v'] = cramers_v_stat
    
    if gamma:
        gamma_stat, gamma_ase = goodman_kruskal_gamma(observed)
        results['gamma'] = {
            'statistic': gamma_stat,
            'ase': gamma_ase
        }
    
    if taub:
        taub_stat, taub_ase = kendall_tau_b(observed)
        results['taub'] = {
            'statistic': taub_stat,
            'ase': taub_ase
        }
    
    return results
