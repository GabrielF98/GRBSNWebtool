"""
Can be used to fix problmes with the databases.
"""

import pandas as pd


def remove_columns_and_save(file_path, columns_to_remove):
    try:
        # Read data from the text file into a pandas DataFrame
        df = pd.read_csv(
            file_path, delimiter="\t"
        )  # Assuming the text file has tab-separated values (adjust delimiter if needed)

        # Check if the columns_to_remove exist in the DataFrame
        missing_columns = [col for col in columns_to_remove if col not in df.columns]
        if missing_columns:
            print(f"Columns {missing_columns} not found in the file.")
            return

        # Remove the specified columns from the DataFrame
        df.drop(columns_to_remove, axis=1, inplace=True)

        # Write the modified DataFrame to a temporary file
        temp_file_path = file_path + ".temp"
        df.to_csv(
            temp_file_path, sep="\t", index=False
        )  # Adjust the delimiter as per your requirement

        # Replace the original file with the temporary file
        import os

        os.replace(temp_file_path, file_path)

        print(f"Columns {columns_to_remove} removed and file updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
if __name__ == "__main__":
    file_path = ""  # Replace with the path to your text file
    columns_to_remove = [
        "time",
        "dtime",
        "time_unit",
    ]  # Replace with the names of the columns you want to remove
    remove_columns_and_save(file_path, columns_to_remove)
