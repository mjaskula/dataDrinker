import os, sys
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
	return writeToJson(BreweryDb.styles(), 'styles.json')


def loadBeers(styles):
	for style in styles['data']:
		processBeersForStyle(style)
		

def processBeersForStyle(style):
	print 'Loading beers for style {0} {1}...'.format(style['id'], style['name'].encode(sys.stdout.encoding, 'replace'))
	print BreweryDb.beers({'styleId': style['id']})
	sys.exit(0)

def writeToJson(object, filename):
	with open(OUTPUT + '/' + filename, 'w') as outfile:
	  json.dump(object, outfile)
	return object

if __name__ == "__main__":
    main()