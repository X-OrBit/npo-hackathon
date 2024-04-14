import re

import requests
import pandas as pd

from bs4 import BeautifulSoup
from dataclasses import dataclass
from pathlib import Path

CB_RATE_URl = "https://base.garant.ru/10180094/"


@dataclass
class MonthlyCBRateRecord:
    year: int
    month: int
    value: float


@dataclass
class QuarterlyCBRateRecord:
    year: int
    quarter: int
    value: float


def get_month(str_month: str) -> int:
    months = ["янв", "фев", "мар", "апр", "ма", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
    for index, month in enumerate(months):
        if str_month.startswith(month):
            return index
    raise ValueError


# year, month, day
def parse_date(s: str) -> (int, int, int):
    s = s.strip()
    day = int(s.split(' ')[0])
    month = get_month(s.split(' ')[1])
    year = int(re.findall(r'\d{4}', s)[0])
    return year, month, day


def collect_cb_rate(from_year: int, to_year: int) -> list[MonthlyCBRateRecord]:
    r = requests.get(CB_RATE_URl)
    soup = BeautifulSoup(r.text, "html.parser")
    data = []
    tables = soup.select("table")
    for table in tables:
        rows = table.select("tr")
        for row in rows:
            cells = row.select("td")
            data.append((*parse_date(cells[0].text.split("-")[0]), float(cells[1].text.strip().replace(",", "."))))

    data.sort()

    cb_rate_records = []
    index = 0
    for year in range(from_year, to_year + 1):
        for month in range(0, 12):
            while index + 1 < len(data) and (year, month, 1) >= tuple(data[index + 1][:3]):
                index += 1
            value = data[index][-1]
            cb_rate_records.append(
                MonthlyCBRateRecord(
                    year=year,
                    month=month,
                    value=value
                )
            )

    return cb_rate_records


def monthly_to_quarterly_cb_rate(monthly_records: list[MonthlyCBRateRecord]) -> list[QuarterlyCBRateRecord]:
    quarterly_cb_rate_records_dict: dict[str, list[float]] = {}
    for record in monthly_records:
        key = f"{record.year}-{record.month // 3}"
        quarterly_cb_rate_records_dict.setdefault(key, []).append(record.value)

    quarterly_cb_rate_records = [
        QuarterlyCBRateRecord(
            year=int(key.split("-")[0]),
            quarter=int(key.split("-")[1]),
            value=round(sum(value) / len(value), 6),
        )
        for key, value in quarterly_cb_rate_records_dict.items()
    ]

    return sorted(
        quarterly_cb_rate_records,
        key=lambda r: (r.year, r.quarter),
    )


def collect_and_save_cb_rate(
        output_file: str | Path,
        from_year: int,
        to_year: int
) -> None:
    if Path(output_file).exists():
        return
    monthly_records = collect_cb_rate(from_year, to_year)
    monthly_records = [record for record in monthly_records if (from_year <= record.year <= to_year)]
    quarterly_records = monthly_to_quarterly_cb_rate(monthly_records)

    df = pd.DataFrame(
        data=[
            [record.year, record.quarter, record.value]
            for record in quarterly_records
        ],
        columns=["year", "quarter", "cb_rate"]
    )
    df.to_csv(str(output_file), encoding="utf-8", index=False)
