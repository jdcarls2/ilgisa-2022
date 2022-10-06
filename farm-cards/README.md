# Kendall County Farm Card Calculations

## Overview
The purpose of this repository is to openly document the means by which farmland cards are calculated in Kendall County, and to make those methods available to the general public, both for possible replication elsewhere and for accountability to County residents.

This repository does *not* detail the *valuation* of farm parcels as it applies to Kendall County specifically, though the general process is described in the `farm-cards.ipynb` notebook.

The valuation process is the purview of the [Assessment Office](https://kendallcountyil.gov/offices/assessments), and further inquiries in such matters can be directed there.

## Contents

* `farm-cards.ipynb`

    This **Jupyter Notebook** gives the step-by step procedure typically followed, and shows examples of intermediate and final outputs. It also includes some discussion of how the code might be adapted for other environments.

* `farm_output.txt`

    Sample output from the notebook

* `input_pins.txt`

    Sample PINs for running the notebook

* `farm-cards.slides.html`

    A standalone presentation file of notebook cells converted to slides. Non-interactive.

* `input_pins.shp, shx, etc`

    Shapefile of input parcel features

* `soil_PI.csv`

    CSV of soil productivity indices per soil type, from the Illinois Department of Revenue