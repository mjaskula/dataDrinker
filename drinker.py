import os, sys
import pprint
import simplejson as json
from brewerydb import *

OUTPUT = "output"

beerList = [] #TODO: make functional

def main():
	ensureOutputDir()
	configure()
	loadBeers(loadStyles())


def ensureOutputDir():
	if not os.path.exists(OUTPUT):
	    os.makedirs(OUTPUT)


def configure():
	BreweryDb.configure(open("apikey").readline().strip())


def loadStyles():
	print "Loading styles..."
	styles = handleBreweryDbResponse(BreweryDb.styles())
	return writeToJson(styles, 'styles.json')


def loadBeers(styles):
	#for style in styles:
		loadBeersForStyle(styles[0])
		writeToJson(beerList, 'beers.json')
		

def loadBeersForStyle(style):
	print 'Loading beers for style {0} {1}...'.format(style['id'], encode(style['name']))
	beers = handleBreweryDbResponse(BreweryDb.beers({'styleId': style['id'], 'withBreweries': 'Y'}))  #TODO: handle pagination
	writeToJson(beers, 'beers-{0}.json'.format(style['id']))
	for beer in beers:
		processBeer(beer)

def processBeer(beer):
	# pprint.pprint(beer)
	print 'Loading: {0} - {1}'.format(encode(beer['breweries'][0]['name']), encode(beer['name']))
	beerData = gatherData(beer)
	if beerData is not None: 
		beerList.append(beerData)

def gatherData(beer):
	beerData = {}
	copyField(beerData, 'brewery', beer['breweries'][0], 'name') 
	copyField(beerData, 'name',    beer, 'name') 
	copyField(beerData, 'style',   beer, 'style', 'name')
	copyField(beerData, 'styleId', beer, 'styleId')
	copyField(beerData, 'abv',     beer, 'abv') 
	copyField(beerData, 'ibu',     beer, 'ibu')
	copyField(beerData, 'og',      beer, 'originalGravity')
	copyField(beerData, 'srm',     beer, 'srm', 'name') 
	return beerData

def copyField(dest, destFieldName, src, *srcFieldNames):
	value = get(src, *srcFieldNames)
	if value is not None:
		print '  {0}: {1}'.format(destFieldName, encode(value))
		dest[destFieldName] = value

# helpers

def get(dict, *args):
	if len(args) > 1:
		return get(dict.get(args[0], {}), *(args[1:]))
	elif len(args) == 1:
		return dict.get(args[0], None)
	else:
		return dict

def encode(value):
	return value.encode(sys.stdout.encoding, 'replace') if isinstance(value, unicode) else value

def handleBreweryDbResponse(response):
	if (response['status'] == "success"):
		return response['data']
	else:
		print response
		sys.exit(1)

def writeToJson(object, filename):
	with open(OUTPUT + '/' + filename, 'w') as outfile:
	  json.dump(object, outfile)
	return object

if __name__ == "__main__":
    main()