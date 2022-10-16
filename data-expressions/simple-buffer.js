var portal = Portal('https://www.arcgis.com/');

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
        {name: 'plant_name', type: 'esriFieldTypeString'},
        {name: 'plant_code', type: 'esriFieldTypeInteger'}
    ],
  geometryType: 'esriGeometryPolygon',
  features: []
};

for (var p in plants) {
    
    var fivemile = Buffer(p, 5, 'miles')
    
    Push(
        out_dict['features'],
        {
            attributes: {
                plant_name: p['Plant_Name'],
                plant_code: p['Plant_Code']
            },
            geometry: fivemile
        }
    );
};

return FeatureSet(Text(out_dict));
