# -*- coding: utf-8 -*-
"""
Data loading

@author: Ro
"""

import yaml
import re
import numpy as np
import pandas as pd
from decimal import Decimal
from typing import Literal
from pathlib import Path


# -------------------------------------------------------------------
# Containers
# -------------------------------------------------------------------

ANALYSIS_DATA: dict[str, dict[str, pd.DataFrame]] = {}
ANALYSIS_PARAMS: dict[str, dict] = {}


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
# 1. File-type and content-type dispatch: automatically pick loader 
#    based on extension and content
# -------------------------------------------------------------------

def smart_read_table(path: Path) -> pd.DataFrame:

    header = None

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#"):
                raw = line.lstrip("#").strip()

                # Caso 1: header con |
                if "|" in raw:
                    header = [h.strip() for h in raw.split("|")]
                else:
                    # Caso 2: header alineado por espacios
                    header = re.split(r"\s{2,}", raw)

                break

    if header is None:
        raise ValueError(f"No header found in file: {path}")    

    df = pd.read_csv(path, sep=r"\s+", engine="python", comment="#",
        skip_blank_lines=True, header=None, names=header)

    # Normalización de nombres de columnas
    df.columns = (df.columns
                  .str.strip()
                  .str.replace(r"\s+", "_", regex=True))

    return df

def load_file(path: Path):
    """Load a file by inferring the loader from its extension."""
    
    if not hasattr(load_file, "_LOADERS"):
        load_file._LOADERS = {
            ".csv":    lambda p: pd.read_csv(p),
            ".tsv":    lambda p: pd.read_csv(p, sep="\t"),
            ".txt":    smart_read_table,
            ".out":    smart_read_table, 
            ".parquet": lambda p: pd.read_parquet(p),
            ".json":   lambda p: pd.read_json(p),
            ".xlsx":   lambda p: pd.read_excel(p),
            ".xls":    lambda p: pd.read_excel(p),
            ".npy":    lambda p: pd.DataFrame(np.load(p))
            }
        
    ext = path.suffix.lower()

    if ext not in load_file._LOADERS:
        raise ValueError(f"Unsupported file type: {ext}, path={path}")

    return load_file._LOADERS[ext](path)


# -------------------------------------------------------------------
# 2. Apply and validate precision mode
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
        
        
# -------------------------------------------------------------------
# 2. Flexible dataset loader supporting:
#    - list format: [{'name': 'iris', 'path': '...'}, ...]
#    - dict  format: {'MD1': 'file1.csv', 'MD2': 'file2.csv'}
# -------------------------------------------------------------------

def load_datasets(datasets_spec, *, default_mode: PrecisionMode = "float"):
    
    """
    Returns:
        dict[str, pd.DataFrame]
    """
    datasets = {}

    def load_one(name: str, spec: dict) -> pd.DataFrame:
            path = Path(spec["path"])
            mode: PrecisionMode = spec.get("mode", default_mode)
    
            df = load_file(path)
            df = apply_precision_mode(df, mode)
    
            validate_dataframe_precision(df, mode=mode, name=name)
    
            return df

    # Case A — list format
    if isinstance(datasets_spec, list):
        for entry in datasets_spec:
            if not isinstance(entry, dict) or "path" not in entry:
                raise ValueError(f"Invalid dataset entry: {entry}")

            name = entry.get("name") or Path(entry["path"]).stem
            path = Path(entry["path"])

            datasets[name] = load_one(path)

    # Case B — dict format
    elif isinstance(datasets_spec, dict):
        for name, spec in datasets_spec.items():
            if isinstance(spec, str):
                spec = {"path": spec}

            datasets[name] = load_one(name, spec)

    else:
        raise ValueError(f"Unsupported datasets specification type: {type(datasets_spec)}")

    return datasets

# -------------------------------------------------------------------
# Analysis parameters loader & validator
# -------------------------------------------------------------------

def load_analysis_parameters(params: dict | None, *, analysis_name: str, default_mode: str) -> dict:
    if params is None:
        params = {}

    if not isinstance(params, dict):
        raise TypeError(
            f"'analysis_parameters' in analysis '{analysis_name}' must be a dict, "
            f"got {type(params).__name__}"
        )

    # Validación estructural suave (sin hardcodeo de keys)
    for key, value in params.items():
        if isinstance(value, (list, tuple)) and len(value) == 0:
            raise ValueError(
                f"Empty list for parameter '{key}' in analysis '{analysis_name}'"
            )

        if isinstance(value, dict) and len(value) == 0:
            raise ValueError(
                f"Empty dict for parameter '{key}' in analysis '{analysis_name}'"
            )

    # Metadata experimental (trazabilidad)
    params["_meta"] = {
        "analysis_name": analysis_name,
        "default_mode": default_mode,
    }

    return params


# -------------------------------------------------------------------
# Load multiple YAML documents
# -------------------------------------------------------------------
def load_yaml_documents(path: str):
    with open(path, "r") as f:
        return list(yaml.safe_load_all(f))


# -------------------------------------------------------------------
# Full pipeline: read YAML → load datasets + parameters
# -------------------------------------------------------------------

def load_analysis_configs(settings_path: str):
    docs = load_yaml_documents(settings_path)

    analysis_data: dict[str, dict[str, pd.DataFrame]] = {}
    analysis_params: dict[str, dict] = {}

    for i, doc in enumerate(docs):
        name = doc.get("analysis_name", f"analysis_{i+1}")
        default_mode = doc.get("default_mode", "float")

        # ---- Load datasets ----
        analysis_data[name] = load_datasets(
            doc.get("datasets", {}),
            default_mode=default_mode
        )

        # ---- Load analysis parameters ----
        analysis_params[name] = load_analysis_parameters(
            doc.get("analysis_parameters"),
            analysis_name=name,
            default_mode=default_mode
        )

    return analysis_data, analysis_params

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
        
def main():

    ANALYSIS_DATA, ANALYSIS_PARAMS = load_analysis_configs("../../config/settings.yaml")
    
    for analysis_name in ANALYSIS_DATA:
        print(f"\n=== {analysis_name} ===")
        
        print("Datasets loaded:") 
        for dataset_name, df in ANALYSIS_DATA[analysis_name].items():
            print(f"  {dataset_name}: shape={df.shape}")

        print("Analysis parameters:")
        for key in ANALYSIS_PARAMS[analysis_name].keys():
            print(f"  - {key}")
    
    return ANALYSIS_DATA, ANALYSIS_PARAMS

if __name__ == "__main__":
    ANALYSIS_DATA, ANALYSIS_PARAMS = main()