library(magrittr)
library(rgeos)
library(rgdal) # needs gdal > 1.11.0
library(ggplot2)
library(jsonlite)
library(httr)
library(ggthemes)


#jsonfile = '/Users/Simon/Work/DataMining/Paleogeography/Heine_AJES_15_GlobalPaleoshorelines-master 2/Smith_Paleoshorelines/Smith_Timesteps_geojson/Global_Paleoshorelines_Smith_FROMAGE__70.6.geojson'
#dat <- readChar(jsonfile, file.info(jsonfile)$size)
#dat <- readLines(jsonfile, warn = FALSE) %>%
#  paste(collapse = "\n") %>%
#  fromJSON(simplifyVector = TRUE)

recon_time <- 50

full_request = sprintf('http://portal.gplates.org/service/get_coastline_polygons/?time=%d',recon_time)
r <- GET(full_request)
bin <- content(r, "raw")
writeBin(bin, "myfile.geojson")

dat <- readOGR(dsn="myfile.geojson", layer="OGRGeoJSON", stringsAsFactors=FALSE)


coords = gplates_reconstruct_point(20,25,recon_time)


#dat = readOGR(jsonfile, "OGRGeoJSON", stringsAsFactors=FALSE)
dat_map <- fortify(dat)

outline <- bbox(dat)
outline <- data.frame(xmin=-180,xmax=180,ymin=-90,ymax=90)

gg <- ggplot()
gg <- gg + geom_rect(data=outline, 
                     aes(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax), 
                     color=1, fill="white", size=0.3)
gg <- gg + geom_map(data=dat_map, map=dat_map,
                    aes(x=long, y=lat, map_id=id),
                    color="white", size=0.15, fill="#d8d8d6")
gg <- gg + geom_point(aes(x=coords[1], y=coords[2]))
gg <- gg + scale_size(name="Magnitude", trans="exp", labels=c(5:8), range=c(1, 20))
gg <- gg + coord_map("mollweide")
gg <- gg + theme_map()
gg <- gg + theme(panel.border=element_blank())
gg
