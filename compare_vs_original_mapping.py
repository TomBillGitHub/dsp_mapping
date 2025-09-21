"""
Class for comparing originals vs mapping
"""

import pandas as pd
from google.cloud import bigquery


class CompareMapping:
    """
    Class to compare DSP mapping
    """

    def __init__(self, current_values):
        self.current_values = current_values

    def run_compare_mapping(self):
        """
        Function to run class
        """
        original_mapping = self.get_original_mapping_from_bq()
        original_values, current_values = self.get_current_unique_dsp_counts(
            original_mapping, self.current_values
        )

        merged = self.merged_original_and_current(original_values, current_values)
        merged_final = self.calculate_difference(merged)

        return merged_final, original_mapping

    def get_original_mapping_from_bq(self):
        """
        Function to retrieve BQ table of DSP mappings
        """
        client = bigquery.Client(project="bfm-sandbox")

        query = """
            SELECT 
                *
            FROM `project.reference.dsp_mapping_table_bq_native`
            """

        dsp_mapping_in_bq = client.query(query).to_dataframe()
        return dsp_mapping_in_bq

    def get_current_unique_dsp_counts(self, original_values, current_values):
        """
        Gets value counts of each unique DSP
        """
        current_values = pd.DataFrame(
            current_values["dsp"].value_counts()
        ).reset_index()
        original_values = pd.DataFrame(
            original_values["dsp"].value_counts()
        ).reset_index()

        return original_values, current_values

    def merged_original_and_current(self, original_values, current_values):
        """
        Merges original & new mappings to find differences
        """
        merged = pd.merge(
            original_values,
            current_values,
            how="outer",
            left_on="dsp",
            right_on="dsp",
            suffixes=["_original", "_current_new"],
        )

        return merged

    def calculate_difference(self, merged):
        """
        Calculates the difference by subtracting count of original mappings from current count
        """
        merged["difference"] = merged["count_current_new"] - merged["count_original"]
        merged_final = merged.sort_values(by="difference", ascending=False)

        return merged_final
