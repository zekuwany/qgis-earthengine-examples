from functools import reduce

import ee

ee.Initialize();

# samples = ee.FeatureCollection("projects/ee-zekuwany/assets/Park_Catchment");
samples = ee.FeatureCollection(ee.Geometry.MultiPoint([[41.60149951171874, 9.308978413841306],
          [41.60149951171874, 7.866935433696327],
          [42.01074023437499, 7.866935433696327],
          [42.01074023437499, 9.308978413841306]]));


# mask out cloud covered regions
def maskBadData(image):
    valid = image.select('cfmask').eq(0);
    clean = image.mask(valid);

    return clean;


# funciton using reducer to get the mean
def getMeans(image):
    return image.set(image.reduceRegion(ee.Reducer.mean(), samples, 30, maxPixels=100000, bestEffort=True))


collections = [
    ee.ImageCollection("LANDSAT/LT5_SR").select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7']),
    ee.ImageCollection("LANDSAT/LE7_SR").select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7']),
    ee.ImageCollection("LANDSAT/LE7_SR").select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
                                                ['B1', 'B2', 'B3', 'B4', 'B5', 'B7'])
]

# merge collections
images = reduce((lambda c1, c2: c1.merge(c2)), collections)

images = ee.ImageCollection(images)

# get means
means = images.filterBounds(samples).map(maskBadData).map(getMeans)

# hack to make sure the output has required bands
empty = images.first().set({"B1": 0, "B2": 0, "B3": 0, "B4": 0, "B5": 0, "B7": 0});
means = ee.FeatureCollection([empty]).merge(means).filter(ee.Filter.neq('B1', None))

# print the output  to debug before exporting
results = means.select([".*"], None, False).getInfo()
print(results['features'][0]['properties']['B1'])

exportname = 'segID_0';
# task=ee.batch.Export.table.toDrive(LC8_extract.select([".*"], None, False), description=exportname,fileFormat='csv');
# task.start();
# ee.batch.Task.list();
# print(exportname);
