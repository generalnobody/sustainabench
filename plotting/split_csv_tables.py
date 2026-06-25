# Used to split the tables from the performance-per-carbon spreadsheet: https://docs.google.com/spreadsheets/d/1VI0vRGZW7mPM44MnEibJzmqFGFIJpWXt8OS7XAhwT8I/edit?usp=sharing

import os
import re
import pandas as pd


def sanitize_filename(text):
    """Make a safe filename."""
    text = str(text).strip()
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", "_", text)
    return text


def extract_and_save_tables(input_csv, output_dir="output_tables"):
    os.makedirs(output_dir, exist_ok=True)

    raw = pd.read_csv(
        input_csv,
        header=None,
        dtype=str,
        keep_default_na=False,
    )

    nrows, ncols = raw.shape
    saved = []

    r = 0
    while r < nrows:

        # A table-group starts with rows like:
        # Rome,Performance,,,,,,,Genoa,Performance,...
        # followed by:
        # Benchmark,Metric,...
        if r + 1 >= nrows:
            break

        c = 0
        while c < ncols - 1:

            title = str(raw.iat[r, c]).strip()
            category = str(raw.iat[r, c + 1]).strip()

            if not title or not category:
                c += 8
                continue

            # Verify header row exists
            if (
                str(raw.iat[r + 1, c]).strip().lower()
                != "benchmark"
            ):
                c += 8
                continue

            # Determine width of this table from header row
            width = 0
            cc = c
            while cc < ncols:
                value = str(raw.iat[r + 1, cc]).strip()

                if value == "":
                    break

                width += 1
                cc += 1

            if width == 0:
                c += 8
                continue

            headers = (
                raw.iloc[r + 1, c:c + width]
                .astype(str)
                .str.strip()
                .tolist()
            )

            # Read data rows until an empty row for this table
            data = []
            rr = r + 2

            while rr < nrows:

                row_slice = (
                    raw.iloc[rr, c:c + width]
                    .astype(str)
                    .str.strip()
                    .tolist()
                )

                if all(x == "" for x in row_slice):
                    break

                data.append(row_slice)
                rr += 1

            if data:
                df = pd.DataFrame(data, columns=headers)

                filename = (
                    f"{sanitize_filename(title)}__"
                    f"{sanitize_filename(category)}.csv"
                )

                path = os.path.join(output_dir, filename)

                df.to_csv(path, index=False)

                saved.append(path)

            c += 8

        r += 1

    print(f"Saved {len(saved)} tables:")
    for path in saved:
        print("  ", path)

    return saved


if __name__ == "__main__":
    output_dir="../experiments/plots/performance_per_carbon/"
    files = ["NL_2024_Tables.csv",
             "FR_2024_Tables.csv",
             "NL_2022_Tables.csv"]
    
    for file in files:
        extract_and_save_tables(
            input_csv=f"performance_per_carbon_tables/{file}",
            output_dir=f"{output_dir}/{file.split('.')[0]}",
        )
