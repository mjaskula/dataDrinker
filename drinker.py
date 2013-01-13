import os,json
from brewerydb import *

OUTPUT = "output"

if not os.path.exists(OUTPUT):
    os.makedirs(OUTPUT)

BreweryDb.configure(open("apikey").readline().strip())


styles = json.loads(BreweryDb.styles())

with open(OUTPUT + '/styles.json', 'w') as outfile:
  json.dump(styles, outfile)



