import os
from typing import Any

from dotenv import load_dotenv

from ransomreport.api.malwarebazaar import MalwareBazaarClient, MalwareBazaarError
from ransomreport.api.ransomwarelive import RansomwareliveClient
from ransomreport.model import (
    GroupProfile,
    IndicatorOfCompromiseFile,
    Location,
    Tactic,
    Technique,
    Vulnerability,
)

_ = load_dotenv()

HASH_TYPES = ("md5", "sha128", "sha256")


def make_ransomwarelive_client() -> RansomwareliveClient:
    ransomwarelive_api_token = os.getenv("RANSOMWARELIVE_API_TOKEN")

    if not ransomwarelive_api_token:
        raise ValueError("No ransomware.live API token")

    return RansomwareliveClient(ransomwarelive_api_token)


def make_malwarebazaar_client() -> MalwareBazaarClient:
    bazaar_auth_key = os.getenv("ABUSECH_AUTH_KEY")

    if not bazaar_auth_key:
        raise ValueError("No MalwareBazaar Auth Key")

    return MalwareBazaarClient(bazaar_auth_key)


def build_technique(technique: dict[str, str]) -> Technique:
    return Technique(
        name=technique.get("technique_name", "-"),
        id=technique.get("technique_id", "-"),
        details=technique.get("technique_details", "-"),
    )


def build_tactic(tactic: dict[str, Any]) -> Tactic:
    return Tactic(
        name=tactic.get("tactic_name", "-"),
        id=tactic.get("tactic_id", "-"),
        techniques=[
            build_technique(technique) for technique in tactic.get("techniques", [])
        ],
    )


def build_vulnerability(vulnerability: dict[str, str]) -> Vulnerability:
    return Vulnerability(
        vendor=vulnerability.get("Vendor", "-"),
        product=vulnerability.get("Product", "-"),
        cve=vulnerability.get("CVE", "-"),
        cvss=float(vulnerability.get("CVSS", "0.0")),
        severity=vulnerability.get("severity", "UNKNOWN"),
    )


def build_location(location: dict[str, str]) -> Location:
    return Location(
        fqdn=location.get("fqdn", "-"),
        title=location.get("title", "-"),
        slug=location.get("slug", "-"),
        type=location.get("type", "-"),
        available=bool(location.get("available", "")),
    )


def get_ransom_notes(group_name: str) -> list[dict[str, str]]:
    ransomwarelive = make_ransomwarelive_client()

    note_names = ransomwarelive.get_ransom_notes_names(group_name)
    notes: list[dict[str, str]] = []
    for note_name in note_names:
        note = ransomwarelive.get_ransom_note(group_name, note_name)
        notes.append(
            {
                "name": note["note_name"] + note["extension"],
                "content": note["content"],
            }
        )

    return notes


def get_iocs(group_name: str) -> dict[str, dict[str, str | IndicatorOfCompromiseFile]]:
    ransomwarelive = make_ransomwarelive_client()
    bazaar = make_malwarebazaar_client()
    iocs = ransomwarelive.get_group_iocs(group_name)

    for ioc_type in iocs:
        iocs[ioc_type] = list({ioc.replace(".", "[.]") for ioc in iocs[ioc_type]})

        if ioc_type not in HASH_TYPES:
            continue

        for i, ioc in enumerate(iocs[ioc_type]):
            try:
                hash_info = bazaar.get_info(ioc)
                iocs[ioc_type][i] = IndicatorOfCompromiseFile(
                    hash=ioc,
                    type=hash_info[0]["file_type"],
                    name=hash_info[0]["file_name"],
                )
            except MalwareBazaarError:
                iocs[ioc_type][i] = IndicatorOfCompromiseFile(
                    hash=ioc, type="-", name="-"
                )

    return iocs


def create_profile(group_name: str) -> GroupProfile:
    group_name = group_name.title()
    ransomwarelive = make_ransomwarelive_client()

    details = ransomwarelive.get_group_details(group_name)

    profile = GroupProfile(
        name=details["group"].title(),
        description=details["description"],
        tools=details["tools"],
        ttps=[build_tactic(tactic) for tactic in details["ttps"]],
        vulnerabilities=[
            build_vulnerability(vuln) for vuln in details["vulnerabilities"]
        ],
        locations=[build_location(loc) for loc in details["locations"]],
        victims=ransomwarelive.get_victims(group_name),
    )

    profile.iocs = get_iocs(group_name)

    profile.notes = get_ransom_notes(group_name)

    return profile
