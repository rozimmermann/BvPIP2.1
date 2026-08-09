# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 17:19:12 2026

@author: Ro
"""

import pandas as pd


def preprocess_conformational_data(df: pd.DataFrame, *, 
                                   gate_threshold: float = 4.0) -> pd.DataFrame:

    df = df.copy()

    # 1. Calculate quantities needed by the analysis
    # ...

    # 2. Determine gate status
    # ...

    # 3. Add conformational labels
    # ...

    return df


def classify_conformation(df: pd.DataFrame, *,
                          gate_distance: str, threshold: float) -> pd.DataFrame:

    result = df.copy()

    result["is_closed"] = (result[gate_distance] < threshold)

    return result
# Determines gate status: open or closed (= "gate flipped"), based on threshold 
# value given in YAML settings file. 

# open_data = df[~df["is_closed"]]
# closed_data = df[df["is_closed"]]