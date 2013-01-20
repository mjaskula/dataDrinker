import os, sys
import pprint
import simplejson as json
from brewerydb import *

OUTPUT = "output"
STYLES_FILE = 'styles.json'

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
	if fileExists(STYLES_FILE):
		print "Loading styles from file..."
		return loadFromJson(STYLES_FILE)
	else:
		print "Loading styles from BreweryDB..."
		styles = handleBreweryDbResponse(BreweryDb.styles())
		return writeToJson(styles, STYLES_FILE)


def loadBeers(styles):
	for style in styles:
		loadBeersForStyle(style)
		writeToJson(beerList, 'beers-{0}.json'.format(style['id']))
	writeToJson(beerList, 'beers-.json')
		

def loadBeersForStyle(style):
	dataFile = 'beers-{0}.raw.json'.format(style['id'])
	if fileExists(dataFile):
		print 'Loading beers for style {0} {1} from file...'.format(style['id'], encode(style['name']))
		beers = loadFromJson(dataFile)
	else:
		print 'Loading beers for style {0} {1} from BreweryDB...'.format(style['id'], encode(style['name']))
		beers = handleBreweryDbResponse(BreweryDb.beers({'styleId': style['id'], 'withBreweries': 'Y'}))  #TODO: handle pagination
		writeToJson(beers, 'beers-{0}.raw.json'.format(style['id']))
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
	copyField(beerData, 'brewery', beer, 'breweries', 0, 'name') 
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

def get(obj, *args):
	if isinstance(obj, dict):
		if len(args) > 1:
			return get(obj.get(args[0], {}), *(args[1:]))
		elif len(args) == 1:
			return obj.get(args[0], None)
		else:
			return obj
	elif isinstance(obj, list):
		if len(args) > 1:
			return get(obj[args[0]], *(args[1:]))
		elif len(args) == 1:
			return obj[args[0]]
		else:
			return obj
	else:
		return obj

def encode(value):
	return value.encode(sys.stdout.encoding, 'replace') if isinstance(value, unicode) else value

def handleBreweryDbResponse(response):
	if (response['status'] == "success"):
		return response.get('data', [])
	else:
		print response
		sys.exit(1)

def fileExists(filename):
	return os.path.isfile(OUTPUT + '/' + filename)

def writeToJson(object, filename):
	with open(OUTPUT + '/' + filename, 'w') as outfile:
	  json.dump(object, outfile)
	return object

def loadFromJson(filename):
	with open(OUTPUT + '/' + filename, 'r') as infile:
	  return json.load(infile)

if __name__ == "__main__":
    main()