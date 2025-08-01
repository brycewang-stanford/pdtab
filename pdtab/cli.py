#!/usr/bin/env python3
"""
Command-line interface for pdtab
Usage: pdtab-cli --help
"""

import argparse
import sys
import pandas as pd
import pdtab

def main():
    parser = argparse.ArgumentParser(
        description='pdtab: Command-line tabulation tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdtab-cli data.csv gender                    # One-way table
  pdtab-cli data.csv treatment outcome --chi2  # Two-way with chi-square
  pdtab-cli data.csv gender --summarize income # Summary statistics
  pdtab-cli --tabi "45 25 \\ 35 55" --exact   # Immediate tabulation
        """
    )
    
    # Input options
    parser.add_argument('file', nargs='?', help='CSV file to analyze')
    parser.add_argument('var1', nargs='?', help='First variable (row variable)')
    parser.add_argument('var2', nargs='?', help='Second variable (column variable)')
    
    # Analysis options
    parser.add_argument('--summarize', help='Variable to summarize')
    parser.add_argument('--weights', help='Weight variable')
    parser.add_argument('--tabi', help='Immediate tabulation from string/matrix')
    
    # Output options
    parser.add_argument('--row', action='store_true', help='Show row percentages')
    parser.add_argument('--column', action='store_true', help='Show column percentages')
    parser.add_argument('--cell', action='store_true', help='Show cell percentages')
    parser.add_argument('--nofreq', action='store_true', help='Suppress frequencies')
    parser.add_argument('--missing', action='store_true', help='Include missing values')
    parser.add_argument('--sort', action='store_true', help='Sort by frequency')
    
    # Statistical tests
    parser.add_argument('--chi2', action='store_true', help='Chi-square test')
    parser.add_argument('--exact', action='store_true', help='Fisher\'s exact test')
    parser.add_argument('--lrchi2', action='store_true', help='Likelihood-ratio chi-square')
    parser.add_argument('--V', action='store_true', help='Cramér\'s V')
    parser.add_argument('--gamma', action='store_true', help='Goodman-Kruskal gamma')
    parser.add_argument('--taub', action='store_true', help='Kendall\'s tau-b')
    
    # Multiple tables
    parser.add_argument('--tab1', nargs='+', help='Multiple one-way tables')
    parser.add_argument('--tab2', nargs='+', help='Multiple two-way tables')
    
    # Output format
    parser.add_argument('--format', choices=['text', 'html', 'csv'], 
                       default='text', help='Output format')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    try:
        # Handle immediate tabulation
        if args.tabi:
            result = pdtab.tabi(
                args.tabi,
                chi2=args.chi2,
                exact=args.exact,
                lrchi2=args.lrchi2,
                V=args.V,
                gamma=args.gamma,
                taub=args.taub
            )
            print_result(result, args)
            return
        
        # Check for required file input
        if not args.file:
            parser.error("CSV file is required (unless using --tabi)")
        
        # Load data
        try:
            df = pd.read_csv(args.file)
        except Exception as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Handle multiple tables
        if args.tab1:
            results = pdtab.tab1(args.tab1, data=df)
            for var, result in results.items():
                print(f"\n{var.upper()}:")
                print_result(result, args)
            return
            
        if args.tab2:
            results = pdtab.tab2(
                args.tab2, 
                data=df,
                chi2=args.chi2,
                exact=args.exact,
                lrchi2=args.lrchi2,
                V=args.V,
                gamma=args.gamma,
                taub=args.taub
            )
            for (var1, var2), result in results.items():
                print(f"\n{var1.upper()} × {var2.upper()}:")
                print_result(result, args)
            return
        
        # Check for required variables
        if not args.var1:
            parser.error("At least one variable is required")
        
        # Single tabulation
        result = pdtab.tabulate(
            args.var1,
            args.var2,
            data=df,
            summarize=args.summarize,
            weights=args.weights,
            row=args.row,
            column=args.column,
            cell=args.cell,
            nofreq=args.nofreq,
            missing=args.missing,
            sort=args.sort,
            chi2=args.chi2,
            exact=args.exact,
            lrchi2=args.lrchi2,
            V=args.V,
            gamma=args.gamma,
            taub=args.taub
        )
        
        print_result(result, args)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def print_result(result, args):
    """Print result in specified format"""
    
    if args.format == 'html':
        output = result.to_html()
    elif args.format == 'csv':
        output = result.to_csv()
    else:  # text
        output = str(result)
    
    # Add statistical results if available
    if hasattr(result, 'statistics') and result.statistics:
        if args.format == 'text':
            output += "\n\nStatistical Tests:"
            for test_name, test_result in result.statistics.items():
                if isinstance(test_result, dict):
                    if 'statistic' in test_result and 'p_value' in test_result:
                        output += f"\n{test_name}: {test_result['statistic']:.4f} (p = {test_result['p_value']:.4f})"
                    elif 'p_value' in test_result:
                        output += f"\n{test_name}: p = {test_result['p_value']:.4f}"
                else:
                    output += f"\n{test_name}: {test_result:.4f}"
    
    # Output to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Output written to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
