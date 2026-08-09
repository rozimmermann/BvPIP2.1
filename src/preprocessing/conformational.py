# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 17:19:12 2026

@author: Ro
"""

import pandas as pd


def classify_conformation(df: pd.DataFrame, *,
                          gate_distance: str, threshold: float) -> pd.DataFrame:

    result = df.copy()

    result["is_closed"] = (result[gate_distance] < threshold)

    return result
# Determines gate status: open or closed (= "gate flipped"), based on threshold 
# value given in YAML settings file. 

# open_data = df[~df["is_closed"]]
# closed_data = df[df["is_closed"]]


def preprocess_conformational_data(df: pd.DataFrame, params: dict) -> pd.DataFrame:

    conformational_params = params.get("conformational", {})

    gate_column = conformational_params.get("gate_column", "gate_distance")

    gate_threshold = conformational_params.get("gate_threshold", 4.0)

    result = df.copy()

    # 1. Calculate quantities needed by the analysis
    result = calculate_required_quantities(
        result,
        params,
    )

    # 2. Determine gate status
    result = assign_conditions(
        result,
        params,
    )

    # 3. Add conformational labels
    result = classify_conformation(
        result,
        params,
    )

    return classify_conformation(df, 
                                 gate_column=gate_column, 
                                 threshold=gate_threshold)