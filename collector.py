from pathlib import Path

import pandas as pd

from collectors import (
    collect_and_save_exchange_rate,
    collect_and_save_oil_cost,
    collect_and_save_inflation, Currency,
    collect_and_save_cb_rate,
    collect_and_save_pension_age,
)

COLLECTED_DIR = Path(__file__).parent / "collected"
FROM_YEAR = 1993
TO_YEAR = 2023


def collect_quarterly():
    collect_and_save_inflation(COLLECTED_DIR / "inflation.csv", FROM_YEAR, TO_YEAR)
    collect_and_save_exchange_rate(Currency("dollar"), COLLECTED_DIR / "dollar_exchange_rate.csv", FROM_YEAR, TO_YEAR)
    collect_and_save_exchange_rate(Currency("yuan"), COLLECTED_DIR / "yuan_exchange_rate.csv", FROM_YEAR, TO_YEAR)
    collect_and_save_oil_cost(COLLECTED_DIR / "oil_cost.csv", FROM_YEAR, TO_YEAR)
    collect_and_save_cb_rate(COLLECTED_DIR / "cb_rate.csv", FROM_YEAR, TO_YEAR)
    # collect_and_save_pension_age(COLLECTED_DIR / "pension_age.csv", FROM_YEAR, TO_YEAR)


def join_dataframes(dataframes: list[pd.DataFrame], key_columns: list[str]) -> pd.DataFrame:
    result = dataframes[0]
    print(result.columns)
    for dataframe in dataframes[1:]:
        print(dataframe.columns)
        result = result.merge(dataframe, how="left", on=key_columns)
    return result


def join_data(source_files: list[str | Path], dest_file: str | Path, join_on: list[str]):
    dataframes = [pd.read_csv(str(source_file)) for source_file in source_files]
    dataframe = join_dataframes(dataframes, join_on)
    dataframe.to_csv(str(dest_file), index=False)


def join_quarterly():
    join_data(
        source_files=[
            COLLECTED_DIR / "inflation.csv",
            COLLECTED_DIR / "dollar_exchange_rate.csv",
            COLLECTED_DIR / "yuan_exchange_rate.csv",
            COLLECTED_DIR / "oil_cost.csv",
            COLLECTED_DIR / "cb_rate.csv",
            # COLLECTED_DIR / "pension_age.csv",
        ],
        dest_file=COLLECTED_DIR / "quarterly.csv",
        join_on=["year", "quarter"]
    )


def main():
    Path(COLLECTED_DIR).mkdir(exist_ok=True, parents=True)

    collect_quarterly()
    join_quarterly()


if __name__ == '__main__':
    main()
