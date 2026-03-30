# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:35:56 2026

@author: Ro
"""

plot_registry = {}


def register_plot(name):

    def wrapper(func):
        plot_registry[name] = func
        return func

    return wrapper