import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader

from ransomreport.aggregate import HASH_TYPES, create_profile
from ransomreport.charts import generate_all_charts
from ransomreport.model import GroupProfile
from ransomreport.stats import (
    VictimsStats,
    get_activity_stats,
    get_victims_stats,
    load_victims_df,
)

env = Environment(
    loader=PackageLoader("ransomreport", "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
)
env.globals.update(zip=zip, now=datetime.now)


def render_group_profile_md(profile: GroupProfile, victims_stats: VictimsStats) -> str:
    template = env.get_template("group_profile.md.j2")
    return template.render(
        profile=profile,
        hash_types=HASH_TYPES,
        stats=victims_stats,
    )


def save_group_profile_md(profile: GroupProfile, output_dir: Path) -> Path:
    group_dir = output_dir / profile.name
    figures_dir = group_dir / "figures"
    group_dir.mkdir(parents=True, exist_ok=True)

    victims_json = json.dumps(profile.victims)
    df = load_victims_df(victims_json)
    victims_stats = get_victims_stats(df)
    activity_stats = get_activity_stats(df)
    generate_all_charts(profile, victims_stats, activity_stats, figures_dir)

    rendered = render_group_profile_md(profile, victims_stats)
    report_path = group_dir / f"{profile.name}.md"
    report_path.write_text(rendered, encoding="utf-8")
    return report_path


def main():
    parser = argparse.ArgumentParser()

    _ = parser.add_argument(
        "-g",
        "--group",
        metavar="GROUP_NAME",
        help="Ransomware group name",
        required=True,
    )
    _ = parser.add_argument(
        "-o",
        "--output-dir",
        metavar="OUTPUT_DIR",
        help="Output directory",
        default="out",
    )

    args = parser.parse_args(sys.argv[1:])

    print(f"[*] Creating profile of group {args.group}")
    profile = create_profile(args.group)

    print("[*] Saving report...")
    report_path = save_group_profile_md(profile, Path(args.output_dir))

    print(f"[+] Report saved to: {report_path}")


if __name__ == "__main__":
    main()
