# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:29:17 2026

@author: Ro
"""

from .registry import register_analysis


@register_analysis("Density")
def run_density_analysis(datasets, params):

    results = {}

    y = params["y_column"]
    features = params["feature_columns"]

    for name, df in datasets.items():

        results[name] = df[[y] + features]

    return results