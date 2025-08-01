# pdtab: Pandas-based Tabulation Library

[![PyPI version](https://badge.fury.io/py/pdtab.svg)](https://badge.fury.io/py/pdtab)
[![Downloads](https://static.pepy.tech/badge/pdtab)](https://pepy.tech/project/pdtab)
[![Downloads](https://static.pepy.tech/badge/pdtab/month)](https://pepy.tech/project/pdtab)
[![Downloads](https://static.pepy.tech/badge/pdtab/week)](https://pepy.tech/project/pdtab)
[![Python Versions](https://img.shields.io/pypi/pyversions/pdtab.svg)](https://pypi.org/project/pdtab/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/brycewang-stanford/pdtab.svg?style=social&label=Star)](https://github.com/brycewang-stanford/pdtab)

**pdtab** is a comprehensive Python library that replicates the functionality of Stata's `tabulate` command using pandas as the backend. This library provides powerful one-way, two-way, and summary tabulations with statistical tests and measures of association.

##  Overview

Stata's `tabulate` command is one of the most widely used tools for creating frequency tables and cross-tabulations in statistical analysis. **pdtab** brings this functionality to Python, offering:

- **Complete Stata compatibility**: Replicates all major features of Stata's tabulate command
- **Statistical tests**: Chi-square tests, Fisher's exact test, likelihood-ratio tests
- **Association measures**: Cramér's V, Goodman and Kruskal's gamma, Kendall's τb
- **Flexible output**: Console tables, HTML, and visualization options
- **Weighted analysis**: Support for frequency, analytic, and importance weights
- **Missing value handling**: Comprehensive options for dealing with missing data

##  Integration with Broader Ecosystem

**pdtab** is part of a comprehensive econometric and statistical analysis ecosystem:

### [PyStataR](https://github.com/brycewang-stanford/PyStataR)
The **pdtab** library will be integrated into **PyStataR**, a comprehensive Python package that bridges Stata and R functionality in Python. PyStataR aims to provide Stata users with familiar commands and workflows while leveraging Python's powerful data science ecosystem.

### [StasPAI](https://github.com/brycewang-stanford/StasPAI)
For users interested in AI-powered econometric analysis, **StasPAI** offers a related project focused on integrating statistical analysis with artificial intelligence methods. StasPAI provides advanced econometric modeling capabilities enhanced by machine learning approaches.

These projects together form a unified toolkit for modern econometric analysis, combining the best of Stata's user-friendly interface, R's statistical capabilities, and Python's machine learning ecosystem.

##  Installation

```bash
pip install pdtab
```

Or install from source:

```bash
git clone https://github.com/pdtab/pdtab.git
cd pdtab
pip install -e .
```

## Requirements

- Python 3.8+
- pandas >= 1.0.0
- numpy >= 1.18.0
- scipy >= 1.4.0
- matplotlib >= 3.0.0 (for plotting)
- seaborn >= 0.11.0 (for enhanced plotting)

## Quick Start

### Basic One-way Tabulation

```python
import pandas as pd
import pdtab

# Create sample data
data = pd.DataFrame({
    'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
    'education': ['High School', 'College', 'Graduate', 'High School', 'College', 'Graduate'],
    'income': [35000, 45000, 75000, 40000, 55000, 80000]
})

# One-way frequency table
result = pdtab.tabulate('gender', data=data)
print(result)
```

```
gender      Freq    Percent    Cum
Male          3      50.00   50.00
Female        3      50.00  100.00
Total         6     100.00  100.00
```

### Two-way Cross-tabulation with Statistics

```python
# Two-way table with chi-square test
result = pdtab.tabulate('gender', 'education', data=data, chi2=True, exact=True)
print(result)
```

### Summary Tabulation

```python
# Summary statistics by group
result = pdtab.tabulate('gender', data=data, summarize='income')
print(result)
```

```
Summary of income by gender

gender     Mean     Std. Dev.   Freq
Male     55000.0    20000.0      3
Female   55000.0    20000.0      3
Total    55000.0    18257.4      6
```

## Main Functions

### `tabulate(varname1, varname2=None, data=None, **options)`

Main tabulation function supporting:

**One-way options:**
- `missing=True`: Include missing values as a category
- `sort=True`: Sort by frequency (descending)
- `plot=True`: Create bar chart
- `nolabel=True`: Show numeric codes instead of labels
- `generate='prefix'`: Create indicator variables

**Two-way options:**
- `chi2=True`: Pearson's chi-square test
- `exact=True`: Fisher's exact test  
- `lrchi2=True`: Likelihood-ratio chi-square
- `V=True`: Cramér's V
- `gamma=True`: Goodman and Kruskal's gamma
- `taub=True`: Kendall's τb
- `row=True`: Row percentages
- `column=True`: Column percentages
- `cell=True`: Cell percentages
- `expected=True`: Expected frequencies

**Summary options:**
- `summarize='variable'`: Variable to summarize
- `means=False`: Suppress means
- `standard=False`: Suppress standard deviations
- `freq=False`: Suppress frequencies

### `tab1(varlist, data=None, **options)`

Create one-way tables for multiple variables:

```python
results = pdtab.tab1(['gender', 'education'], data=data)
for var, result in results.items():
    print(f"\n{var}:")
    print(result)
```

### `tab2(varlist, data=None, **options)`

Create all possible two-way tables:

```python
results = pdtab.tab2(['gender', 'education', 'region'], data=data, chi2=True)
for (var1, var2), result in results.items():
    print(f"\n{var1} × {var2}:")
    print(result)
```

### `tabi(table_data, **options)`

Immediate tabulation from supplied data:

```python
# From string (Stata format)
result = pdtab.tabi("30 18 \\ 38 14", exact=True)

# From list
result = pdtab.tabi([[30, 18], [38, 14]], chi2=True)
```

## Visualization

Create plots directly from tabulation results:

```python
# Bar chart for one-way table
result = pdtab.tabulate('gender', data=data, plot=True)

# Heatmap for two-way table  
result = pdtab.tabulate('gender', 'education', data=data)
fig = pdtab.viz.create_tabulation_plots(result, plot_type='heatmap')
```

## Statistical Tests

### Supported Tests

1. **Pearson's Chi-square Test**: Tests independence in contingency tables
2. **Likelihood-ratio Chi-square**: Alternative to Pearson's chi-square
3. **Fisher's Exact Test**: Exact test for small samples (especially 2×2 tables)

### Association Measures

1. **Cramér's V**: Measure of association (0-1 scale)
2. **Goodman and Kruskal's Gamma**: For ordinal variables (-1 to 1)
3. **Kendall's τb**: Rank correlation with tie correction (-1 to 1)

## Weighted Analysis

Support for different weight types:

```python
# Frequency weights
result = pdtab.tabulate('gender', data=data, weights='freq_weight')

# Analytic weights  
result = pdtab.tabulate('gender', data=data, weights='analytic_weight')
```

## Missing Value Handling

Flexible options for missing data:

```python
# Exclude missing values (default)
result = pdtab.tabulate('gender', data=data)

# Include missing as category
result = pdtab.tabulate('gender', data=data, missing=True)

# Subpopulation analysis
result = pdtab.tabulate('gender', data=data, subpop='analysis_sample')
```

## Export Options

Export results in multiple formats:

```python
result = pdtab.tabulate('gender', 'education', data=data)

# Export to dictionary
data_dict = result.to_dict()

# Export to HTML
html_table = result.to_html()

# Save plot
fig = pdtab.viz.create_tabulation_plots(result)
pdtab.viz.save_plot(fig, 'crosstab.png')
```

## Advanced Examples

### Complex Two-way Analysis

```python
# Comprehensive two-way analysis
result = pdtab.tabulate(
    'treatment', 'outcome', 
    data=clinical_data,
    chi2=True,           # Chi-square test
    exact=True,          # Fisher's exact test
    V=True,              # Cramér's V
    row=True,            # Row percentages
    expected=True,       # Expected frequencies
    missing=True         # Include missing values
)

print(result)
print(f"Chi-square: {result.statistics['chi2']['statistic']:.3f}")
print(f"p-value: {result.statistics['chi2']['p_value']:.3f}")
print(f"Cramér's V: {result.statistics['cramers_v']:.3f}")
```

### Summary Analysis by Multiple Groups

```python
# Income analysis by gender and education
result = pdtab.tabulate(
    'gender', 'education',
    data=data,
    summarize='income',
    means=True,
    standard=True,
    obs=True
)
```

### Immediate Analysis of Published Data

```python
# Analyze a 2×3 contingency table from literature
published_data = """
    45 55 60 \\
    30 40 35
"""

result = pdtab.tabi(published_data, chi2=True, exact=True, V=True)
print("Published data analysis:")
print(result)
```

## Stata Comparison

pdtab aims for 100% compatibility with Stata's tabulate command:

| Stata Command | pdtab Equivalent |
|---------------|------------------|
| `tabulate gender` | `pdtab.tabulate('gender', data=df)` |
| `tabulate gender education, chi2` | `pdtab.tabulate('gender', 'education', data=df, chi2=True)` |
| `tabulate gender, summarize(income)` | `pdtab.tabulate('gender', data=df, summarize='income')` |
| `tab1 gender education region` | `pdtab.tab1(['gender', 'education', 'region'], data=df)` |
| `tab2 gender education region` | `pdtab.tab2(['gender', 'education', 'region'], data=df)` |
| `tabi 30 18 \\ 38 14, exact` | `pdtab.tabi("30 18 \\\\ 38 14", exact=True)` |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/pdtab/pdtab.git
cd pdtab
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Stata Corporation** for the original tabulate command design
- **Pandas Development Team** for the excellent data manipulation library
- **SciPy Community** for statistical computing tools

## Related Projects

**pdtab** is part of a broader ecosystem of econometric and statistical tools:

- **[PyStataR](https://github.com/brycewang-stanford/PyStataR)** - Comprehensive Python package bridging Stata and R functionality (pdtab will be integrated into this project)
- **[StasPAI](https://github.com/brycewang-stanford/StasPAI)** - AI-powered econometric analysis toolkit combining statistical methods with machine learning

## Support

- **Documentation**: [https://pdtab.readthedocs.io](https://pdtab.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/pdtab/pdtab/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pdtab/pdtab/discussions)

---

**pdtab** - Bringing Stata's tabulation power to the Python ecosystem! 🐍
