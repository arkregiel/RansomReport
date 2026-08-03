from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Vulnerability:
    vendor: str
    product: str
    cve: str
    cvss: float
    severity: str


@dataclass
class Technique:
    name: str
    id: str
    details: str


@dataclass
class Tactic:
    name: str
    id: str
    techniques: List[Technique] = field(default_factory=list)


@dataclass
class Location:
    fqdn: str
    title: str
    slug: str
    type: str
    available: bool

    def __post_init__(self):
        self.slug = self.slug.replace(".", "[.]")
        self.fqdn = self.fqdn.replace(".", "[.]")


@dataclass
class IndicatorOfCompromiseFile:
    hash: str
    type: str
    name: str


@dataclass
class GroupProfile:
    name: str
    description: str
    victims: List[Dict[str, Any]] = field(default_factory=list)
    iocs: Dict[str, Any] = field(default_factory=dict)
    ttps: List[Tactic] = field(default_factory=list)
    tools: Dict[str, List[str]] = field(default_factory=dict)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    notes: List[Dict[str, str]] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
