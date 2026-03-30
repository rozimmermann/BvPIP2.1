# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:27:19 2026

@author: Ro
"""

import pandas as pd
from typing import Literal
from decimal import Decimal

# -------------------------------------------------------------------
# Precision modes
# Decimal allows for extra precision (with slow processing) when needed, 
# whereas float allows decimal rounding in calculation resulting in 
# faster processing. These modes were included to provide a more exact 
# alternative to the default float calculation Python offers, specially 
# for the Density analysis which resulted in significant differences 
# otherwise. 
# -------------------------------------------------------------------

PrecisionMode = Literal["float", "decimal"]

# -------------------------------------------------------------------
# Apply and validate precision mode
# -------------------------------------------------------------------

def apply_precision_mode(df: pd.DataFrame, mode: PrecisionMode) -> pd.DataFrame:
    if mode == "float":
        return df.astype(float)

    if mode == "decimal":
        return df.astype(str).map(Decimal)

    raise ValueError(f"Unsupported precision mode: {mode}")


def validate_dataframe_precision(df: pd.DataFrame, mode: PrecisionMode, *, allow_nan: bool = False,
    name: str | None = None):
    label = f" in dataset '{name}'" if name else ""

    if mode == "float":
        if not df.dtypes.eq("float64").all():
            raise TypeError(f"Expected float64 columns{label}, found {df.dtypes.to_dict()}")

    elif mode == "decimal":
        for col in df.columns:
            series = df[col]

            if not allow_nan and series.isna().any():
                raise ValueError(f"NaN values detected{label} in column '{col}'.")

            invalid = series.dropna().map(lambda x: not isinstance(x, Decimal))
            if invalid.any():
                idx = invalid.idxmax()
                value = series.loc[idx]
                raise TypeError(f"Precision validation failed{label} in column '{col}': "
                    f"value '{value}' (type={type(value).__name__})")

    else:
        raise ValueError(f"Unsupported precision mode: {mode}")