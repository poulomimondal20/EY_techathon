import pandas as pd
import os
import numpy as np


def get_file_size_mb(filepath):
    """Get file size in megabytes."""
    return os.path.getsize(filepath) / (1024 * 1024)


def sample_csv_under_size_limit(input_file, output_file, target_size_mb=90, random_state=42):
    """
    Randomly sample data from a CSV file to keep it under target size.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        target_size_mb (int): Target file size in MB (default 90MB)
        random_state (int): Random seed for reproducibility
    """
    
    print(f"Reading file: {input_file}")
    original_size = get_file_size_mb(input_file)
    print(f"Original file size: {original_size:.2f} MB")
    
    if original_size <= target_size_mb:
        print(f"File is already under {target_size_mb}MB. No sampling needed.")
        df = pd.read_csv(input_file)
        df.to_csv(output_file, index=False)
        return
    
    df = pd.read_csv(input_file)
    total_rows = len(df)
    print(f"Total rows in original file: {total_rows:,}")
    
    target_ratio = target_size_mb / original_size
    initial_sample_ratio = target_ratio * 0.95
    
    sample_size = int(total_rows * initial_sample_ratio)
    print(f"Initial sample size: {sample_size:,} rows ({initial_sample_ratio*100:.1f}% of data)")
    
    df_sampled = df.sample(n=sample_size, random_state=random_state)
    
    temp_file = output_file + '.tmp'
    df_sampled.to_csv(temp_file, index=False)
    
    sampled_size = get_file_size_mb(temp_file)
    print(f"Sampled file size: {sampled_size:.2f} MB")
    
    while sampled_size > target_size_mb and sample_size > 100:
        adjustment_ratio = (target_size_mb / sampled_size) * 0.95
        sample_size = int(sample_size * adjustment_ratio)
        print(f"Adjusting sample size to: {sample_size:,} rows")
        
        df_sampled = df.sample(n=sample_size, random_state=random_state)
        df_sampled.to_csv(temp_file, index=False)
        sampled_size = get_file_size_mb(temp_file)
        print(f"New sampled file size: {sampled_size:.2f} MB")
    
    os.rename(temp_file, output_file)
    
    print(f"\n✅ Sampling complete!")
    print(f"Final rows: {len(df_sampled):,} ({len(df_sampled)/total_rows*100:.1f}% of original)")
    print(f"Final file size: {sampled_size:.2f} MB")
    print(f"Output saved to: {output_file}")
    
    print("\nDataset statistics:")
    print(df_sampled.describe())
    
    return df_sampled


def stratified_sample_by_column(input_file, output_file, stratify_column, target_size_mb=90, random_state=42):
    """
    Stratified sampling to maintain distribution of a specific column.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        stratify_column (str): Column name to stratify by
        target_size_mb (int): Target file size in MB
        random_state (int): Random seed
    """
    
    print(f"Reading file: {input_file}")
    df = pd.read_csv(input_file)
    
    if stratify_column not in df.columns:
        print(f"Warning: Column '{stratify_column}' not found. Using random sampling instead.")
        return sample_csv_under_size_limit(input_file, output_file, target_size_mb, random_state)
    
    original_size = get_file_size_mb(input_file)
    total_rows = len(df)
    
    target_ratio = target_size_mb / original_size
    initial_sample_ratio = target_ratio * 0.95
    sample_size = int(total_rows * initial_sample_ratio)
    
    print(f"Performing stratified sampling on column: {stratify_column}")
    df_sampled = df.groupby(stratify_column, group_keys=False).apply(
        lambda x: x.sample(frac=initial_sample_ratio, random_state=random_state)
    )
    
    temp_file = output_file + '.tmp'
    df_sampled.to_csv(temp_file, index=False)
    sampled_size = get_file_size_mb(temp_file)
    
    while sampled_size > target_size_mb and len(df_sampled) > 100:
        adjustment_ratio = (target_size_mb / sampled_size) * 0.95
        
        df_sampled = df.groupby(stratify_column, group_keys=False).apply(
            lambda x: x.sample(frac=initial_sample_ratio * adjustment_ratio, random_state=random_state)
        )
        
        df_sampled.to_csv(temp_file, index=False)
        sampled_size = get_file_size_mb(temp_file)
    
    os.rename(temp_file, output_file)
    
    print(f"\n✅ Stratified sampling complete!")
    print(f"Final rows: {len(df_sampled):,}")
    print(f"Final file size: {sampled_size:.2f} MB")
    print(f"Output saved to: {output_file}")
    
    return df_sampled


if __name__ == "__main__":
    input_csv = "medicine_data.csv"
    output_csv = "medicine_data_sampled.csv"
    
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found in current directory!")
        print(f"Current directory: {os.getcwd()}")
        print("Please ensure medicine_data.csv is in the Datasets folder.")
    else:
        sampled_df = sample_csv_under_size_limit(
            input_file=input_csv,
            output_file=output_csv,
            target_size_mb=90,
            random_state=42
        )
        
        print("\nSample of the data:")
        print(sampled_df.head())
