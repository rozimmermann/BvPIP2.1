# -*- coding: utf-8 -*-
"""
Data loading

@author: Ro
"""

import yaml

with open("../../config/settings.yaml", "r") as file:
    config = yaml.safe_load_all(file)
    document1 = next(config)
    document2 = next(config)
    document3 = next(config)
    document4 = next(config)