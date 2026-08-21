import json
from typing import Any

import requests

from ransomreport.utils import singleton


@singleton
class RansomwareliveClient:
    __token: str
    __url: str = "https://api-pro.ransomware.live"

    def __init__(self, api_token: str):
        self.__token = api_token
        self.__session = requests.Session()
        self.__session.headers.update({"X-API-KEY": self.__token})

        def handle_api_errors(resp: requests.Response, *args, **kwargs) -> None:
            if resp.status_code == 404:
                raise requests.HTTPError(f"Path not found: {resp.request.path_url}")

            data = json.loads(resp.text)
            if "error" in data:
                raise ValueError(data["error"])

        self.__session.hooks["response"] = [handle_api_errors]

    def get_csirts(self, country_code: str) -> list[dict[str, Any]]:
        if country_code and len(country_code) != 2:
            raise ValueError(
                f"country must be  2-letter ISO country code (e.g. FR, US), not {country_code}"
            )

        response = self.__session.get(f"{self.__url}/csirt/{country_code}")
        data = json.loads(response.text)
        return data["results"]

    def get_groups(self) -> list[dict[str, Any]]:
        response = self.__session.get(f"{self.__url}/groups")
        data = json.loads(response.text)
        del data["client"]
        return data["groups"]

    def get_group_details(self, group_name) -> dict[str, Any]:
        response = self.__session.get(f"{self.__url}/groups/{group_name}")
        data = json.loads(response.text)
        del data["client"]
        return data["groups"] if not group_name else data

    def get_iocs(self, ioc_type: str | None = None) -> list[dict[str, Any]]:
        response = self.__session.get(
            f"{self.__url}/iocs",
            params={"type": ioc_type} if ioc_type else {},
        )
        data = json.loads(response.text)
        return data["groups"]

    def get_group_iocs(
        self, group_name: str, ioc_type: str | None = None
    ) -> dict[str, Any]:
        response = self.__session.get(
            f"{self.__url}/iocs/{group_name}",
            params={"type": ioc_type} if ioc_type else {},
        )
        data = json.loads(response.text)
        return data["iocs"]

    def list_sectors(self) -> list[dict[str, Any]]:
        response = self.__session.get(f"{self.__url}/listsectors")
        data = json.loads(response.text)
        return data["sectors"]

    def get_negotiations(
        self, group_name: str | None = None, chat_id: str | None = None
    ) -> list[dict[str, Any]]:
        if chat_id and not group_name:
            raise ValueError("chat_id requires group_name")

        response = self.__session.get(
            f"{self.__url}/negotiations"
            + (f"/{group_name}" if group_name else "")
            + (f"/{chat_id}" if chat_id else ""),
        )

        data = json.loads(response.text)
        del data["client"]
        if chat_id:
            return data["messages"]
        elif group_name:
            return data["chats"]
        else:
            return data["groups"]

    def get_press_all(
        self,
        year: str | None = None,
        month: str | None = None,
        country: str | None = None,
    ) -> list[dict[str, Any]]:
        if year and len(year) != 4 and not year.isdecimal():
            raise ValueError(f"year must be 4-digit string (e.g. 2024), not {year}")
        if month and len(month) != 2 and not month.isdecimal():
            raise ValueError(f"month must be 2-digit string (e.g. 03), not {month}")
        if country and len(country) != 2:
            raise ValueError(
                f"country must be  2-letter ISO country code (e.g. FR, US), not {country}"
            )

        params: dict[str, str] = {}
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if country:
            params["country"] = country

        response = self.__session.get(
            f"{self.__url}/press/all",
            params=params,
        )

        data = json.loads(response.text)
        return data["results"]

    def get_press_recent(self, country: str | None = None) -> list[dict[str, Any]]:
        if country and len(country) != 2:
            raise ValueError(
                f"country must be  2-letter ISO country code (e.g. FR, US), not {country}"
            )

        response = self.__session.get(
            f"{self.__url}/press/recent",
            params={"country": country} if country else {},
        )

        data = json.loads(response.text)

        return data["results"]

    def get_ransom_notes_counts(self) -> list[dict[str, Any]]:
        response = self.__session.get(f"{self.__url}/ransomnotes")

        data = json.loads(response.text)
        del data["client"]
        return data["groups"]

    def get_ransom_notes_names(self, group_name: str) -> list[str]:
        response = self.__session.get(f"{self.__url}/ransomnotes/{group_name}")

        data = json.loads(response.text)
        del data["client"]
        return data["ransomnotes"]

    def get_ransom_note(self, group_name: str, note_name: str) -> dict[str, str]:
        if note_name and not group_name:
            raise ValueError("note_name requires group_name")

        response = self.__session.get(
            f"{self.__url}/ransomnotes/{group_name}/{note_name}"
        )

        data = json.loads(response.text)
        del data["client"]
        return data

    def get_stats(self) -> dict[str, Any]:
        response = self.__session.get(f"{self.__url}/stats")
        data = json.loads(response.text)
        return data["stats"]

    def get_victim(self, victim_id: str) -> dict[str, Any]:
        response = self.__session.get(f"{self.__url}/victim/{victim_id}")
        data = json.loads(response.text)
        return data

    def get_victims(
        self,
        group_name: str | None = None,
        sector: str | None = None,
        country: str | None = None,
        year: str | None = None,
        month: str | None = None,
        date: str | None = None,
    ) -> list[dict[str, Any]]:
        if year and len(year) != 4 and not year.isdecimal():
            raise ValueError(f"year must be 4-digit string (e.g. 2024), not {year}")
        if month and len(month) != 2 and not month.isdecimal():
            raise ValueError(f"month must be 2-digit string (e.g. 03), not {month}")
        if country and len(country) != 2:
            raise ValueError(
                f"country must be  2-letter ISO country code (e.g. FR, US), not {country}"
            )
        if date and date not in ("discovered", "attacked"):
            raise ValueError(
                f"date must be 'discovered' (default) or 'attacked', not {date}"
            )

        params = {}
        if group_name:
            params["group"] = group_name
        if sector:
            params["sector"] = sector
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if country:
            params["country"] = country
        if date:
            params["date"] = date

        response = self.__session.get(f"{self.__url}/victims/", params=params)

        data = json.loads(response.text)

        return data["victims"]

    def get_victims_recent(self, order: str | None = None) -> list[dict[str, Any]]:
        if order and order not in ("discovered", "attacked"):
            raise ValueError(
                f"date must be 'discovered' (default) or 'attacked', not {order}"
            )

        response = self.__session.get(
            f"{self.__url}/victims/recent", params={"order": order} if order else {}
        )
        data = json.loads(response.text)
        return data["victims"]

    def get_victims_search(
        self,
        q: str,
        group_name: str | None = None,
        sector: str | None = None,
        country: str | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        if country and len(country) != 2:
            raise ValueError(
                f"country must be  2-letter ISO country code (e.g. FR, US), not {country}"
            )
        if order and order not in ("discovered", "attacked"):
            raise ValueError(
                f"order must be 'discovered' (default) or 'attacked', not {order}"
            )

        params = {"q": q}
        if group_name:
            params["group"] = group_name
        if sector:
            params["sector"] = sector
        if country:
            params["country"] = country
        if order:
            params["date"] = order

        response = self.__session.get(f"{self.__url}/victims/search", params=params)

        data = json.loads(response.text)

        return data["victims"]

    def get_yara(self, group_name: str | None = None) -> list[dict[str, Any]]:
        response = self.__session.get(
            f"{self.__url}/yara" + (f"/{group_name}" if group_name else "")
        )

        data = json.loads(response.text)

        return data["rules"] if group_name else data["groups"]
