# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 17:19:12 2026

@author: Ro
"""

import pandas as pd


def preprocess_conformational_data(df: pd.DataFrame, params: dict) -> pd.DataFrame:

    df = df.copy()

    preprocessing_params = params.get("preprocessing", {})

    conformational_params = params.get("conformational", {})

    if preprocessing_params.get("calculate_dpe", False):
        df = calculate_dpe(df)

    if preprocessing_params.get("calculate_dpe_dt", False):
        df = calculate_dpe_dt(df)

    if conformational_params.get("enabled", True):
        df = classify_conformation(df,
                                   threshold=conformational_params.get("gate_threshold", 4.0))

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