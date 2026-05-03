# -*- coding: utf-8 -*-
"""
Data loading

@author: Ro
"""

import re
import numpy as np
import pandas as pd
from pathlib import Path
from src.loaders import precision as pr
from src.loaders import yaml_loader as yml
from src.utils import metadata_builder as meta


# -------------------------------------------------------------------
# Containers
# -------------------------------------------------------------------

ANALYSIS_DATA: dict[str, dict[str, pd.DataFrame]] = {}
ANALYSIS_PARAMS: dict[str, dict] = {}

# -------------------------------------------------------------------
# File-type and content-type dispatch: automatically pick loader 
# based on extension and content
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
# Flexible dataset loader supporting:
#   - list format: [{'name': 'iris', 'path': '...'}, ...]
#   - dict  format: {'MD1': 'file1.csv', 'MD2': 'file2.csv'}
# -------------------------------------------------------------------

def load_datasets(datasets_spec, *, default_mode: pr.PrecisionMode = "float"):
    
    """
    Returns:
        dict[str, pd.DataFrame]
    """
    datasets = {}

    def load_one(name: str, spec: dict) -> pd.DataFrame:
            path = Path(spec["path"])
            mode: pr.PrecisionMode = spec.get("mode", default_mode)
    
            df = load_file(path)
            df = pr.apply_precision_mode(df, mode)
    
            pr.validate_dataframe_precision(df, mode=mode, name=name)
    
            return df

    # Case A — list format
    if isinstance(datasets_spec, list):
        for entry in datasets_spec:
            if not isinstance(entry, dict) or "path" not in entry:
                raise ValueError(f"Invalid dataset entry: {entry}")

            name = entry.get("name") or Path(entry["path"]).stem

            df = load_one(name, entry)
            df.attrs["metadata"] = meta.parse_dataset_name(name)
            datasets[name] = df

    # Case B — dict format
    elif isinstance(datasets_spec, dict):
        for name, spec in datasets_spec.items():
            if isinstance(spec, str):
                spec = {"path": spec}

            df = load_one(name, spec)
            df.attrs["metadata"] = meta.parse_dataset_name(name)
            datasets[name] = df

    else:
        raise ValueError(f"Unsupported datasets specification type: {type(datasets_spec)}")

    metadata_index = meta.build_metadata_index(datasets)

    return {"datasets": datasets, "metadata_index": metadata_index}

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
# Full pipeline: read YAML → load datasets + parameters
# -------------------------------------------------------------------

def load_analysis_configs(settings_path: str):
    docs = yml.load_yaml_documents(settings_path)

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
    
    for analysis_name, analysis_bundle in ANALYSIS_DATA.items():
        print(f"\n=== {analysis_name} ===")
        
        datasets = analysis_bundle["datasets"]
        metadata_index = analysis_bundle["metadata_index"]
        
        print("Datasets loaded:") 
        for dataset_name, df in datasets.items():
            print(f"  {dataset_name}: shape={df.shape}")

        print("\nMetadata index:")
        print(metadata_index)

        print("\nAnalysis parameters:")
        for key in ANALYSIS_PARAMS[analysis_name].keys():
            print(f"  - {key}")
    
    return ANALYSIS_DATA, ANALYSIS_PARAMS

if __name__ == "__main__":
    ANALYSIS_DATA, ANALYSIS_PARAMS = main()