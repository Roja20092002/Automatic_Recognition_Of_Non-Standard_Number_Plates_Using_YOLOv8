import csv
import os


def save_results(results):

    os.makedirs(
        "outputs/final",
        exist_ok=True
    )

    csv_path = "outputs/final/results.csv"

    with open(
        csv_path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Plate",
            "Confidence",
            "Valid"
        ])

        for result in results:

            writer.writerow([
                result["plate"],
                result["confidence"],
                result["valid"]
            ])

    return csv_path