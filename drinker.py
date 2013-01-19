import os, sys
import pprint
import simplejson as json
from brewerydb import *

OUTPUT = "output"


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
		

def loadBeersForStyle(style):
	print 'Loading beers for style {0} {1}...'.format(style['id'], style['name'].encode(sys.stdout.encoding, 'replace'))
	beers = handleBreweryDbResponse(BreweryDb.beers({'styleId': style['id'], 'withBreweries': 'Y'}))  #TODO: handle pagination
	for beer in beers:
		processBeer(beer)

def processBeer(beer):
	#pprint.pprint(beer)
	print '{0} - {1}'.format(beer['breweries'][0]['name'].encode(sys.stdout.encoding, 'replace'), beer['name'].encode(sys.stdout.encoding, 'replace'))


# helpers

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