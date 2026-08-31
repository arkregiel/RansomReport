import io
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd


@dataclass
class VictimsStats:
    first_discovered: date
    last_discovered: date
    countries_names: np.ndarray
    countries_counts: np.ndarray
    sectors_names: np.ndarray
    sectors_counts: np.ndarray


@dataclass
class ActivityStats:
    dates: np.ndarray
    cumulative_counts: np.ndarray
    heatmap_matrix: np.ndarray
    heatmap_weekdays: np.ndarray
    heatmap_months: np.ndarray


def get_countries_stats(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    series = df["country"].replace("", np.nan).dropna().value_counts()

    top10 = series.head(10)
    other = series.iloc[10:].sum()

    series_top = pd.concat([top10, pd.Series({"other": other})])

    counts = series_top.to_numpy()
    countries = series_top.index.to_numpy()
    return countries, counts


def get_sectors_stats(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    series = df["activity"].replace("", np.nan).dropna().value_counts()

    counts = series.to_numpy()
    sectors = series.index.to_numpy()

    return sectors, counts


def get_victims_stats(victims_json: str) -> VictimsStats:
    df = pd.read_json(io.StringIO(victims_json))
    df["discovered"] = pd.to_datetime(df["discovered"])

    countries_names, countries_counts = get_countries_stats(df)
    sectors_names, sectors_counts = get_sectors_stats(df)

    return VictimsStats(
        first_discovered=df["discovered"].min(skipna=False).date(),
        last_discovered=df["discovered"].max(skipna=False).date(),
        countries_names=countries_names,
        countries_counts=countries_counts,
        sectors_names=sectors_names,
        sectors_counts=sectors_counts,
    )


def get_cumulative_activity(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    dates = df["discovered"].dropna().to_numpy()
    cumulative = np.arange(1, len(dates) + 1)
    return dates, cumulative


def get_activity_heatmap(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    d = df["discovered"].dropna()
    weekday = pd.Categorical(d.dt.day_name(), categories=weekday_order, ordered=True)
    month = pd.Categorical(d.dt.month_name(), categories=month_order, ordered=True)

    pivot = pd.crosstab(weekday, month).reindex(
        index=weekday_order, columns=month_order, fill_value=0
    )
    return pivot.to_numpy(), pivot.index.to_numpy(), pivot.columns.to_numpy()


def get_activity_stats(victims_json: str) -> ActivityStats:
    df = pd.read_json(io.StringIO(victims_json))
    df["discovered"] = pd.to_datetime(df["discovered"])

    dates, cumulative_counts = get_cumulative_activity(df)
    matrix, weekdays, months = get_activity_heatmap(df)

    return ActivityStats(
        dates=dates,
        cumulative_counts=cumulative_counts,
        heatmap_matrix=matrix,
        heatmap_weekdays=weekdays,
        heatmap_months=months,
    )
