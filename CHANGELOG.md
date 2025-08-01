# Changelog

All notable changes to pdtab will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-08-01

### Fixed
- Fixed README badges display issues
- Corrected repository URLs throughout documentation
- Improved installation and development setup instructions

### Removed
- Command-line interface (`pdtab-cli`) for simplified package design

### Changed
- Enhanced badge display with reliable shields.io alternatives
- Updated documentation to focus on Python API usage

## [0.1.0] - 2025-08-01 - Initial Release

### Added
- Initial release of pdtab library
- Complete implementation of Stata's tabulate functionality
- One-way frequency tabulation with `OneWayTabulator` class
- Two-way cross-tabulation with `TwoWayTabulator` class
- Summary tabulation for continuous variables with `SummarizeTabulator` class
- Immediate tabulation from raw data with `ImmediateTabulator` class
- Comprehensive statistical testing suite:
  - Pearson's chi-square test
  - Likelihood-ratio chi-square test
  - Fisher's exact test
  - Cramér's V coefficient
  - Goodman and Kruskal's gamma
  - Kendall's tau-b
- Association measures and effect size calculations
- Weighted analysis support for complex sampling designs
- Multiple table generation with `tab1()` and `tab2()` functions
- Data processing utilities for validation and preprocessing
- Visualization module with matplotlib/seaborn integration
- Export capabilities (HTML, CSV, dictionary formats)
- Comprehensive documentation and examples
- Tutorial notebook with real-world scenarios
- Quick start guide for immediate productivity

### Features
- **Main API Functions:**
  - `tabulate()` - Main tabulation function
  - `tab1()` - Multiple one-way tables
  - `tab2()` - Multiple two-way tables  
  - `tabi()` - Immediate tabulation from raw counts

- **Statistical Analysis:**
  - Independence testing with multiple methods
  - Association strength measurement
  - Effect size calculation and interpretation
  - Exact tests for small samples
  - Robust handling of edge cases

- **Data Handling:**
  - Missing value treatment options
  - Weighted analysis capabilities
  - Categorical data preprocessing
  - Input validation and error handling

- **Output Options:**
  - Flexible percentage displays (row, column, cell)
  - Sortable frequency tables
  - Professional formatting for publications
  - Multiple export formats

- **Visualization:**
  - Bar charts for one-way tables
  - Heatmaps for two-way tables
  - Association measure plots
  - Publication-ready graphics

### Dependencies
- pandas >= 1.0.0
- numpy >= 1.18.0
- scipy >= 1.4.0
- matplotlib >= 3.1.0 (optional, for visualization)
- seaborn >= 0.10.0 (optional, for advanced plots)

### Documentation
- Complete API reference
- Tutorial notebook with 50+ examples
- Quick start guide
- Stata comparison table
- Real-world use cases

### Performance
- Optimized for large datasets
- Memory-efficient implementations
- Vectorized operations using pandas/numpy
- Fast statistical computations with scipy

### Compatibility
- Python 3.8+
- Cross-platform support (Windows, macOS, Linux)
- Jupyter notebook integration
- Command-line interface

### Testing
- Comprehensive test suite
- Edge case validation
- Statistical accuracy verification
- Example-based testing

## [Unreleased]

### Planned Features
- Additional statistical tests (McNemar's test, Cochran's Q)
- More visualization options
- Integration with other statistical packages
- Performance optimizations
- Extended documentation

### Known Issues
- None currently reported

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
