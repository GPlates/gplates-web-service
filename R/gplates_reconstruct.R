library(jsonlite)
library(rgdal)

gplates_reconstruct_point <- function(lon,lat,age){
  
  url <- 'http://127.0.0.1:8000/reconstruct/reconstruct_points/'
  query <- sprintf('?points=%d,%d&time=%d&model=default',lon,lat,age)
  
  fullrequest <- sprintf(paste0(url,query))
  
  print(fullrequest)
  rawdata <- readLines(fullrequest, warn="F") 
  dat <- fromJSON(rawdata)
  
  rcoords = dat['coordinates'][[1]]
  return(rcoords)
}

gplates_reconstruct_coastlines <- function(age){

  url <- 'http://127.0.0.1:8000/reconstruct/coastlines/'
  query <- sprintf('?time=%d',age)
  
  fullrequest <- sprintf(paste0(url,query))
  print(fullrequest)
  
  r <- GET(fullrequest)
  bin <- content(r, "raw")
  writeBin(bin, "myfile.geojson")
  
  dat <- readOGR(dsn="myfile.geojson", layer="OGRGeoJSON", stringsAsFactors=FALSE)
  
  return(dat)
}

gplates_reconstruct_static_polygons <- function(age){
  
  url <- 'http://127.0.0.1:8000/reconstruct/static_polygons/'
  query <- sprintf('?time=%d',age)
  
  fullrequest <- sprintf(paste0(url,query))
  print(fullrequest)
  
  r <- GET(fullrequest)
  bin <- content(r, "raw")
  writeBin(bin, "myfile.geojson")
  
  dat <- readOGR(dsn="myfile.geojson", layer="OGRGeoJSON", stringsAsFactors=FALSE)
  
  return(dat)
}