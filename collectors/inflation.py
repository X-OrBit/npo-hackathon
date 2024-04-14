import requests
import pandas as pd

from bs4 import BeautifulSoup
from dataclasses import dataclass
from pathlib import Path

INFLATION_URl = "https://уровень-инфляции.рф/таблицы-инфляции"


@dataclass
class MonthlyInflationRecord:
    year: int
    month: int
    value: float


@dataclass
class QuarterlyInflationRecord:
    year: int
    quarter: int
    value: float


def collect_inflation() -> list[MonthlyInflationRecord]:
    inflation_records = []

    r = requests.get(INFLATION_URl)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.select_one(".table > tbody")
    rows = table.select("tr")
    for row in rows:
        cells = row.select("td")
        year = int(cells[0].text)

        for month, cell in enumerate(cells[1:13]):
            if not cell.text:
                continue
            inflation_records.append(MonthlyInflationRecord(
                month=month,
                year=year,
                value=float(cell.text)
            ))

    return inflation_records


def monthly_to_quarterly_inflation(monthly_records: list[MonthlyInflationRecord]) -> list[QuarterlyInflationRecord]:
    quarterly_inflation_records_dict: dict[str, list[float]] = {}
    for record in monthly_records:
        key = f"{record.year}-{record.month // 3}"
        quarterly_inflation_records_dict.setdefault(key, []).append(record.value)

    quarterly_inflation_records = [
        QuarterlyInflationRecord(
            year=int(key.split("-")[0]),
            quarter=int(key.split("-")[1]),
            value=round(sum(value) / len(value), 6),
        )
        for key, value in quarterly_inflation_records_dict.items()
    ]

    return sorted(
        quarterly_inflation_records,
        key=lambda r: (r.year, r.quarter),
    )


def collect_and_save_inflation(
        output_file: str | Path,
        from_year: int,
        to_year: int
) -> None:
    if Path(output_file).exists():
        return
    monthly_records = collect_inflation()
    monthly_records = [record for record in monthly_records if (from_year <= record.year <= to_year)]
    quarterly_records = monthly_to_quarterly_inflation(monthly_records)

    df = pd.DataFrame(
        data=[
            [record.year, record.quarter, record.value]
            for record in quarterly_records
        ],
        columns=["year", "quarter", "inflation"]
    )
    df.to_csv(str(output_file), encoding="utf-8", index=False)
