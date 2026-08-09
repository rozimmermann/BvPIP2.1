# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:32:21 2026

@author: Ro
"""

from yaml_loader import load_yaml_documents
from dataset_loader import load_datasets
from registry import analysis_registry
from registry import plot_registry


def run_pipeline(settings_path):

    docs = load_yaml_documents(settings_path)

    for doc in docs:

        name = doc["analysis_name"]

        datasets = load_datasets(doc["datasets"])
        params = doc["analysis_parameters"]

        if name not in analysis_registry:
            print(f"No analysis for {name}")
            continue

        print(f"Running {name}")

        results = analysis_registry[name](datasets, params)

        if name in plot_registry:
            plot_registry[name](results, params)