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
    monthly_labels: np.ndarray
    monthly_counts: np.ndarray


def load_victims_df(victims_json: str) -> pd.DataFrame:
    df = pd.read_json(io.StringIO(victims_json))
    df["discovered"] = pd.to_datetime(df["discovered"], utc=True).dt.tz_convert(None)
    return df


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


def get_victims_stats(df: pd.DataFrame) -> VictimsStats:
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
    dates = np.sort(df["discovered"].dropna().to_numpy())  # zawsze rosnąco
    cumulative = np.arange(1, len(dates) + 1)
    return dates, cumulative


def get_monthly_activity(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    d = df["discovered"].dropna()
    counts = d.dt.to_period("M").value_counts().sort_index()
    labels = counts.index.astype(str).to_numpy()
    return labels, counts.to_numpy()


def get_activity_stats(df: pd.DataFrame) -> ActivityStats:
    dates, cumulative_counts = get_cumulative_activity(df)
    monthly_labels, monthly_counts = get_monthly_activity(df)

    return ActivityStats(
        dates=dates,
        cumulative_counts=cumulative_counts,
        monthly_labels=monthly_labels,
        monthly_counts=monthly_counts,
    )
