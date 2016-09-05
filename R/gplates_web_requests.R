library(jsonlite)
library(rgdal)
library(magrittr)

#file = '/Users/Simon/Work/DataMining/Paleogeography/Heine_AJES_15_GlobalPaleoshorelines-master 2/Smith_Paleoshorelines/Smith_Timesteps_geojson/Global_Paleoshorelines_Smith_FROMAGE__70.6.geojson'

#geojson <- readLines(file, warn = FALSE) %>%
#  paste(collapse = "\n") %>%
#  fromJSON(simplifyVector = FALSE)


#gas <- readOGR(dsn = file, layer = "OGRGeoJSON")
#plot(gas)

url = 'http://portal.gplates.org/service/reconstruct_feature_collection/'

jsonfile = '/Users/Simon/Work/DataMining/Paleogeography/Heine_AJES_15_GlobalPaleoshorelines-master 2/Smith_Paleoshorelines/Smith_Timesteps_geojson/Global_Paleoshorelines_Smith_FROMAGE__70.6.geojson'
#dat <- readChar(jsonfile, file.info(jsonfile)$size)
dat <- readLines( , warn = FALSE) %>%
  paste(collapse = "\n") %>%
  fromJSON(simplifyVector = TRUE)

fullrequest = sprintf('%s?feature_collection=%s&geologicage=%d&model=default',url,dat,120)

print(fullrequest)

rawdata <- readLines(fullrequest, warn="F") 

