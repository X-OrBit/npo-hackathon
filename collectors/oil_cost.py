import pandas as pd

from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data/oil_cost.csv"


@dataclass
class MonthlyOilCostRecord:
    year: int
    month: int
    value: float


@dataclass
class QuarterlyOilCostRecord:
    year: int
    quarter: int
    value: float


def collect_oil_cost() -> list[MonthlyOilCostRecord]:
    df = pd.read_csv(DATA_PATH)

    return [
        MonthlyOilCostRecord(
            year=int(row["Дата"].split(".")[-1]),
            month=int(row["Дата"].split(".")[1]) - 1,
            value=float(row["Цена"].replace(",", "."))
        )
        for _, row in df.iterrows()
    ]


def monthly_to_quarterly_oil_cost(monthly_records: list[MonthlyOilCostRecord]) -> list[QuarterlyOilCostRecord]:
    quarterly_oil_cost_records_dict: dict[str, list[float]] = {}
    for record in monthly_records:
        key = f"{record.year}-{record.month // 3}"
        quarterly_oil_cost_records_dict.setdefault(key, []).append(record.value)

    quarterly_oil_cost_records = [
        QuarterlyOilCostRecord(
            year=int(key.split("-")[0]),
            quarter=int(key.split("-")[1]),
            value=round(sum(value) / len(value), 6),
        )
        for key, value in quarterly_oil_cost_records_dict.items()
    ]

    return sorted(
        quarterly_oil_cost_records,
        key=lambda r: (r.year, r.quarter),
    )


def collect_and_save_oil_cost(
        output_file: str | Path,
        from_year: int,
        to_year: int
) -> None:
    if Path(output_file).exists():
        return
    monthly_records = collect_oil_cost()
    monthly_records = [record for record in monthly_records if (from_year <= record.year <= to_year)]
    quarterly_records = monthly_to_quarterly_oil_cost(monthly_records)

    df = pd.DataFrame(
        data=[
            [record.year, record.quarter, record.value]
            for record in quarterly_records
        ],
        columns=["year", "quarter", "oil_cost"]
    )
    df.to_csv(str(output_file), encoding="utf-8", index=False)
