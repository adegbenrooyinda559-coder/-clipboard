import csv
from datetime import datetime
import os
from pathlib import Path
import shutil

# Define directories
BASE_DIR = Path("./automation_workspace")
RAW_DIR = BASE_DIR / "raw_inputs"
PROCESSED_DIR = BASE_DIR / "processed_reports"
ARCHIVE_DIR = BASE_DIR / "archive"

# Ensure directories exist
for folder in [RAW_DIR, PROCESSED_DIR, ARCHIVE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


def log_action(message):
    """Appends an execution log with a timestamp."""
    log_path = BASE_DIR / "automation_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")


def organize_incoming_files():
    """Workflow 1: Sorts raw files into categorized folders."""
    log_action("Starting workflow: Organizing incoming files...")
    moved_count = 0

    for file_path in RAW_DIR.iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in [".csv", ".txt"]:
                target_folder = RAW_DIR / "documents"
            elif ext in [".png", ".jpg", ".pdf"]:
                target_folder = RAW_DIR / "media"
            else:
                target_folder = RAW_DIR / "misc"

            target_folder.mkdir(exist_ok=True)
            shutil.move(str(file_path), target_folder / file_path.name)
            moved_count += 1

    log_action(f"Completed workflow: Organized {moved_count} files.")


def process_sales_report(input_csv_name):
    """Workflow 2: Cleans raw CSV data, filters out invalid rows, and computes totals."""
    log_action(
        f"Starting workflow: Processing sales report ({input_csv_name})..."
    )
    input_path = RAW_DIR / "documents" / input_csv_name

    if not input_path.exists():
        log_action(f"Error: Input file {input_csv_name} not found.")
        return

    cleaned_rows = []
    total_revenue = 0.0

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean whitespace from fields
            cleaned_row = {k: v.strip() for k, v in row.items()}

            # Filter out rows with missing or zero quantities
            try:
                qty = int(cleaned_row.get("Quantity", 0))
                price = float(cleaned_row.get("UnitPrice", 0.0))
                if qty > 0 and price > 0:
                    line_total = qty * price
                    cleaned_row["Total"] = str(round(line_total, 2))
                    total_revenue += line_total
                    cleaned_rows.append(cleaned_row)
            except ValueError:
                continue  # Skip rows with malformed numeric data

    # Write processed output report
    output_filename = f"processed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output_path = PROCESSED_DIR / output_filename

    if cleaned_rows:
        fieldnames = list(cleaned_rows[0].keys())
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(writerows=cleaned_rows)

        log_action(
            f"Success: Generated report {output_filename} with total revenue: ${total_revenue:,.2f}"
        )

        # Archive the original raw file
        shutil.move(str(input_path), ARCHIVE_DIR / input_path.name)
    else:
        log_action("Warning: No valid records found to process.")


if __name__ == "__main__":
    log_action("--- Automation Suite Started ---")
    organize_incoming_files()
    # Example call for processing a report (ensure a sample file exists in RAW_DIR/documents first)
    # process_sales_report("sample_sales.csv")
    log_action("--- Automation Suite Finished ---")