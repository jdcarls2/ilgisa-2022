var n = Now()
var thehour = Hour(Now())
var theminute = Minute(Now())

if (thehour > 12){
    thehour -= 12
}

var out_dict = {
    fields: [
        {name: 'thehour', type: 'esriFieldTypeInteger'},
        {name: 'theminute', type: 'esriFieldTypeInteger'},
        {name: 'hourdegrees', type: 'esriFieldTypeDouble'},
        {name: 'minutedegrees', type: 'esriFieldTypeDouble'},
        {name: 'ampm', type: 'esriFieldTypeString'}],
    geometryType: '',
    features: [
        {attributes: {
            thehour: thehour,
            theminute: theminute,
            hourdegrees: thehour * 30 + (5 / theminute),
            minutedegrees: theminute * 6,
            ampm: Iif(Hour(Now()) > 12, 'PM', 'AM')
        }}]
}

return FeatureSet(Text(out_dict))
