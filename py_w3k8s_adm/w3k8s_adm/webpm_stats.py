from collections import defaultdict
from dataclasses import dataclass
import functools
import os
from pathlib import Path
from typing import Any, Literal
import json


@dataclass(frozen=True)
class VersionStats:
    version: str
    library_id: str
    files: list[Path]
    size: int
    all_packages: list[str]
    # size of file, in bytes


@dataclass(frozen=True)
class PackageStats:
    name: str
    versions: list[str]
    versions_stats: dict[str, VersionStats]
    namespace: str
    kind: str
    path: Path

    def __str__(self, indent: int = 0):
        prefix = "\t" * indent
        r = f"{prefix}📦 {self.name}\n"
        r += f"{prefix}\tkind: {self.kind}\n"
        for k, v in self.versions_stats.items():
            r += f"{prefix}\t{k} : {len(v.files)} files ({v.size} bytes)\n"

        return r


Kinds = Literal["esm", "webapp", "pyodide", "backends", "unknown"]


@dataclass(frozen=True)
class WebpmStats:
    packages: list[PackageStats]
    namespaces: dict[str, int]
    kinds: dict[Kinds, int]
    root_package_ids: set[str]
    documents: list[dict[str, Any]]

    @staticmethod
    def from_documents(local_db_path: Path):
        webpm_docdb_path = local_db_path / "docdb" / "webpm" / "libraries" / "data.json"
        webpm_storage_path = local_db_path / "storage" / "webpm" / "libraries"
        data = json.load(open(webpm_docdb_path, "rb"))
        all_packages = [d for d in data["documents"]]

        kinds: dict[Kinds, int] = defaultdict(lambda: 0)
        namespaces: dict[str, int] = defaultdict(lambda: 0)
        root_packages = [
            d for d in all_packages if (not "parent" in d or not d["parent"])
        ]
        root_package_ids = {p["library_id"] for p in root_packages}
        library_names: set[str] = set()
        for p in root_packages:
            if p["library_name"] in library_names:
                continue
            namespaces[p["namespace"]] += 1
            if not "kind" in p:
                kinds["unknown"] += 1
                continue
            kinds[p["kind"]] += 1

            if not p["library_name"] in library_names:
                library_names.add(p["library_name"])

        package_names = set(p["library_name"] for p in root_packages)
        packages_stats: list[PackageStats] = []
        for package_name in package_names:
            versions = [
                p["version"] for p in root_packages if p["library_name"] == package_name
            ]
            first = next(
                (p for p in root_packages if p["library_name"] == package_name)
            )
            versions_stats = {}
            for version in versions:
                path = webpm_storage_path / package_name.replace("@", "") / version
                files = [
                    f
                    for f in list(path.rglob("*"))
                    if f.is_file() and (f.parent / f"{f.name}.metadata.json").is_file()
                ]
                size = functools.reduce(
                    lambda acc, e: acc + os.stat(e).st_size, files, 0
                )
                sub_packages = [
                    p["library_id"]
                    for p in all_packages
                    if "parent" in p and p["parent"] == f"{package_name}#{version}"
                ]
                library_id = f"{package_name}#{version}"
                versions_stats[version] = VersionStats(
                    library_id=library_id,
                    version=version,
                    files=files,
                    size=size,
                    all_packages=[library_id, *sub_packages],
                )
            stats = PackageStats(
                name=package_name,
                path=webpm_storage_path / package_name.replace("@", ""),
                versions=versions,
                versions_stats=versions_stats,
                namespace=first["namespace"],
                kind=first["kind"],
            )
            packages_stats.append(stats)

        return WebpmStats(
            packages=packages_stats,
            kinds=kinds,
            root_package_ids=root_package_ids,
            namespaces=namespaces,
            documents=all_packages,
        )

    def __str__(self):
        r = ""
        r += f"🔍 Found {len(self.namespaces)} namespaces:\n"
        for k, count in self.namespaces.items():
            r += f"\t📂 {k} : {count} packages \n"

        r += f"\t🔍 Found {len(self.kinds)} kinds:\n"
        for k, count in self.kinds.items():
            r += f"\t📂 {k} : {count} packages \n"

        r += f"\t🔍 Found {len(self.packages)} packages:\n"
        for p in self.packages:
            r += p.__str__(1)

        return r
