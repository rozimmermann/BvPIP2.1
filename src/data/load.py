# -*- coding: utf-8 -*-
"""
Data loading

@author: Ro
"""

import yaml

with open("config/settings.yaml", "r") as file:
    config = yaml.safe_load(file)

data_path = config["data_path"]