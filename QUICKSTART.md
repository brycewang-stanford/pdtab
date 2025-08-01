# pdtab Quick Start Guide

Get started with pdtab in 5 minutes! This guide shows you the most common use cases.

## Installation

```bash
pip install pdtab
```

## Basic Usage

```python
import pandas as pd
import pdtab

# Load your data
df = pd.read_csv('your_data.csv')

# One-way frequency table
pdtab.tabulate('gender', data=df)

# Two-way cross-tabulation
pdtab.tabulate('treatment', 'outcome', data=df)

# With statistical tests
pdtab.tabulate('treatment', 'outcome', data=df, chi2=True, exact=True)
```

## Common Patterns

### 1. Basic Frequency Analysis
```python
# Simple frequency table
result = pdtab.tabulate('category', data=df)
print(result)

# With sorting
result = pdtab.tabulate('category', data=df, sort=True)

# Include missing values
result = pdtab.tabulate('category', data=df, missing=True)
```

### 2. Cross-tabulation with Percentages
```python
# Row percentages
pdtab.tabulate('group', 'outcome', data=df, row=True)

# Column percentages  
pdtab.tabulate('group', 'outcome', data=df, column=True)

# Cell percentages
pdtab.tabulate('group', 'outcome', data=df, cell=True)
```

### 3. Statistical Testing
```python
# Chi-square test
result = pdtab.tabulate('treatment', 'response', data=df, chi2=True)
print(f"P-value: {result.statistics['chi2']['p_value']}")

# Fisher's exact test
result = pdtab.tabulate('treatment', 'response', data=df, exact=True)

# Multiple tests at once
result = pdtab.tabulate('group', 'outcome', data=df, 
                       chi2=True, exact=True, V=True)
```

### 4. Summary Statistics
```python
# Mean and std by group
pdtab.tabulate('gender', data=df, summarize='income')

# Two-way summary
pdtab.tabulate('gender', 'education', data=df, summarize='income')
```

### 5. Multiple Tables
```python
# Multiple one-way tables
results = pdtab.tab1(['var1', 'var2', 'var3'], data=df)

# All two-way combinations
results = pdtab.tab2(['var1', 'var2', 'var3'], data=df)
```

### 6. Immediate Tabulation
```python
# From raw counts (2x2 table)
pdtab.tabi("45 25 \\ 35 55", chi2=True)

# From matrix
pdtab.tabi([[30, 25], [20, 35]], exact=True)
```

## Quick Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `tabulate()` | Main tabulation function | `tabulate('var1', 'var2', data=df)` |
| `tab1()` | Multiple one-way tables | `tab1(['var1', 'var2'], data=df)` |
| `tab2()` | Multiple two-way tables | `tab2(['var1', 'var2'], data=df)` |
| `tabi()` | Immediate tabulation | `tabi("10 20 \\ 30 40")` |

## Key Options

| Option | Description | Example |
|--------|-------------|---------|
| `chi2=True` | Chi-square test | Statistical independence test |
| `exact=True` | Fisher's exact test | Exact p-values for small samples |
| `row=True` | Row percentages | Percentages within each row |
| `column=True` | Column percentages | Percentages within each column |
| `sort=True` | Sort by frequency | Order categories by count |
| `missing=True` | Include missing values | Show missing data in results |
| `weights='var'` | Weighted analysis | Use sampling weights |

## Real Example

```python
import pandas as pd
import pdtab

# Create sample data
data = {
    'treatment': ['A', 'B'] * 50,
    'outcome': ['Success', 'Failure'] * 50,
    'gender': ['Male', 'Female'] * 50
}
df = pd.DataFrame(data)

# Analysis
result = pdtab.tabulate('treatment', 'outcome', data=df, 
                       chi2=True, row=True)
print(result)

# Check significance
if result.statistics['chi2']['p_value'] < 0.05:
    print("Significant association found!")
```

## Next Steps

- Read the [full tutorial](tutorial.ipynb)
- Check the [complete documentation](README.md)
- Try with your own data!

Happy tabulating! 📊
