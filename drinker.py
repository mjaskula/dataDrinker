import os, sys
import pprint
import simplejson as json
from brewerydb import *

OUTPUT = "output"
STYLES_FILE = 'styles.json'

counts = {'total': 0, 'using': 0, 'srm': 0, 'ibu': 0, 'og': 0, 'abv': 0}

def main():
	ensureOutputDir()
	configure()
	loadBeers(loadStyles())
	pprint.pprint(counts)


def ensureOutputDir():
	if not os.path.exists(OUTPUT):
	    os.makedirs(OUTPUT)


def configure():
	BreweryDb.configure(open("apikey").readline().strip())


def loadStyles():
	if fileExists(STYLES_FILE):
		print "Loading styles from file..."
		styles = loadFromJson(STYLES_FILE)
	else:
		print "Loading styles from BreweryDB..."
		styles = handleBreweryDbResponse(BreweryDb.styles()).get('data', [])
		writeToJson(styles, STYLES_FILE)
	counts['styles'] = len(styles)
	return styles


def loadBeers(styles):
	fullList = []
	for style in styles:
		counts[style['name']] = {'total': 0}
		beers = loadBeersForStyle(style)
		counts[style['name']]['using'] = len(beers)
		writeToJson(beers, 'beers-{0}.json'.format(style['id']))
		fullList.extend(beers)
	writeToJson(fullList, 'beers.json')
		

def loadBeersForStyle(style):
	beersForStyle = []

	currentPage = 1
	numPages = 30 # a guess at max page numbers
	while currentPage <= numPages:
		beers, numPages = loadStylePage(style, currentPage, numPages)
		for beer in beers:
			processedBeer = processBeer(beer)
			if processedBeer is not None:
				print '  Loaded: {0} - {1}'.format(encode(processedBeer['brewery']), encode(processedBeer['name']))
				counts['using'] += 1
				beersForStyle.append(processedBeer)
		currentPage += 1
	return beersForStyle

def loadStylePage(style, page, numPages):
	dataFile = 'beers-{0}-{1}.raw.json'.format(style['id'], page)
	if fileExists(dataFile):
		print 'Loading beers for style {0} {1} page {2} from file...'.format(style['id'], encode(style['name']), page)
		beers = loadFromJson(dataFile)
	else:
		beers = []
		# beers, numPages = loadBeersFromBreweryDb(style, page)
	counts[style['name']]['total'] = counts[style['name']]['total'] + len(beers)
	return (beers, numPages)

def loadBeersFromBreweryDb(style, page):
		print 'Loading beers for style {0} {1} page {2} from BreweryDB...'.format(style['id'], encode(style['name']), page)
		response = handleBreweryDbResponse(BreweryDb.beers({'styleId': style['id'], 'withBreweries': 'Y', 'p': page}))
		numPages = response.get('numberOfPages')
		beers = response.get('data', [])
		writeToJson(beers, 'beers-{0}-{1}.raw.json'.format(style['id'], page))
		return (beers, numPages)

def processBeer(beer):
	# pprint.pprint(beer)
	beerData = gatherData(beer)
	counts['total'] += 1
	if ('abv' in beerData and 'ibu' in beerData and 'og' in beerData and 'srm' in beerData):
		return beerData
	elif ('ibu' in beerData and 'og' in beerData and 'srm' in beerData):
		counts['abv'] += 1
		return None
	elif ('abv' in beerData and 'og' in beerData and 'srm' in beerData):
		counts['ibu'] += 1
		return None
	elif ('abv' in beerData and 'ibu' in beerData and 'srm' in beerData):
		counts['og'] += 1
		return None
	elif ('abv' in beerData and 'ibu' in beerData and 'og' in beerData):
		counts['srm'] += 1
		return None
	else:
		return None

def gatherData(beer):
	beerData = {}
	copyField(beerData, 'brewery',   beer, 'breweries', 0, 'name') 
	copyField(beerData, 'breweryId', beer, 'breweries', 0, 'id') 
	copyField(beerData, 'name',      beer, 'name') 
	copyField(beerData, 'id',        beer, 'id') 
	copyField(beerData, 'style',     beer, 'style', 'name')
	copyField(beerData, 'styleId',   beer, 'styleId')
	copyField(beerData, 'abv',       beer, 'abv') 
	copyField(beerData, 'ibu',       beer, 'ibu')
	copyField(beerData, 'og',        beer, 'originalGravity')
	copyField(beerData, 'srm',       beer, 'srm', 'name')
	return beerData

def copyField(dest, destFieldName, src, *srcFieldNames):
	value = get(src, *srcFieldNames)
	if value is not None:
		# print '    {0}: {1}'.format(destFieldName, encode(value))
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
		return response
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