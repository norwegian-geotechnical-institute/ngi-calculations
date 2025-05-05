import pandas as pd
from tests.data.calculation_data import ExcelDataConfig
from tests.data.excel_data_column_mapping import CptRawColumns

from ngi_calculations.cpt_correlations.methods.cpt_process.calculations import CPTProcessCalculation
from ngi_calculations.cpt_correlations.methods.cpt_process.options import CptProcessOptions
from ngi_calculations.cpt_correlations.models.cpt_cone import CptCone
from ngi_calculations.cpt_correlations.models.cpt_raw import RawCPT
from ngi_calculations.cpt_correlations.models.lab_data import LabData


def import_raw_cpt_from_excel(file_path, file_config: ExcelDataConfig) -> pd.DataFrame:
    return pd.read_excel(
        file_path,
        sheet_name=file_config.sheetname,
        header=[file_config.header_row - 1],
        usecols=f"{file_config.start_column}:{file_config.end_column}",
        skiprows=[0, 2],
        nrows=file_config.data_end_row - file_config.data_start_row + 1,
    )


if __name__ == "__main__":
    # ── raw cpt data ──────────────────────────────────────────────────────
    # import the raw cpt data from an excel file. You can provide directly the cpt as dataframe
    raw_cpt_config = ExcelDataConfig(
        sheetname="cpt_raw",
        start_column="A",
        end_column="I",
        header_row=1,
        data_start_row=5,
        data_end_row=439,
        column_mapping=CptRawColumns().columns,
    )

    raw_cpt_df = import_raw_cpt_from_excel("tests/data/calculations/testA.xlsx", raw_cpt_config)
    raw_cpt = RawCPT(data=raw_cpt_df, cone={"a": CptCone()})

    # ── lab profile data ──────────────────────────────────────────────────
    # 1. top and bottom of the lab profile in m, it does not need to be the cpt depths
    lab_profile_depths: list[float] = [0, 100]

    # 2. list of uw in kN/m3, should have same length as lab_profile_depths
    lab_profile_uw: list[float] = [14, 18]
    if len(lab_profile_uw) != len(lab_profile_depths):
        raise ValueError("the length of uw and depth must be the same")

    # 3. list of u0 in kPa, should have same length as lab_profile_depths
    lab_profile_u0: list[float] = [14, 18]
    if len(lab_profile_u0) != len(lab_profile_depths):
        raise ValueError("the length of u0 and depth must be the same")

    lab_data_df = pd.DataFrame({"depth": lab_profile_depths, "uw": lab_profile_uw, "u0": lab_profile_u0})
    lab_data = LabData(data=lab_data_df)

    # ── process the cpt ───────────────────────────────────────────────────
    processed_cpt = CPTProcessCalculation(
        raw_cpt=raw_cpt, lab_data=lab_data, options=CptProcessOptions(cpt_identifier="method_id")
    )
    # 1. choose how the lab profiles are spread over the raw cpt rows
    # this is needed to compute the vertical stress
    # by default the interpolation is a "linear" but if the uw is constant you can set it to "padding" or "linear"
    # note that u0 is always interpolated linearly
    processed_cpt.options.interpolation_mode = "linear"  # "padding" or "linear"

    # 2. Process the cpt data
    processed_cpt.calculate()

    # 3. you can now access the processed cpt data via:
    print(processed_cpt.results.head(10))
