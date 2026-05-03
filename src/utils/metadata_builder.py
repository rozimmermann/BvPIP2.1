# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 17:58:38 2026

@author: Ro
"""

import re
import pandas as pd
from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetMetadata:
    md: int | None = None
    chain: str | None = None
    dyn_cm: int | None = None


dataset_name_pattern = re.compile(
    r"""
    MD(?P<md>\d+)                    # MD number
    (?:\s+Chain\s+(?P<chain>[A-Z]))? # optional chain
    (?:\s+(?P<dyn_cm>\d+)DynCm)?     # optional dyn cm
    """,
    re.VERBOSE
)


def parse_dataset_name(name: str) -> DatasetMetadata:
    match = dataset_name_pattern.search(name)

    if not match:
        return DatasetMetadata()

    groups = match.groupdict()

    return DatasetMetadata(
        md=int(groups.get("md")) if groups.get("md") else None,
        chain=groups.get("chain"),
        dyn_cm=int(groups.get("dyn_cm")) if groups.get("dyn_cm") else None
    )


def build_metadata_index(datasets):

    rows = []

    for name, df in datasets.items():
        meta = df.attrs["metadata"]

        rows.append({
            "name": name,
            "md": meta.md,
            "chain": meta.chain,
            "dyn_cm": meta.dyn_cm
        })

    return pd.DataFrame(rows)