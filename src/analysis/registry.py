# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:33:41 2026

@author: Ro
"""

analysis_registry = {}


def register_analysis(name):

    def wrapper(func):
        analysis_registry[name] = func
        return func

    return wrapper