# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:32:37 2026

@author: Ro
"""

from pipeline.runner import run_pipeline

# Import analyses and plots so they register themselves
import analysis.density
import plots.density_plots


def main():

    run_pipeline("../config/settings.yaml")


if __name__ == "__main__":
    main()