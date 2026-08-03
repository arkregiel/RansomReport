import argparse
import sys

from ransomreport.aggregate import HASH_TYPES, create_profile
from ransomreport.model import GroupProfile


def print_group_profile_md(profile: GroupProfile) -> None:
    print(f"# Ransomware Group: {profile.name}\n")
    print(profile.description, "\n")

    print("## TTPs\n")

    for tactic in profile.ttps:
        print(f"### {tactic.id} -- {tactic.name}\n")
        print("| Technique ID | Technique Name | Technique Details |")
        print("|:---|:---|:---|")
        for technique in tactic.techniques:
            print(f"| {technique.id} | {technique.name} | {technique.details} |")

        print()

    print("## Tools\n")

    for purpose in profile.tools.keys():
        print(f"- **{purpose}**")
        for tool in profile.tools[purpose]:
            print(f"\t- {tool}")

    print()

    print("## Locations\n")

    print("| Title | Type | URL |")
    print("|:---|:---|:---|")
    for location in profile.locations:
        print(f"| {location.title} | {location.type} | {location.slug} |")

    print()

    print("## IoC\n")

    for ioc_type in profile.iocs.keys():
        print(f"### {ioc_type.upper()}\n")
        if ioc_type in HASH_TYPES:
            print("| Hash | File Type | File Name |")
            print("|:---|:---|:---|")
            for ioc in profile.iocs[ioc_type]:
                print(f"| {ioc.hash} | {ioc.type} | {ioc.name} |")

            continue

        for ioc in profile.iocs[ioc_type]:
            print(f"- {ioc}")

    print()

    print("## Ransom Notes\n")

    for note in profile.notes:
        print(f"*{note['name']}*")
        print("```")
        print(note["content"])
        print("```\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
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
