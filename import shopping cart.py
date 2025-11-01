import csv
import io
import os
from typing import List, Tuple

# --- Configuration ---
# 1. Input File Name: Set this to the name of your text file.
INPUT_FILENAME = 'Shopping Cart.txt'
# 2. Output File Name: The CSV file to be created.
OUTPUT_FILENAME = 'shopping_cart_output.csv'
# ---------------------

def read_input_file(file_path: str) -> str:
    """Reads the content of the specified text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The input file '{file_path}' was not found.")
        # Exit the script if the file isn't found
        exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        exit(1)


def extract_table(lines: List[str], start_marker: str, end_marker: str) -> Tuple[List[str], List[str]]:
    """
    Extracts the header and data rows for a table between two marker strings.
    The first line after the start_marker is assumed to be the header.
    """
    try:
        # Find the start index of the table title
        start_index = lines.index(start_marker)
    except ValueError:
        return [], []

    try:
        # Find the end index of the section (which is the next table title or section)
        end_index = lines.index(end_marker, start_index)
    except ValueError:
        # If no end marker is found, assume it runs until the end of the list
        end_index = len(lines)

    # The line immediately after the table title is the header
    # We use a try-except block just in case the file is malformed and a header is missing
    try:
        header = lines[start_index + 1].strip()
    except IndexError:
        header = ""
    
    # Data rows start after the header and run up to the end marker
    # We only keep non-empty, non-header lines in this range
    data_rows = [line.strip() for line in lines[start_index + 2:end_index] if line.strip() and line.strip() != header]
    
    return header.split(','), data_rows

def extract_unstructured_data(lines: List[str], start_marker: str) -> str:
    """
    Extracts all lines after a specified start marker, cleans them, and joins them.
    """
    try:
        start_index = lines.index(start_marker)
        # Combine all subsequent non-empty lines, joining them with a space
        unstructured_content = ' '.join([
            line.strip() 
            for line in lines[start_index + 1:] 
            if line.strip()
        ])
        return unstructured_content
    except ValueError:
        return ""


def main():
    """
    Main function to orchestrate the data extraction from file and CSV writing.
    """
    # 1. Read the input file content
    input_content = read_input_file(INPUT_FILENAME)

    # Clean and split the input data into lines
    raw_lines = [line.strip() for line in input_content.splitlines()]
    clean_lines = [line for line in raw_lines if line] # Remove empty lines

    # Define markers for the sections
    T1_MARKER = "Table 1: Shopping Cart Items"
    T2_MARKER = "Table 2: Cart Summary"
    UNSTRUCTURED_MARKER = "Unstructured Data:"

    # --- 2. Extract Data for Each Table ---
    # Table 1: Itemized List (Ends at the start of Table 2)
    t1_header, t1_data_rows = extract_table(clean_lines, T1_MARKER, T2_MARKER)

    # Table 2: Summary (Ends at the start of Unstructured Data)
    t2_header, t2_data_rows = extract_table(clean_lines, T2_MARKER, UNSTRUCTURED_MARKER)

    # Unstructured Data (Starts after the marker, runs to the end)
    unstructured_content = extract_unstructured_data(clean_lines, UNSTRUCTURED_MARKER)

    # --- 3. Write Data to CSV File ---
    print(f"Writing parsed data to {OUTPUT_FILENAME}...")
    
    with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write Table 1
        writer.writerow([T1_MARKER])
        if t1_header:
            writer.writerow(t1_header)
        for row in t1_data_rows:
            # Use csv.reader to safely split comma-separated data, which handles embedded commas
            row_reader = csv.reader(io.StringIO(row))
            writer.writerow(next(row_reader))
        
        # Write separator
        writer.writerow([])
        writer.writerow(['---'])
        writer.writerow([])

        # Write Table 2
        writer.writerow([T2_MARKER])
        if t2_header:
            writer.writerow(t2_header)
        for row in t2_data_rows:
            writer.writerow(row.split(','))
            
        # Write separator
        writer.writerow([])
        writer.writerow(['---'])
        writer.writerow([])

        # Write Unstructured Data
        writer.writerow([UNSTRUCTURED_MARKER])
        writer.writerow(['Notes', 'Content'])
        writer.writerow(['', unstructured_content])

    print(f"Extraction complete. Data saved to {OUTPUT_FILENAME}.")

if __name__ == "__main__":
    main()