# -*- coding: utf-8 -*-
"""
Data loading

@author: Ro
"""

import yaml
import pandas as pd

with open("../../config/settings.yaml", "r") as file:
    config = yaml.safe_load_all(file)
    density = next(config)
    PE = next(config)
    Pf = next(config)
    RMSD = next(config)