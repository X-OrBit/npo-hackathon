from enum import Enum

import requests
import pandas as pd
import re

from tqdm import tqdm
from bs4 import BeautifulSoup
from dataclasses import dataclass
from pathlib import Path

EXCHANGE_RATE_URl = "https://ratestats.com/%(currency)s/%(year)d/"


class Currency(Enum):
    DOLLAR = "dollar"
    YUAN = "yuan"


@dataclass
class MonthlyExchangeRateRecord:
    year: int
    month: int
    value: float


@dataclass
class QuarterlyExchangeRateRecord:
    year: int
    quarter: int
    value: float


def collect_exchange_rate(
        currency: Currency,
        from_year: int,
        to_year: int
) -> list[MonthlyExchangeRateRecord]:
    exchange_rate_records = []

    for year in tqdm(range(from_year, to_year + 1), desc=f"Collecting {currency.value} exchange rates"):
        r = requests.get(EXCHANGE_RATE_URl % {
            "currency": currency.value,
            "year": year
        })
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.select_one(".b-rates_middle > table > tbody")
        rows = table.select("tr")
        for month, row in enumerate(rows):
            cells = row.select("td")
            value = float(re.sub("\s+", "", cells[3].text.replace(",", ".")))
            exchange_rate_records.append(
                MonthlyExchangeRateRecord(
                    year=year,
                    month=month,
                    value=value
                )
            )

    return exchange_rate_records


def monthly_to_quarterly_inflation(monthly_records: list[MonthlyExchangeRateRecord]) -> list[QuarterlyExchangeRateRecord]:
    quarterly_inflation_records_dict: dict[str, list[float]] = {}
    for record in monthly_records:
        key = f"{record.year}-{record.month}"
        quarterly_inflation_records_dict.setdefault(key, []).append(record.value)

    quarterly_inflation_records = [
        QuarterlyExchangeRateRecord(
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


def collect_and_save_exchange_rate(
        currency: Currency,
        output_file: str | Path,
        from_year: int,
        to_year: int
) -> None:
    if Path(output_file).exists():
        return
    monthly_records = collect_exchange_rate(currency, from_year, to_year)
    quarterly_records = monthly_to_quarterly_inflation(monthly_records)

    df = pd.DataFrame(
        data=[
            [record.year, record.quarter, record.value]
            for record in quarterly_records
        ],
        columns=["year", "quarter", currency.value],
    )
    df.to_csv(str(output_file), encoding="utf-8", index=False)
