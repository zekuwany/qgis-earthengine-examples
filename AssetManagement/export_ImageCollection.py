import ee
from ee_plugin import Map


# USDA NAIP ImageCollection
collection = ee.ImageCollection('USDA/NAIP/DOQQ')

# create an roi
polys = ee.Geometry.Polygon(
        [[[41.60149951171874, 9.308978413841306],
          [41.60149951171874, 7.866935433696327],
          [42.01074023437499, 7.866935433696327],
          [42.01074023437499, 9.308978413841306]]])

# create a FeatureCollection based on the roi and center the map
centroid = polys.centroid()
lng, lat = centroid.getInfo()['coordinates']
print("lng = {}, lat = {}".format(lng, lat))
Map.setCenter(lng, lat, 12)
fc = ee.FeatureCollection(polys)

# filter the ImageCollection using the roi
naip = collection.filterBounds(polys)
naip_2015 = naip.filterDate('2015-01-01', '2015-12-31')
mosaic = naip_2015.mosaic()

# print out the number of images in the ImageCollection
count = naip_2015.size().getInfo()
print("Count: ", count)

# add the ImageCollection and the roi to the map
vis = {'bands': ['N', 'R', 'G']}
Map.addLayer(mosaic,vis)
Map.addLayer(fc)

# export the ImageCollection to Google Drive
downConfig = {'scale': 30, "maxPixels": 1.0E13, 'driveFolder': 'image'}  # scale means resolution.
img_lst = naip_2015.toList(100)

for i in range(0, count):
    image = ee.Image(img_lst.get(i))
    name = image.get('system:index').getInfo()
    # print(name)
    task = ee.batch.Export.image(image, name, downConfig)
    task.start()

