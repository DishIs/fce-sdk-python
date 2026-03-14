"""Domains resource."""
from __future__ import annotations
from urllib.parse import quote
from ..http import HttpClient, SyncHttpClient
from ..types import (DomainInfo, CustomDomain, AddCustomDomainResult,
                     VerifyCustomDomainResult, RemoveCustomDomainResult)


class DomainsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> list[DomainInfo]:
        data = await self._http.request("GET", "/domains")
        return [DomainInfo.from_dict(d) for d in data.get("data", [])]

    async def list_with_expiry(self) -> list[DomainInfo]:
        data = await self._http.request("GET", "/domains/all")
        return [DomainInfo.from_dict(d) for d in data.get("data", [])]

    async def list_custom(self) -> list[CustomDomain]:
        data = await self._http.request("GET", "/custom-domains")
        return [CustomDomain.from_dict(d) for d in data.get("data", [])]

    async def add_custom(self, domain: str) -> AddCustomDomainResult:
        data = await self._http.request("POST", "/custom-domains", body={"domain": domain})
        return AddCustomDomainResult.from_dict(data.get("data", data))

    async def verify_custom(self, domain: str) -> VerifyCustomDomainResult:
        data = await self._http.request("POST", f"/custom-domains/{quote(domain)}/verify", body={})
        return VerifyCustomDomainResult.from_dict(data)

    async def remove_custom(self, domain: str) -> RemoveCustomDomainResult:
        data = await self._http.request("DELETE", f"/custom-domains/{quote(domain)}")
        return RemoveCustomDomainResult.from_dict(data)


class SyncDomainsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def list(self) -> list[DomainInfo]:
        data = self._http.request("GET", "/domains")
        return [DomainInfo.from_dict(d) for d in data.get("data", [])]

    def list_with_expiry(self) -> list[DomainInfo]:
        data = self._http.request("GET", "/domains/all")
        return [DomainInfo.from_dict(d) for d in data.get("data", [])]

    def list_custom(self) -> list[CustomDomain]:
        data = self._http.request("GET", "/custom-domains")
        return [CustomDomain.from_dict(d) for d in data.get("data", [])]

    def add_custom(self, domain: str) -> AddCustomDomainResult:
        data = self._http.request("POST", "/custom-domains", body={"domain": domain})
        return AddCustomDomainResult.from_dict(data.get("data", data))

    def verify_custom(self, domain: str) -> VerifyCustomDomainResult:
        data = self._http.request("POST", f"/custom-domains/{quote(domain)}/verify", body={})
        return VerifyCustomDomainResult.from_dict(data)

    def remove_custom(self, domain: str) -> RemoveCustomDomainResult:
        data = self._http.request("DELETE", f"/custom-domains/{quote(domain)}")
        return RemoveCustomDomainResult.from_dict(data)
