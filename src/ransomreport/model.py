from dataclasses import dataclass, field


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
    techniques: list[Technique] = field(default_factory=list)


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
    victims: list[dict[str, dict[str, object]]] = field(default_factory=list)
    iocs: dict[str, dict[str, str | IndicatorOfCompromiseFile]] = field(
        default_factory=dict
    )
    ttps: list[Tactic] = field(default_factory=list)
    tools: dict[str, list[str]] = field(default_factory=dict)
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    notes: list[dict[str, str]] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)
