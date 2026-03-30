# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:27:36 2026

@author: Ro
"""

import yaml

# -------------------------------------------------------------------
# Load multiple YAML documents
# -------------------------------------------------------------------

def load_yaml_documents(path: str):
    with open(path, "r") as f:
        return list(yaml.safe_load_all(f))