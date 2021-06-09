import click
import json

from loguru import logger
from toolz import pluck


@click.command()
@click.argument("orig_file", type=click.File("r"))
@click.argument("updated_file", type=click.File("r"))
@click.argument("merged_file", type=click.File("w"))
def main(orig_file, updated_file, merged_file):

    logger.info(f"Loading updated reports from {updated_file.name}.")
    all_reports = list(map(json.loads, updated_file))
    all_report_links = set(pluck("report_link", all_reports))
    logger.info(f"Loaded {len(all_reports)} reports from {updated_file.name}.")

    logger.info(
        f"Gathering old reports from {orig_file.name} to add any older "
        "missing reports."
    )
    for report in map(json.loads, orig_file):
        if report["report_link"] not in all_report_links:
            all_reports.append(report)
            all_report_links.update(report["report_link"])

    logger.info(f"Writing {len(all_reports)} to {merged_file.name}.")
    for report in map(json.dumps, all_reports):
        merged_file.write(report + "\n")
    logger.info(" 🛸 Done 🛸 ")


if __name__ == "__main__":
    main()
