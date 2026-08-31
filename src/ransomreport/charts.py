from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from ransomreport.model import GroupProfile
from ransomreport.stats import ActivityStats, VictimsStats


def _styled_bar_chart(labels, counts, title: str, xlabel: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, counts, color="#4C72B0", width=0.6)

    ax.yaxis.set_major_locator(MaxNLocator(nbins=15))
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_xlim(-0.7, len(labels) - 0.3)

    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel(xlabel, fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=13, fontweight="bold")

    ax.tick_params(axis="x", labelsize=10, rotation=45)
    ax.tick_params(axis="y", labelsize=10)
    plt.setp(ax.get_xticklabels(), ha="right")

    plt.tight_layout()
    return fig


def generate_top_countries(
    stats: VictimsStats, profile: GroupProfile, figures_dir: Path
) -> None:
    fig = _styled_bar_chart(
        stats.countries_names,
        stats.countries_counts,
        title="Number of victims by country",
        xlabel="Country",
        ylabel="Number of victims",
    )
    filename = "top_countries.png"
    fig.savefig(figures_dir / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    profile.figures["top_countries"] = f"figures/{filename}"


def generate_victims_per_sector(
    stats: VictimsStats, profile: GroupProfile, figures_dir: Path
) -> None:
    fig = _styled_bar_chart(
        stats.sectors_names,
        stats.sectors_counts,
        title="Number of victims by sector",
        xlabel="Sector",
        ylabel="Number of victims",
    )
    filename = "victims_per_sector.png"
    fig.savefig(figures_dir / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    profile.figures["victims_per_sector"] = f"figures/{filename}"


def generate_victims_scatter(
    activity: ActivityStats, profile: GroupProfile, figures_dir: Path
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(
        activity.dates,
        activity.cumulative_counts,
        color="#4C72B0",
        s=30,
        alpha=0.85,
        edgecolor="white",
        linewidth=0.5,
    )

    ax.yaxis.set_major_locator(MaxNLocator(nbins=15))
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    ax.set_title("Cumulative victims over time", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Date", fontsize=13, fontweight="bold")
    ax.set_ylabel("Cumulative number of victims", fontsize=13, fontweight="bold")

    ax.tick_params(axis="x", labelsize=10, rotation=45)
    ax.tick_params(axis="y", labelsize=10)
    plt.setp(ax.get_xticklabels(), ha="right")

    plt.tight_layout()

    filename = "victims_scatter.png"
    fig.savefig(figures_dir / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    profile.figures["victims_scatter"] = f"figures/{filename}"


def generate_victims_heatmap(
    activity: ActivityStats, profile: GroupProfile, figures_dir: Path
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(activity.heatmap_matrix, cmap="Blues", aspect="auto")

    ax.set_xticks(range(len(activity.heatmap_months)))
    ax.set_xticklabels(activity.heatmap_months, fontsize=10, rotation=45, ha="right")
    ax.set_yticks(range(len(activity.heatmap_weekdays)))
    ax.set_yticklabels(activity.heatmap_weekdays, fontsize=10)

    for i in range(activity.heatmap_matrix.shape[0]):
        for j in range(activity.heatmap_matrix.shape[1]):
            value = activity.heatmap_matrix[i, j]
            if value > 0:
                color = (
                    "white" if value > activity.heatmap_matrix.max() / 2 else "black"
                )
                ax.text(
                    j, i, str(value), ha="center", va="center", color=color, fontsize=9
                )

    ax.set_title(
        "Attack activity by weekday and month", fontsize=16, fontweight="bold", pad=15
    )
    ax.set_xlabel("Month", fontsize=13, fontweight="bold")
    ax.set_ylabel("Weekday", fontsize=13, fontweight="bold")

    fig.colorbar(im, ax=ax, label="Number of victims")
    plt.tight_layout()

    filename = "victims_heatmap.png"
    fig.savefig(figures_dir / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    profile.figures["victims_heatmap"] = f"figures/{filename}"


def generate_all_charts(
    profile: GroupProfile,
    victims_stats: VictimsStats,
    activity_stats: ActivityStats,
    figures_dir: Path,
) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    generate_top_countries(victims_stats, profile, figures_dir)
    generate_victims_per_sector(victims_stats, profile, figures_dir)
    generate_victims_scatter(activity_stats, profile, figures_dir)
    generate_victims_heatmap(activity_stats, profile, figures_dir)
