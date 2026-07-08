#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (Optional) PEP 723 inline script metadata for self-contained execution with `uv`.
# Remove or adjust if managing dependencies via a traditional virtual environment.
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas",
#     "loguru",
# ]
# ///

"""
Script Template for S. pombe Phenotype Processing
===================================================

A template script that demonstrates the standard layout for AI-generated
Python scripts in this workspace. Replace this description with the
script's actual business logic, core algorithm, and context.

Input
-----
- Input file path (CSV, TSV, or XLSX) with required columns.
- See ``--input`` / ``--help`` for exact format.

Output
------
- Filtered results saved to the configured output directory.
- File format depends on the script's core logic.

Usage
-----
    mamba run -n bioinformatics python script_name.py
    mamba run -n bioinformatics python script_name.py --input path/to/data.csv --verbose

Author:   [Name] (guidance) + [AI Agent] (implementation)
Date:     YYYY-MM-DD
Version:  1.0.0
"""

# =============================================================================
# IMPORTS
# =============================================================================
# 1. Standard Library Imports
import argparse
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

# 2. Data Processing Imports
import pandas as pd

# 3. Third-party Imports
from loguru import logger

# =============================================================================
# DECORATORS
# =============================================================================
# Use standard library decorators (e.g., @functools.cache, @contextlib.contextmanager) 
# freely. Create custom decorators only when they meaningfully simplify the script — 
# e.g., to eliminate repetitive boilerplate across multiple functions. 
# Do NOT create decorators just for the sake of having them.

# =============================================================================
# GLOBAL CONSTANTS & ENUMS
# =============================================================================
# Use StrEnum for fixed sets of closely related string markers (e.g., column names, 
# operation modes, strict categorical statuses) that you might want to switch 
# or pattern-match (match-case) against. Do NOT use StrEnum for truly single, 
# unrelated string constants (e.g., a single API URL or a regular regex pattern).
class DataCol(StrEnum):
    GENE_ID = "systematic_name"
    PHENOTYPE = "phenotype"
    PVALUE = "p_value"

# =============================================================================
# CONFIGURATION & DATACLASSES
# =============================================================================
# Set `frozen=True` if this config represents parameters that are set exactly once 
# at startup and should NEVER be modified during execution (the vast majority of cases). 
# Set `frozen=False` ONLY if the application explicitly requires hot-reloading 
# or dynamically mutating the configuration object state during runtime.
@dataclass(kw_only=True, slots=True, frozen=True)
class AppConfig:
    """Configuration for the script's runtime parameters."""
    input_path: Path
    output_dir: Path
    p_value_threshold: float
    keywords: list[str]

# =============================================================================
# LOGGING SETUP
# =============================================================================
def setup_logger(log_level: str = "INFO") -> None:
    """Configure the Loguru logger."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
        level=log_level
    )

setup_logger()

# =============================================================================
# CORE LOGIC (FUNCTIONS / CLASSES)
# =============================================================================
# Always use f-strings for string interpolation. Never use .format() or % formatting.
@logger.catch
def filter_dataframe(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Filter the Pandas DataFrame based on configured P-value thresholds and keywords."""
    # Guard clause: Return early if the dataframe is empty
    if df.empty:
        logger.warning("Received empty DataFrame. Skipping filtering.")
        return df

    logger.info(f"Initial raw data shape: {df.shape}")
    
    # Use StrEnum instead of hardcoded strings
    mask = df[DataCol.PVALUE] < config.p_value_threshold
    filtered_df = df.loc[mask].copy()
    
    logger.info(f"Data shape after p-value filtering: {filtered_df.shape}")
    return filtered_df

# =============================================================================
# MAIN EXECUTION
# =============================================================================
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments and return the populated namespace."""
    parser = argparse.ArgumentParser(description="Script template for processing phenotype DataFrames.")
    parser.add_argument("-i", "--input", type=Path, required=True, help="Input raw CSV path.")
    parser.add_argument("-o", "--outdir", type=Path, default=Path("./results"), help="Output directory.")
    parser.add_argument("-t", "--threshold", type=float, default=0.05, help="P-value threshold.")
    parser.add_argument("-k", "--keywords", type=str, nargs="+", required=True, help="Phenotype keywords.")
    parser.add_argument("--verbose", action="store_true", help="Enable DEBUG level logging.")
    return parser.parse_args()

def main() -> int:
    """Main orchestrator function for the script execution."""
    args = parse_args()
    
    # Configure logger based on CLI flag
    setup_logger(log_level="DEBUG" if args.verbose else "INFO")
    
    # Instantiate Config
    config = AppConfig(
        input_path=args.input.resolve(),
        output_dir=args.outdir.resolve(),
        p_value_threshold=args.threshold,
        keywords=args.keywords
    )
    
    # Prepare output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Execute core logic 
    logger.info(f"Starting processing for file: {config.input_path}")
    try:
        df_raw = pd.read_csv(config.input_path)
        df_filtered = filter_dataframe(df_raw, config)
        
        out_file = config.output_dir / "filtered_results.csv"
        df_filtered.to_csv(out_file, index=False)
        logger.info(f"Results successfully saved to {out_file} ({len(df_filtered):,} rows)")
        
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
