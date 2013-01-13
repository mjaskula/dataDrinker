import os
import simplejson as json
from brewerydb import *

OUTPUT = "output"

# setup

if not os.path.exists(OUTPUT):
    os.makedirs(OUTPUT)

BreweryDb.configure(open("apikey").readline().strip())

print "Loading styles..."

styles = BreweryDb.styles()

with open(OUTPUT + '/styles.json', 'w') as outfile:
  json.dump(styles, outfile)


# load and write the beers


