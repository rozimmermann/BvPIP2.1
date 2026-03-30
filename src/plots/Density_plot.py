# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:31:26 2026

@author: Ro
"""

import matplotlib.pyplot as plt
from .registry import register_plot


@register_plot("Density")
def plot_density(results, params):

    y = params["y_column"]
    features = params["feature_columns"]

    for name, df in results.items():

        plt.figure()

        for f in features:
            plt.plot(df[y], df[f], label=f)

        plt.title(name)
        plt.legend()

        plt.show()