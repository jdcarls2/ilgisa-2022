var portal = Portal('https://www.arcgis.com/');

var tracts = FeatureSetByPortalItem(
    portal,
    '30338679df5542378ec86997ca447576',
    2,
    ['B01001_001E'],
    false
);

var plants = FeatureSetByPortalItem(
    portal,
    'b063316fac7345dba4bae96eaa813b2f',
    0,
    ['Plant_Name', 'Plant_Code'],
    true
);

plants = Filter(
    plants,
    "StateName = 'Illinois' AND PrimSource = 'coal'")

var out_dict = {
    fields: [
        {name: 'population', type: 'esriFieldTypeInteger'},
        {name: 'plant_name', type: 'esriFieldTypeString'},
        {name: 'plant_code', type: 'esriFieldTypeInteger'}
    ],
  geometryType: 'esriGeometryPolygon',
  features: []
};

for (var p in plants) {
    
    var fivemile = Buffer(p, 5, 'miles')
    var nearby_pop = Intersects(fivemile, tracts)
    
    Push(
        out_dict['features'],
        {
            attributes: {
                population: Sum(nearby_pop, 'B01001_001E'),
                plant_name: p['Plant_Name'],
                plant_code: p['Plant_Code']
            },
            geometry: fivemile
        }
    );
};

return FeatureSet(Text(out_dict));