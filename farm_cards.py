########
# Name:         Farm Card Calculations
# Author:       Josh Carlson, Kendall County IL
# Last Updated: 07-Oct-2022
# Description:  A script to calculate farmland features for import into Devnet
# Output:       A .txt file
########


## Modules
import geopandas as gp
import pandas as pd
import numpy as np
import requests
from pathlib import Path
from datetime import datetime
import re

## Globals -- Change these as needed
# Spatial reference for layers
sr = "{'wkid': 3435}"

# Parcels REST service
parcels_url = 'https://maps.co.kendall.il.us/server/rest/services/Hosted/Current_Cadastral_Features/FeatureServer/1/query?'

# SSURGO Soils REST service
soils_url = 'https://maps.co.kendall.il.us/server/rest/services/Hosted/Assessor_Soils/FeatureServer/0/query?'

# Landuse REST service
landuse_url = 'https://maps.co.kendall.il.us/server/rest/services/Hosted/Assessor_Landuse/FeatureServer/0/query?'

# Prepare default output
out_file = Path.expanduser(Path(f"~/Desktop/farms_{datetime.now().strftime('%Y%m%d-%H%M')}.txt"))
    
## Drop any existing file by same name
if Path.exists(out_file):
    print('Output file already exists. Removing!')
    Path.remove(out_file)
Path.touch(out_file)
print('Good to go!')

## Warnings start at False
warnings = False

## Get a list of PINs from variable text input
pin_string = input('Enter PINs: ')
pin_list = re.split('\n|,|&', re.sub(' |-', '', pin_string))
pins = ','.join(["'" + p.replace('-', '') + "'" for p in pin_list])

## Parcels DF
# Request parameters
parcels_params = {
    'where': f"pin_dashless IN ({pins})",
    'outFields': 'gross_acres, pin_dashless',
    'outSR': sr,
    'f': 'geojson'
}

parcels = requests.get(parcels_url, parcels_params)
parcels_df = gp.read_file(parcels.text)

parcels_df['calc_area'] = parcels_df.area

### Iterate over p_df and calculate per parcel, append to output file
n = 0

while n < len(parcels_df):
    p_df = parcels_df.iloc[n:n+1]

    # Spatial Filter
    bbox = ','.join([str(i) for i in p_df.total_bounds])

    # Params
    farm_params = {
        'where': '1=1',
        'outFields': '*',
        'returnGeometry': True,
        'geometryType': 'esriGeometryEnvelope',
        'geometry': bbox,
        'spatialRel': 'esriSpatialRelIntersects',
        'outSR': sr,
        'f': 'geojson'
    }

    # Soils
    soils = requests.get(soils_url, farm_params)
    s_df = gp.read_file(soils.text)

    # Landuse
    landuse = requests.get(landuse_url, farm_params)

    l_df = gp.read_file(landuse.text)

    ## Overlay Data, Tidy Up
    df = gp.overlay(p_df, s_df, how='intersection')
    df = gp.overlay(df, l_df, how='intersection')

    # Remove unwanted columns
    keepers = [
        'gross_acres',
        'gis_acres',
        'calc_area',
        'pin_dashless',
        'soil_type',
        'slope',
        'landuse_type',
        'geometry'
    ]

    df.drop(columns=[c for c in df if c not in keepers], inplace=True)

    # Calculate part acres
    df['part_acres'] = df.area / df['calc_area'] * df['gross_acres']

    # Drop other columns
    df.drop(columns=['calc_area'], inplace=True)

    # LU to string
    df.loc[:, 'landuse_type'] = '0' + df['landuse_type'].astype('str')


    ## Finish up acreage
    # Aggregate
    out_cols = ['pin_dashless', 'soil_type', 'slope', 'landuse_type']

    aggs = {
        'soil_type':'first',
        'slope':'first',
        'landuse_type':'first',
        'pin_dashless':'first',
        'gross_acres':'max',
        'part_acres':'sum'
    }

    df = df.groupby(by=out_cols, as_index=False).agg(aggs).reset_index(drop=True)

    ## Check acreage sums
    qc = df.groupby('pin_dashless').agg({'gross_acres':'max', 'part_acres':'sum'}).reset_index()
    qc['diff'] = qc['gross_acres'] - round(qc['part_acres'], 4)

    outliers = qc.query('diff != 0')

    if len(outliers) > 0:
        print(f"ACREAGE MISMATCH OF {qc.loc[0,'diff']:f} ON PARCEL {qc.loc[0,'pin_dashless']}")
        warnings = True

    # Round of to 4 decimals
    df.loc[:, 'part_acres'] = round(df.loc[:, 'part_acres'], 4)

    # Drop 0s
    df = df[df.loc[:, 'part_acres'] > 0]

    # Remove extra fields
    df.drop(columns=['gross_acres'], inplace=True)

    df.to_csv(out_file, sep='\t', header=False, index=False, mode='a')

    n += 1

if warnings:
    print('Completed with warnings. Check output before importing file!')
else:
    print('Completed!')
