# pdtab v0.1.0 Release Notes

## 🎉 Initial Release

This is the initial release of **pdtab**, a comprehensive Python library that replicates Stata's `tabulate` command functionality using pandas as the backend.

## ✨ Key Features

### 📊 Core Tabulation
- **One-way tabulation**: Frequency tables with percentages and sorting
- **Two-way cross-tabulation**: Complete crosstab analysis with row/column/cell percentages
- **Summary tabulation**: Descriptive statistics by categorical groups
- **Immediate tabulation**: Direct analysis from raw count data

### 🔬 Statistical Analysis
- **Pearson's chi-square test**: Independence testing for contingency tables
- **Likelihood-ratio chi-square**: Alternative independence test
- **Fisher's exact test**: Exact p-values for small samples
- **Cramér's V**: Measure of association strength (0-1 scale)
- **Goodman-Kruskal Gamma**: Ordinal association measure (-1 to 1)
- **Kendall's τb**: Rank correlation with tie correction (-1 to 1)

### 🛠️ Advanced Features
- **Weighted analysis**: Full support for sampling weights
- **Missing value handling**: Flexible options for missing data treatment
- **Multiple table generation**: Batch processing with `tab1()` and `tab2()`
- **Command-line interface**: `pdtab-cli` for terminal usage
- **Visualization**: Integration with matplotlib/seaborn for publication-ready plots
- **Export options**: HTML, CSV, and dictionary formats

## 🆚 Stata Compatibility

pdtab provides 100% compatibility with Stata's tabulate command syntax:

| Stata Command | pdtab Equivalent |
|---------------|------------------|
| `tabulate var` | `pdtab.tabulate('var', data=df)` |
| `tabulate var1 var2, chi2` | `pdtab.tabulate('var1', 'var2', data=df, chi2=True)` |
| `tabulate var, summarize(income)` | `pdtab.tabulate('var', data=df, summarize='income')` |
| `tab1 var1 var2 var3` | `pdtab.tab1(['var1', 'var2', 'var3'], data=df)` |
| `tab2 var1 var2 var3` | `pdtab.tab2(['var1', 'var2', 'var3'], data=df)` |
| `tabi 30 18 \\ 38 14, exact` | `pdtab.tabi("30 18 \\\\ 38 14", exact=True)` |

## 🚀 Installation

```bash
pip install pdtab
```

## 📚 Documentation

- **README.md**: Complete API documentation with examples
- **QUICKSTART.md**: 5-minute getting started guide
- **tutorial.ipynb**: Comprehensive Jupyter notebook with 50+ examples
- **PUBLISHING_GUIDE.md**: Guide for package development and publishing

## 🔧 Requirements

- Python 3.8+
- pandas >= 1.0.0
- numpy >= 1.18.0
- scipy >= 1.4.0
- matplotlib >= 3.0.0 (optional, for visualization)
- seaborn >= 0.11.0 (optional, for enhanced plotting)

## 🌟 What's Next

pdtab is designed to be part of a larger econometric ecosystem:

- **Integration with PyStataR**: This library will be integrated into the comprehensive PyStataR package
- **Compatibility with StasPAI**: Works seamlessly with AI-powered econometric analysis tools

## 🤝 Contributing

We welcome contributions! This project uses modern Python development practices:

- **pyproject.toml**: Modern package configuration
- **Comprehensive testing**: Full test suite with edge case coverage
- **Type hints**: Complete type annotation for better IDE support
- **Documentation**: Extensive examples and use cases

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Stata Corporation** for the original tabulate command design
- **Pandas Development Team** for the excellent data manipulation foundation
- **SciPy Community** for statistical computing capabilities

---

**pdtab v0.1.0** - Bringing Stata's tabulation power to the Python ecosystem! 🐍📊
