import argparse
import sys

from jinja2 import Environment, PackageLoader

from ransomreport.aggregate import HASH_TYPES, create_profile
from ransomreport.model import GroupProfile

env = Environment(
    loader=PackageLoader("ransomreport", "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_group_profile_md(profile: GroupProfile) -> str:
    template = env.get_template("group_profile.md.j2")
    return template.render(profile=profile, hash_types=HASH_TYPES)


def print_group_profile_md(profile: GroupProfile) -> None:
    print(render_group_profile_md(profile))


def main():
    parser = argparse.ArgumentParser()

    _ = parser.add_argument(
        "-g",
        "--group",
        metavar="GROUP_NAME",
        help="Ransomware group name",
        required=True,
    )

    args = parser.parse_args(sys.argv[1:])

    profile = create_profile(args.group)

    print_group_profile_md(profile)


if __name__ == "__main__":
    main()
