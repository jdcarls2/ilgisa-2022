## Modules
import geopandas as gp
import pandas as pd
import numpy as np
import requests

## Globals
# Spatial reference for layers
sr = "{'wkid': 3435}"

# Parcels REST service
parcels_url = 'https://maps.co.kendall.il.us/server/rest/services/Hosted/Current_Cadastral_Features/FeatureServer/1/query?'

# SSURGO Soils REST service
soils_url = 'https://maps.co.kendall.il.us/server/rest/services/Hosted/Assessor_Soils/FeatureServer/0/query?'

# Landuse REST service
landuse_url = 'https://maps.co.kendall.il.us/server/rest/services/Hosted/Assessor_Landuse/FeatureServer/0/query?'

def calc_farms(pin_list, out_path, return_df=False):
    """
    A standalone version of the farm cards notebook calculation.

        Parameters:
            pin_list (list): A list of PINs as strings, i.e., ['pin1', 'pin2', ... 'pinN']
            out_path (str): The directory and filename for the output of the calculation

        Returns:
            A dataframe of the calculated values, if `return_df` is set to True.
    """

    ## Turn list of strings into double-quoted strings
    pin_list = ["'" + pin + "'" for pin in pin_list]

    ## Parcels DF
    parcels_params = {
        'where': f"pin IN ({','.join(pin_list)})",
        'outFields': 'gross_acres, pin',
        'outSR': sr,
        'f': 'geojson'
    }

    parcels = requests.get(parcels_url, parcels_params)

    p_df = gp.read_file(parcels.text)

    p_df['calc_area'] = p_df.area

    ## Landuse and Soils
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
        'pin',
        'soil_type',
        'slope',
        'landuse_type',
        'geometry'
    ]

    df.drop(columns=[c for c in df if c not in keepers], inplace=True)

    # Calculate part acres
    df['part_acres'] = df.area / df['calc_area'] * df['gross_acres']

    # Drop other columns
    df.drop(columns=['gross_acres', 'calc_area'], inplace=True)

    # Remove PIN hyphens
    df.loc[:,'pin'] = df['pin'].str.replace('-', '')

    # LU to string
    df.loc[:, 'landuse_type'] = '0' + df['landuse_type'].astype('str')


    ## Finish up acreage
    # Aggregate
    out_cols = ['pin', 'soil_type', 'slope', 'landuse_type']

    df = df.groupby(by=out_cols, as_index=False).sum()

    # Round of to 4 decimals
    df.loc[:, 'part_acres'] = round(df.loc[:, 'part_acres'], 4)

    # Drop 0s
    df = df[df.loc[:, 'part_acres'] > 0]

    ## Add Values
    # Productivity Index
    pi_df = pd.read_csv('resources/soil_PI_2021.csv')

    # Slope and Erosion
    se_df = se_df = pd.read_csv('resources/soil_slope_erosion_2021.csv')

    # Merge In to DF
    df = df.merge(pi_df, how='left', left_on='soil_type', right_on='map_symbol', suffixes=('','_desc'))
    df = df.merge(se_df, how='left', left_on='slope', right_on='erosion_code')

    ## Adjust Values
    # Adjusted PI
    df['adj_PI'] = df['productivity_index'] * df['coeff_fav']

    # Unfavored
    df[['adj_PI']] = df[['adj_PI']].where(df['favorability'] == 'Favorable', df['productivity_index'] * df['coeff_unf'], axis=0)

    ## Equalized Assessment Values
    # Add table
    eav_df = pd.read_csv('resources/eav_2021.csv')

    # Calculate sub 82 PI EAV
    sub82 = pd.DataFrame({'avg_PI': np.arange(1,82)})

    sub82['eav'] = 199.29 - (((207.47-199.29)/5)*(82-sub82['avg_PI']))

    eav_df = eav_df.append(sub82)

    df[['adj_PI']] = df[['adj_PI']].round()

    df = df.merge(eav_df, how='left', left_on='adj_PI', right_on='avg_PI')

    # Adjust by landuse type
    df['eav_adj']=0

    df[['eav_adj']] = df[['eav']].where(df['landuse_type']=='02', 0)

    # permanent pasture
    df.loc[df['landuse_type']=='03', 'eav_adj'] = df['eav']/3

    # other farmland
    df.loc[df['landuse_type']=='04', 'eav_adj'] = df['eav']/6

    # contributory wasteland
    df.loc[df['landuse_type'] == '05', 'eav_adj'] = 33.22

    df['value'] = df['part_acres'] * df['eav_adj']

    df.to_csv(out_path, sep='\t', header=False)

    if return_df:
        return df