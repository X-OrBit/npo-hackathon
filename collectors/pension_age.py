import pandas as pd

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MonthlyPensionAgeRecord:
    year: int
    month: int
    male_value: float
    female_value: float


@dataclass
class QuarterlyPensionAgeRecord:
    year: int
    quarter: int
    male_value: float
    female_value: float


def collect_pension_age(from_year: int, to_year: int) -> list[MonthlyPensionAgeRecord]:
    data = [
        (1967, 0, 1, 55, 60),
        (2020, 0, 1, 56, 61),
        (2022, 0, 1, 57, 62),
        (2024, 0, 1, 58, 63),
        (2026, 0, 1, 59, 64),
        (2028, 0, 1, 60, 65),
        (2030, 0, 1, 61, 65),
        (2032, 0, 1, 62, 65),
        (2034, 0, 1, 63, 65),
    ]

    pension_age_records = []
    index = 0
    for year in range(from_year, to_year + 1):
        for month in range(0, 12):
            while index + 1 < len(data) and (year, month, 1) >= tuple(data[index + 1][:3]):
                index += 1
            pension_age_records.append(
                MonthlyPensionAgeRecord(
                    year=year,
                    month=month,
                    male_value=data[index][-2],
                    female_value=data[index][-1],
                )
            )

    return pension_age_records


def monthly_to_quarterly_pension_age(monthly_records: list[MonthlyPensionAgeRecord]) -> list[QuarterlyPensionAgeRecord]:
    quarterly_pension_age_records_dict: dict[str, list[list[float]]] = {}
    for record in monthly_records:
        key = f"{record.year}-{record.month // 3}"
        if key not in quarterly_pension_age_records_dict:
            quarterly_pension_age_records_dict[key] = [[], []]
        quarterly_pension_age_records_dict[key][0].append(record.male_value)
        quarterly_pension_age_records_dict[key][1].append(record.female_value)

    quarterly_pension_age_records = [
        QuarterlyPensionAgeRecord(
            year=int(key.split("-")[0]),
            quarter=int(key.split("-")[1]),
            male_value=round(sum(value[0]) / len(value[0]), 6),
            female_value=round(sum(value[1]) / len(value[1]), 6),
        )
        for key, value in quarterly_pension_age_records_dict.items()
    ]

    return sorted(
        quarterly_pension_age_records,
        key=lambda r: (r.year, r.quarter),
    )


def collect_and_save_pension_age(
        output_file: str | Path,
        from_year: int,
        to_year: int
) -> None:
    if Path(output_file).exists():
        return
    monthly_records = collect_pension_age(from_year, to_year)
    monthly_records = [record for record in monthly_records if (from_year <= record.year <= to_year)]
    quarterly_records = monthly_to_quarterly_pension_age(monthly_records)

    df = pd.DataFrame(
        data=[
            [record.year, record.quarter, record.male_value, record.female_value]
            for record in quarterly_records
        ],
        columns=["year", "quarter", "pension_age_male", "pension_age_female"]
    )
    df.to_csv(str(output_file), encoding="utf-8", index=False)
