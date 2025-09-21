"""
Maps DSPs to instances where they are in Curve
"""

import argparse
import logging
import os
import pandas as pd
from fastapi import FastAPI
from google.cloud import bigquery

from dsps import DSPS
from compare_vs_original_mapping import CompareMapping


_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()


########


def get_actuals_df():
    """
    Get all unqiue subSources from Recordings & Publishing sales tables from Curve
    """
    client = bigquery.Client(project="project")

    query = """
        SELECT DISTINCT subSource
        FROM `project.recording_dataset.recording_sales`

        UNION DISTINCT

        SELECT DISTINCT subSource 
        FROM `project.publishing_dataset.publishing_sales`
        """

    return client.query(query).to_dataframe()


def unique_sub_sources(key, value, actuals_df):
    """
    Based on list of DSPs in 'DSP' it gets unique values
    """
    output = []

    for val in value:
        dsp_unique = actuals_df.loc[
            actuals_df["subSource"].str.contains(
                val, case=False, regex=False, na=False
            ),
            "subSource",
        ].reset_index(drop=True)
        output.append(dsp_unique)

        all_dsps = pd.DataFrame(output)

        dsp_final = (
            pd.melt(all_dsps, ignore_index=True, value_name="subSource")
            .dropna()
            .drop(columns="variable")
            .drop_duplicates()
            .reset_index(drop=True)
        )

        dsp_final["dsp"] = str(key)

    return dsp_final


def building_dsp_mapping_table(dsps):
    """
    Iterate through DSP names and find where DSPs are mentioned
    """
    actuals_df = get_actuals_df()
    columns = ["subSource", "dsp"]
    dsp_mapping_table = pd.DataFrame(columns=columns)

    for dsp_key, dsp_values in dsps.items():
        dsp_output = unique_sub_sources(dsp_key, dsp_values, actuals_df)
        dsp_mapping_table = pd.concat(
            [dsp_mapping_table, dsp_output], ignore_index=True
        )

    return dsp_mapping_table.drop_duplicates()


def post_to_bigquery(df):
    """
    Post to BigQuery the new additions to DSP map
    """
    bigqueryclient = bigquery.Client(project="project")
    tableref = bigqueryclient.dataset("reference").table("dsp_mapping_table_bq_native")
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, autodetect=True
    )
    bigqueryjob = bigqueryclient.load_table_from_dataframe(
        df, tableref, job_config=job_config
    )
    bigqueryjob.result()


def main(post=False):
    """
    Main function to run DSP mapping
    """
    dsp_mapping_table = building_dsp_mapping_table(DSPS)

    # Compare the original DSP mapping to new DSP mappings that might be present
    mapping = CompareMapping(dsp_mapping_table)
    merged_final, original_mapping = mapping.run_compare_mapping()
    _logger.info("Changes %a", merged_final)

    # Isolate new mapping values
    new_values = dsp_mapping_table[
        ~dsp_mapping_table["subSource"].isin(original_mapping["subSource"])
    ]

    if new_values.empty:
        _logger.info(" No new values!")
    else:
        _logger.info(" New Values: %a", new_values)

    if post and not new_values.empty:
        _logger.info("Posting to BigQuery")
        post_to_bigquery(dsp_mapping_table)
        _logger.info("Post complete")


@app.get("/")
def run_from_web():
    """
    Function to run from web
    """
    post_mode = os.environ.get("POST_MODE", "0") == "1"
    main(post=post_mode)
    return {"message": f"DSP mapping completed. Post mode: {post_mode}"}


if __name__ == "__main__":

    port = os.environ.get("PORT", "8080")
    _logger.info(port)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--post",
        action=argparse.BooleanOptionalAction,
        help="Manually post to BQ",
        default=False,
    )

    args = parser.parse_args()
    main(post=args.post)
