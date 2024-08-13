import pandas as pd
import os
import glob

def combine_csv_files_by_class(file_paths, sample_size_per_class, class_column, output_file):
    """
    Combine multiple CSV files by sampling a specified number of rows per class from each file.

    Parameters:
    - file_paths: List of file paths to the CSV files.
    - sample_size_per_class: Number of rows to sample per class from each file.
    - class_column: Name of the column containing the class labels.
    - output_file: Path to the output CSV file.

    Returns:
    - combined_df: DataFrame containing the combined and sampled data.
    """
    combined_df = pd.DataFrame()

    for file_path in file_paths:
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path)

        sampled_df = pd.DataFrame()
        
        for class_label in df['AttackerType'].unique():
            class_df = df[df['AttackerType'] != 0]
            if len(class_df) <= sample_size_per_class:
                sampled_class_df = class_df
            else:
                sampled_class_df = class_df.sample(n=sample_size_per_class, random_state=42)  # Use a seed for reproducibility
            
            sampled_df = pd.concat([sampled_df, sampled_class_df], ignore_index=True)
        
        combined_df = pd.concat([combined_df, sampled_df], ignore_index=True)

    combined_df.to_csv(output_file, index=False)
    print(f"Combined file saved to {output_file}")
    return combined_df

# Example usage:
# List of file paths to your CSV files
file_paths = glob.glob("./raw_datasets/training_datasets/Malfunctions/*.csv")
# Number of rows to sample per class from each file
sample_size_per_class = 13
# Name of the column containing the class labels
class_column = "class"
# Path to save the combined CSV file
output_file = "vehicles_400_2200.csv"

combined_df = combine_csv_files_by_class(file_paths, sample_size_per_class, class_column, output_file)
print("Combined DataFrame shape:", combined_df.shape)

