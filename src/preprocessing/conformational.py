# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 17:19:12 2026

@author: Ro
"""

import pandas as pd


def preprocess_conformational_data(df: pd.DataFrame, *, gate_threshold: float = 4.0) -> pd.DataFrame:

    df = df.copy()

    # 1. Calculate quantities needed by the analysis
    # ...

    # 2. Determine gate status
    # ...

    # 3. Add conformational labels
    # ...

    return df


def classify_conformation(gate_distance: pd.Series, *, threshold: float = 4.0) -> pd.Series:

    return gate_distance < threshold


df["gate_flipped"] = classify_conformation(
    df["gate_distance"],
    threshold=4.0,
)

# df["is_closed"] = df["gate_distance"] < threshold

# open_data = df[~df["is_closed"]]
# closed_data = df[df["is_closed"]]