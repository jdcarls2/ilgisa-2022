var portal = Portal('https://arcgis.com')

var fs = FeatureSetByPortalItem(
    portal,
    'b063316fac7345dba4bae96eaa813b2f',
    0,
    ['Total_MW', 'StateName', 'PrimSource'],
    false
)

return GroupBy(
    fs,
    [
        'StateName',
        'PrimSource'
    ],
    [
        {
            name: 'Total_MW',
            expression: 'Total_MW',
            statistic: 'SUM'
        },
        {
            name: 'Avg_MW',
            expression: 'Total_MW',
            statistic: 'AVG'
        },
        {
            name: 'Num_Plants',
            expression: '1',
            statistic: 'COUNT'
        }
    ]
)
