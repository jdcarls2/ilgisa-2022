var portal = Portal('https://arcgis.com');

var fs = FeatureSetByPortalItem(
    portal,
    '2718975e52e24286acf8c3882b7ceb18',
    5,
    [
        'NAME',
        'HISPPOP_CY',
        'NHSPWHT_CY',
        'NHSPBLK_CY',
        'NHSPAI_CY',
        'NHSPASN_CY',
        'NHSPPI_CY',
        'NHSPOTH_CY',
        'NHSPMLT_CY',
        'TOTPOP_CY'
    ],
    false
);

fs = Filter(fs, "ID LIKE '17113%'");

var sql = `
(
    (HISPPOP_CY * (HISPPOP_CY - 1)) +
    (NHSPWHT_CY * (NHSPWHT_CY - 1)) +
    (NHSPBLK_CY * (NHSPBLK_CY - 1)) +
    (NHSPAI_CY * (NHSPAI_CY - 1)) +
    (NHSPASN_CY * (NHSPASN_CY - 1)) +
    (NHSPPI_CY * (NHSPPI_CY - 1)) +
    (NHSPOTH_CY * (NHSPOTH_CY - 1)) +
    (NHSPMLT_CY * (NHSPMLT_CY - 1)) / 1.0
)
/
(TOTPOP_CY * (TOTPOP_CY - 1) * 1.1 / 1.1)
`;

return GroupBy(
    fs,
    'NAME',
    [
        {name: 'simpsonDI', expression: sql, statistic: 'SUM'}
    ]
);
